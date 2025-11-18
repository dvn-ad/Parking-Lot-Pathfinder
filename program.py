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

def can_move(floors, z, y, x, dy, dx):
    cell = floors[z][y][x]
    # Passable source symbols (cells that may allow exiting horizontally).
    # Only '.' (road), the car start 'C', lobby 'O' (so lobby can start a search),
    # and vertical markers 'N'/'T' (and arrows) allow exits. Entrances 'E'/'e'
    # and parking slots are NOT horizontal sources for movement.
    if cell in [".", "C", "O", "N", "T"]:
        return True
    if cell == ">": return (dy, dx) == (0, 1)
    if cell == "<": return (dy, dx) == (0, -1)
    if cell == "^": return (dy, dx) == (-1, 0)
    if cell in ["v", "V"]: return (dy, dx) == (1, 0)
    return False

def get_neighbors(pos, floors, goal=None):
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
            road_tiles = {".", ">", "<", "^", "v", "V", "C"}
            if (z, ny, nx) != goal and dest not in road_tiles:
                # destination is not a road and not the goal -> cannot move into it
                continue
            # check source allows exiting in this direction
            if can_move(floors, z, y, x, dy, dx):
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
    # Down from 'T' -> 'e'
    if cur == 'T' and z - 1 >= 0 and floors[z-1][y][x] == 'e':
        neighbors.append((z-1, y, x))
    # Note: Entrance cells 'E' and 'e' do NOT create vertical moves to 'N'/'T'.
    # Vertical movement is only allowed from 'N' -> 'E' (up) and 'T' -> 'e' (down).
    return neighbors

# ---------- PATHFINDING ALGORITHMS ----------
def pathfind(floors, start, goal, algo="a_star"):
    if algo == "bfs":
        return bfs(floors, start, goal)
    elif algo == "dijkstra":
        return dijkstra(floors, start, goal)
    # *** DIUBAH: Sekarang memanggil "greedy_bfs" ***
    elif algo == "greedy_bfs": 
        return greedy_bfs(floors, start, goal)
    else:
        return a_star(floors, start, goal)

def a_star(floors, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        for neighbor in get_neighbors(current, floors, goal):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
    return None

def dijkstra(floors, start, goal):
    pq = [(0, start)]
    came_from = {}
    dist = {start: 0}
    while pq:
        cost, current = heapq.heappop(pq)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        for neighbor in get_neighbors(current, floors, goal):
            new_cost = cost + 1
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(pq, (new_cost, neighbor))
    return None

def bfs(floors, start, goal):
    queue = deque([start])
    came_from = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for neighbor in get_neighbors(current, floors, goal):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)
    return None

# *** DIUBAH: Menggantikan DFS dengan Greedy BFS ***
def greedy_bfs(floors, start, goal):
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), start))
    came_from = {start: None} 

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        for neighbor in get_neighbors(current, floors, goal):
            if neighbor not in came_from:
                came_from[neighbor] = current
                priority = heuristic(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor))
    
    return None

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
    # target_symbol is provided as uppercase ('P','L','D'); available slots are lowercase
    target_lower = target_symbol.lower()
    slots = find_positions(floors, target_lower)

    if not cars or not slots:
        print(f"[!] Missing required symbols (C or {target_lower}).")
        return None

    car = cars[0]
    best_slot, best_path_car, best_path_lobby = None, None, None
    best_score = float("inf")

    for slot in slots:
        z, y, x = slot
        lobbies_same_floor = [l for l in find_positions(floors, "O") if l[0] == z]
        if not lobbies_same_floor:
            continue

        path_car = pathfind(floors, car, slot, algo)
        if not path_car or path_car[-1] != slot:
            continue

        best_lobby_path = None
        best_lobby_len = float("inf")
        for lobby in lobbies_same_floor:
            path_l = pathfind(floors, lobby, slot, algo)
            if path_l and path_l[-1] == slot and len(path_l) < best_lobby_len:
                best_lobby_len = len(path_l)
                best_lobby_path = path_l

        if best_lobby_path is None:
            continue

        floor_diff = abs(z - desired_floor) if desired_floor is not None else 0
        score = len(path_car) * w_car + len(best_lobby_path) * w_lobby + (floor_diff * 5)

        if score < best_score:
            best_score = score
            best_slot = slot
            best_path_car = path_car
            best_path_lobby = best_lobby_path

    if not best_slot:
        print("[!] No valid parking slot found that matches the target symbol and is reachable from a lobby.")
        return None

    return best_slot, best_path_car, best_path_lobby, best_score

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
            best_slot, path_car, path_lobby, score = result
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

