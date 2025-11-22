from flask import Flask, render_template, request
from program import load_floors, find_best_slot
import time
import os

app = Flask(__name__, static_folder="static")

ALGO_CHOICES = {
    'a_star': 'A*',
    'dijkstra': 'Dijkstra',
    'bfs': 'BFS',
    'greedy_bfs': 'Greedy BFS',
    'all': 'Run all'
}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', algos=ALGO_CHOICES)


@app.route('/find', methods=['POST'])
def find():
    try:
        algo = request.form.get('algorithm', 'a_star')
        ptype = request.form.get('parking_type', 'P')
        desired_floor_str = request.form.get('desired_floor', '').strip()
        desired_floor = int(desired_floor_str) if desired_floor_str != '' else None
        pref = request.form.get('preference', 'lobby')
        if pref == 'lobby':
            w_lobby, w_car = 2, 1
        else:
            w_lobby, w_car = 1, 2
        show_path = request.form.get('show_path') == 'on'

        base_dir = os.path.dirname(os.path.abspath(__file__))
        maps_dir = os.path.join(base_dir, 'maps')
        floors = load_floors(maps_dir)

        algos = []
        if algo == 'all':
            algos = ['a_star', 'dijkstra', 'bfs', 'greedy_bfs']
        else:
            algos = [algo]

        results = []
        for a in algos:
            start_time = time.time()
            result = find_best_slot(floors, a, ptype, desired_floor, w_lobby, w_car)
            end_time = time.time()
            exec_time = end_time - start_time
            exec_time_str = f"{exec_time:.4f}s"

            if result:
                best_slot, path_car, path_lobby, score = result
                results.append({
                    'algo': ALGO_CHOICES.get(a, a),
                    'best_slot': best_slot,
                    'path_car': path_car,
                    'path_lobby': path_lobby,
                    'score': score,
                    'exec_time': exec_time,
                    'exec_time_str': exec_time_str,
                })
            else:
                results.append({
                    'algo': ALGO_CHOICES.get(a, a),
                    'best_slot': None,
                    'exec_time': exec_time,
                    'exec_time_str': exec_time_str,
                })

        # Build overlays for map visualization: for each result, create dict of overlay arrows
        def path_to_overlays(path, tag):
            # returns dict[(z,y,x)] = {'char': arrow, 'tag': tag}
            overlays = {}
            if not path:
                return overlays
            for i in range(len(path)-1):
                z1,y1,x1 = path[i]
                z2,y2,x2 = path[i+1]
                if z1 == z2:
                    if y2 == y1 and x2 == x1+1:
                        arrow = '→'
                    elif y2 == y1 and x2 == x1-1:
                        arrow = '←'
                    elif y2 == y1+1 and x2 == x1:
                        arrow = '↓'
                    elif y2 == y1-1 and x2 == x1:
                        arrow = '↑'
                    else:
                        arrow = '·'
                    overlays[(z1,y1,x1)] = {'char': arrow, 'tag': tag}
                else:
                    # vertical move: mark at source with up/down arrow
                    if z2 == z1+1:
                        overlays[(z1,y1,x1)] = {'char': '⇑', 'tag': tag}
                    else:
                        overlays[(z1,y1,x1)] = {'char': '⇓', 'tag': tag}
            return overlays

        results_with_overlays = []
        for r in results:
            overlays = {}
            if r.get('path_car'):
                overlays.update(path_to_overlays(r['path_car'], 'car'))
            if r.get('path_lobby'):
                # Instead of arrows for lobby path, mark the path cells for highlighting.
                for k,v in path_to_overlays(r['path_lobby'], 'lobby').items():
                    # If a car arrow already exists at this cell, keep the car arrow
                    # and add a highlight flag so both visuals appear (arrow + blue background).
                    if k in overlays:
                        overlays[k]['highlight'] = True
                    else:
                        overlays[k] = {'char': None, 'tag': 'lobby', 'highlight': True}

            # Determine which floor indices are used by overlays (and include slot floor as fallback)
            floors_used = sorted({coord[0] for coord in overlays.keys()})
            if not floors_used and r.get('best_slot'):
                floors_used = [r['best_slot'][0]]

            results_with_overlays.append({'result': r, 'overlays': overlays, 'floors_used': floors_used})

        # If the user requested all algorithms, sort results by execution time (fastest first)
        if algo == 'all' and len(results_with_overlays) > 1:
            results_with_overlays.sort(key=lambda it: (it['result'].get('exec_time') if it['result'].get('exec_time') is not None else float('inf')))

        # pass Python's enumerate into Jinja context for indexing floors
        return render_template('result.html', results=results_with_overlays, show_path=show_path, floors=floors, enumerate=enumerate)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
