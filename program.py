import csv
import math
import heapq
import os
import time
from collections import deque

# ---------- GRID UTILS ----------
def read_csv_grid(filename):
    with open(filename, "r") as f:
        reader = csv.reader(f)
        return [row for row in reader]

def load_floors(folder):
    floors = []
    csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]

    def get_sort_key(filename):
        try:
            name_part = filename.split('.')[0]
            return int("".join(filter(str.isdigit, name_part)))
        except ValueError:
            return 0

    sorted_files = sorted(csv_files, key=get_sort_key)
    for file in sorted_files:
        floors.append(read_csv_grid(os.path.join(folder, file)))
    return floors

# ---------- PATHFINDING UTILS ----------
def heuristic(a, b):
    # Manhattan distance for 3D grid
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])

def heuristic_blind(pos, desired_floor):
    if desired_floor is None:
        return 0
    # Heuristic is just vertical distance. 
    # We can weight it to encourage moving to that floor.
    return abs(pos[0] - desired_floor) * 10

def can_move(floors, z, y, x, dy, dx, is_pedestrian=False):
    cell = floors[z][y][x]
    
    # Pedestrians can move freely from any walkable tile (except walls)
    # They ignore one-way signs.
    if is_pedestrian:
        return True

    # Passable source symbols (cells that may allow exiting horizontally).
    # Only '.' (road), the car start 'C', lobby 'O' (so lobby can start a search),
    # and vertical markers 'N'/'T' (and arrows) allow exits. Entrances 'E'/'e'
    # allow exiting to the floor.
    if cell in [".", "C", "O", "N", "T", "E", "e"]:
        return True
    if cell == ">": return (dy, dx) == (0, 1)
    if cell == "<": return (dy, dx) == (0, -1)
    if cell == "^": return (dy, dx) == (-1, 0)
    if cell in ["v", "V"]: return (dy, dx) == (1, 0)
    return False

def get_neighbors(pos, floors, goal=None, is_pedestrian=False):
    z, y, x = pos
    neighbors = []
    height, width = len(floors[z]), len(floors[z][0])
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    for dy, dx in directions:
        ny, nx = y + dy, x + dx
        if 0 <= ny < height and 0 <= nx < width:
            dest = floors[z][ny][nx]
            # skip walls
            if dest == "#":
                continue
            # Horizontal movement rules: ONLY allow entering road tiles ('.' or directional arrows)
            # or the exact goal cell. Do NOT treat parking slots, lobbies, or entrances as roads.
            road_tiles = {".", ">", "<", "^", "v", "V", "C", "N", "T"}
            
            # Check if destination is the goal
            is_target = False
            if isinstance(goal, tuple) and (z, ny, nx) == goal:
                is_target = True
            elif isinstance(goal, str) and dest == goal:
                is_target = True
                
            if not is_target and dest not in road_tiles:
                # destination is not a road and not the goal -> cannot move into it
                continue
            # check source allows exiting in this direction
            allowed = can_move(floors, z, y, x, dy, dx, is_pedestrian)
            
            # Allow turning into a parking slot from a directional road
            if not allowed and not is_pedestrian and is_target:
                cur_cell = floors[z][y][x]
                if cur_cell == "^" and dy != 1: allowed = True      # Allow except backward (South)
                elif cur_cell in ["v", "V"] and dy != -1: allowed = True # Allow except backward (North)
                elif cur_cell == "<" and dx != 1: allowed = True    # Allow except backward (East)
                elif cur_cell == ">" and dx != -1: allowed = True   # Allow except backward (West)

            if allowed:
                neighbors.append((z, ny, nx))
    # Vertical movement rules using new symbols:
    # 'N' = naik (up): can move up to floor z+1 if that cell is 'E' (entrance on upper floor)
    # 'T' = turun (down): can move down to floor z-1 if that cell is 'e' (entrance on lower floor)
    # 'E' on an upper floor can move down to a matching 'N' below
    # 'e' on a lower floor can move up to a matching 'T' above
    cur = floors[z][y][x]
    # Up from 'N' -> 'E'
    if cur == 'N' and z + 1 < len(floors) and floors[z+1][y][x] == 'E':
        neighbors.append((z+1, y, x))

        neighbors.append((z+1, y, x))
    # Down from 'T' -> 'e'
    if cur == 'T' and z - 1 >= 0 and floors[z-1][y][x] == 'e':
        neighbors.append((z-1, y, x))
    # Note: Entrance cells 'E' and 'e' do NOT create vertical moves to 'N'/'T'.
    # Vertical movement is only allowed from 'N' -> 'E' (up) and 'T' -> 'e' (down).
    return neighbors

# ---------- PATHFINDING ALGORITHMS ----------
def pathfind(floors, start, goal, algo="a_star", is_pedestrian=False, desired_floor=None):
    if algo == "bfs":
        return bfs(floors, start, goal, is_pedestrian, desired_floor)
    elif algo == "dijkstra":
        return dijkstra(floors, start, goal, is_pedestrian, desired_floor)
    # *** DIUBAH: Sekarang memanggil "greedy_bfs" ***
    elif algo == "greedy_bfs": 
        return greedy_bfs(floors, start, goal, is_pedestrian, desired_floor)
    else:
        return a_star(floors, start, goal, is_pedestrian, desired_floor)

def a_star(floors, start, goal, is_pedestrian=False, desired_floor=None):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    visited_order = []

    # Check if goal is coordinate or symbol
    is_blind = isinstance(goal, str)

    while open_set:
        _, current = heapq.heappop(open_set)
        visited_order.append(current)
        
        found = False
        if is_blind:
            z, y, x = current
            if floors[z][y][x] == goal:
                # STRICT CHECK: Only accept goal if on desired_floor
                if desired_floor is None or z == desired_floor:
                    found = True
        else:
            if current == goal:
                found = True
        
        if found:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], visited_order
            
        # Pass goal to get_neighbors even if blind, so it can check if neighbor is the target symbol
        for neighbor in get_neighbors(current, floors, goal, is_pedestrian):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                
                if is_blind:
                    h = heuristic_blind(neighbor, desired_floor)
                else:
                    h = heuristic(neighbor, goal)
                    
                f_score = tentative_g + h
                heapq.heappush(open_set, (f_score, neighbor))
    return None, visited_order

def dijkstra(floors, start, goal, is_pedestrian=False, desired_floor=None):
    pq = [(0, start)]
    came_from = {}
    dist = {start: 0}
    visited_order = []
    
    # Check if goal is coordinate or symbol
    is_blind = isinstance(goal, str)
    
    while pq:
        cost, current = heapq.heappop(pq)
        visited_order.append(current)
        
        found = False
        if is_blind:
            z, y, x = current
            if floors[z][y][x] == goal:
                # STRICT CHECK: Only accept goal if on desired_floor
                if desired_floor is None or z == desired_floor:
                    found = True
        else:
            if current == goal:
                found = True
                
        if found:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], visited_order
            
        # Pass goal to get_neighbors even if blind
        for neighbor in get_neighbors(current, floors, goal, is_pedestrian):
            new_cost = cost + 1
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(pq, (new_cost, neighbor))
    return None, visited_order

def bfs(floors, start, goal, is_pedestrian=False, desired_floor=None):
    queue = deque([start])
    came_from = {start: None}
    visited_order = []
    
    # Check if goal is coordinate or symbol
    is_blind = isinstance(goal, str)
    
    while queue:
        current = queue.popleft()
        visited_order.append(current)
        
        found = False
        if is_blind:
            z, y, x = current
            if floors[z][y][x] == goal:
                # STRICT CHECK: Only accept goal if on desired_floor
                if desired_floor is None or z == desired_floor:
                    found = True
        else:
            if current == goal:
                found = True
                
        if found:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return path[::-1], visited_order
            
        # Pass goal to get_neighbors even if blind
        for neighbor in get_neighbors(current, floors, goal, is_pedestrian):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)
    return None, visited_order

# *** DIUBAH: Menggantikan DFS dengan Greedy BFS ***
def greedy_bfs(floors, start, goal, is_pedestrian=False, desired_floor=None):
    open_set = []
    
    # Check if goal is coordinate or symbol
    is_blind = isinstance(goal, str)
    
    if is_blind:
        h = heuristic_blind(start, desired_floor)
    else:
        h = heuristic(start, goal)
        
    heapq.heappush(open_set, (h, start))
    came_from = {start: None} 
    visited_order = []

    while open_set:
        _, current = heapq.heappop(open_set)
        visited_order.append(current)

        found = False
        if is_blind:
            z, y, x = current
            if floors[z][y][x] == goal:
                # STRICT CHECK: Only accept goal if on desired_floor
                if desired_floor is None or z == desired_floor:
                    found = True
        else:
            if current == goal:
                found = True

        if found:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return path[::-1], visited_order

        # Pass goal to get_neighbors even if blind
        for neighbor in get_neighbors(current, floors, goal, is_pedestrian):
            if neighbor not in came_from:
                came_from[neighbor] = current
                
                if is_blind:
                    priority = heuristic_blind(neighbor, desired_floor)
                else:
                    priority = heuristic(neighbor, goal)
                    
                heapq.heappush(open_set, (priority, neighbor))
    
    return None, visited_order

# ---------- SLOT SEARCH ----------
def find_positions(floors, symbol):
    positions = []
    for z, floor in enumerate(floors):
        for y, row in enumerate(floor):
            for x, val in enumerate(row):
                if val == symbol:
                    positions.append((z, y, x))
    return positions

def find_best_slot(floors, algo="a_star", target_symbol="P", desired_floor=None, w_lobby=2, w_car=1):
    cars = find_positions(floors, "C")
    target_lower = target_symbol.lower()
    slots = find_positions(floors, target_lower)
    lobbies = find_positions(floors, "O")

    if not cars or not slots:
        print(f"[!] Missing required symbols (C or {target_lower}).")
        return None

    car = cars[0]
    best_slot = None
    best_path_car = None
    best_path_lobby = None
    best_score = float("inf")
    best_visited_car = []
    best_visited_lobby = []

    for slot in slots:
        z, y, x = slot
        
        # 1. Calculate Car -> Slot path
        path_car, visited_car = pathfind(floors, car, slot, algo, is_pedestrian=False)
        if not path_car:
            continue

        # 2. Calculate Lobby -> Slot path (nearest lobby on same floor)
        lobbies_on_floor = [l for l in lobbies if l[0] == z]
        
        path_lobby = None
        visited_lobby = []
        min_lobby_dist = float("inf")
        
        if not lobbies_on_floor:
            lobby_dist = 9999
        else:
            for lobby in lobbies_on_floor:
                p_l, v_l = pathfind(floors, lobby, slot, algo, is_pedestrian=True)
                if p_l:
                    dist = len(p_l)
                    if dist < min_lobby_dist:
                        min_lobby_dist = dist
                        path_lobby = p_l
                        visited_lobby = v_l
            
            if path_lobby is None:
                lobby_dist = 9999
            else:
                lobby_dist = min_lobby_dist

        # 3. Calculate Score
        # score = jarak(Car->Slot) * w_car + jarak(Lobby->Slot) * w_lobby + (|floor - desired_floor| * 1000)
        car_dist = len(path_car)
        floor_penalty = 0
        if desired_floor is not None:
            floor_penalty = abs(z - desired_floor) * 1000
            
        score = (car_dist * w_car) + (lobby_dist * w_lobby) + floor_penalty
        
        if score < best_score:
            best_score = score
            best_slot = slot
            best_path_car = path_car
            best_path_lobby = path_lobby
            best_visited_car = visited_car
            best_visited_lobby = visited_lobby

    if not best_slot:
        print("[!] No valid parking slot found.")
        return None

    return best_slot, best_path_car, best_path_lobby, best_score, best_visited_car, best_visited_lobby

# ---------- MAIN ----------
if __name__ == "__main__":
    floors = load_floors("maps")

    print("[1] A*")
    print("[2] Dijkstra")
    print("[3] BFS")
    print("[4] Greedy BFS") 
    print("[5] Run all")
    inp = input("Choose algorithm: ").strip()

    print("\nParking Type:")
    print("[1] Normal (P)")
    print("[2] Ladies (L)")
    print("[3] Disability (D)")
    p_type = input("Choose type: ").strip()
    target_symbol = {"1": "P", "2": "L", "3": "D"}.get(p_type, "P")

    print("\nEnter desired floor number (0 = ground):")
    try:
        desired_floor = int(input("Desired floor: ").strip())
    except ValueError:
        desired_floor = None

    show_path = input("\nShow paths? (y/n): ").strip().lower() == "y"

    algos = []
    if inp == "5":
        algos = ["a_star", "dijkstra", "bfs", "greedy_bfs"] 
    elif inp == "1":
        algos = ["a_star"]
    elif inp == "2":
        algos = ["dijkstra"]
    elif inp == "3":
        algos = ["bfs"]
    elif inp == "4":
        algos = ["greedy_bfs"] 
    else:
        print("Invalid choice.")
        exit()

    print("\nPrefer parking closer to:")
    print("[1] Lobby")
    print("[2] Car Position")
    pref = input("Choose preference: ").strip()
    if pref == "1":
        w_lobby, w_car = 2, 1
    else:
        w_lobby, w_car = 1, 2

    for algo in algos:
        algo_name = algo.replace("_", " ").upper()
        print(f"\n=== Running {algo_name} ===")
        
        start_time = time.time()
        result = find_best_slot(floors, algo, target_symbol, desired_floor, w_lobby, w_car)
        end_time = time.time()
        exec_time = end_time - start_time

        if result:
            best_slot, path_car, path_lobby, score, visited_car, visited_lobby = result
            print(f"Best slot: Floor {best_slot[0]}, Pos ({best_slot[1]+1}, {best_slot[2]+1})")
            print(f"Total combined cost (Car + Lobby + Floor offset): {score}")
            print(f"Execution Time: {exec_time:.4f} seconds")

            if show_path:
                print("\nPath from Car → Slot:")
                for step in path_car:
                    print(f"  Floor {step[0]} → ({step[1]+1}, {step[2]+1})")

                print("\nPath from Nearest Lobby → Slot:")
                for step in path_lobby:
                    print(f"  Floor {step[0]} → ({step[1]+1}, {step[2]+1})")
        else:
            print("No valid slot found!")
            print(f"Execution Time: {exec_time:.4f} seconds")

