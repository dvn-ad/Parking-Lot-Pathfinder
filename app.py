from flask import Flask, render_template, request
from program import load_floors, find_best_slot

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

    floors = load_floors('maps')

    algos = []
    if algo == 'all':
        algos = ['a_star', 'dijkstra', 'bfs', 'greedy_bfs']
    else:
        algos = [algo]

    results = []
    for a in algos:
        result = find_best_slot(floors, a, ptype, desired_floor, w_lobby, w_car)
        if result:
            best_slot, path_car, path_lobby, score = result
            results.append({
                'algo': ALGO_CHOICES.get(a, a),
                'best_slot': best_slot,
                'path_car': path_car,
                'path_lobby': path_lobby,
                'score': score,
            })
        else:
            results.append({
                'algo': ALGO_CHOICES.get(a, a),
                'best_slot': None,
            })

    return render_template('result.html', results=results, show_path=show_path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
