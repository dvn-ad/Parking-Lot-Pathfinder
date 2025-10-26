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
    for file in sorted(os.listdir(folder)):
        if file.endswith(".csv"):
            floors.append(read_csv_grid(os.path.join(folder, file)))
    return floors

# ---------- PATHFINDING UTILS ----------
def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])

def can_move(floors, z, y, x, dy, dx):
    cell = floors[z][y][x]
    if cell in [".", "C", "P", "L", "D", "O", "S"]:
        return True
    if cell == ">": return (dy, dx) == (0, 1)
    if cell == "<": return (dy, dx) == (0, -1)
    if cell == "^": return (dy, dx) == (-1, 0)
    if cell == "v" or cell == "V": return (dy, dx) == (1, 0)
    return False

def get_neighbors(pos, floors):
    z, y, x = pos
    neighbors = []
    height, width = len(floors[z]), len(floors[z][0])
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    for dy, dx in directions:
        ny, nx = y + dy, x + dx
        if 0 <= ny < height and 0 <= nx < width:
            if floors[z][ny][nx] != "#" and can_move(floors, z, y, x, dy, dx):
                neighbors.append((z, ny, nx))

    if floors[z][y][x] == "S":
        if z + 1 < len(floors) and floors[z+1][y][x] == "S":
            neighbors.append((z+1, y, x))
        if z - 1 >= 0 and floors[z-1][y][x] == "S":
            neighbors.append((z-1, y, x))
    return neighbors

# ---------- PATHFINDING ALGORITHMS ----------
def pathfind(floors, start, goal, algo="a_star"):
    if algo == "bfs":
        return bfs(floors, start, goal)
    elif algo == "dijkstra":
        return dijkstra(floors, start, goal)
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
        for neighbor in get_neighbors(current, floors):
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
        for neighbor in get_neighbors(current, floors):
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
        for neighbor in get_neighbors(current, floors):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)
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

def find_best_slot(floors, algo="a_star", target_symbol="P", desired_floor=None):
    cars = find_positions(floors, "C")
    slots = find_positions(floors, target_symbol)
    lobbies = find_positions(floors, "O")

    if not cars or not slots or not lobbies:
        print("missing C, target slot, or O")
        return None

    car = cars[0]
    lobby = lobbies[0]
    best_slot, best_path_car, best_path_lobby = None, None, None
    best_score = float("inf")

    for slot in slots:
        path_car = pathfind(floors, car, slot, algo)
        path_lobby = pathfind(floors, lobby, slot, algo)
        if not path_car or not path_lobby:
            continue

        # floor distance penalty (favor closer floor)
        floor_diff = abs(slot[0] - desired_floor) if desired_floor is not None else 0

        # Weighted score: prioritize distance + floor diff
        score = len(path_car) + len(path_lobby) + (floor_diff * 5)

        if score < best_score:
            best_score = score
            best_slot = slot
            best_path_car = path_car
            best_path_lobby = path_lobby
    return best_slot, best_path_car, best_path_lobby, best_score

# ---------- MAIN ----------
if __name__ == "__main__":
    floors = load_floors("maps")

    print("[1] A*")
    print("[2] Dijkstra")
    print("[3] BFS")
    print("[4] Run all")
    inp = input("Choose algorithm: ").strip()

    print("\nParking Type:")
    print("[1] Normal (P)")
    print("[2] Ladies (L)")
    print("[3] Disability (D)")
    p_type = input("Choose type: ").strip()
    target_symbol = {"1": "P", "2": "L", "3": "D"}.get(p_type, "P")

    # New: choose desired floor
    print("\nEnter desired floor number (0 = ground):")
    try:
        desired_floor = int(input("Desired floor: ").strip())
    except ValueError:
        desired_floor = None

    show_path = input("\nShow paths? (y/n): ").strip().lower() == "y"

    algos = []
    if inp == "4":
        algos = ["a_star", "dijkstra", "bfs"]
    elif inp == "1":
        algos = ["a_star"]
    elif inp == "2":
        algos = ["dijkstra"]
    elif inp == "3":
        algos = ["bfs"]
    else:
        print("Invalid choice.")
        exit()

    for algo in algos:
        print(f"\n=== Running {algo.upper()} ===")
        start_time = time.time()
        result = find_best_slot(floors, algo, target_symbol, desired_floor)
        end_time = time.time()
        exec_time = end_time - start_time

        if result:
            best_slot, path_car, path_lobby, score = result
            print(f"Best slot: Floor {best_slot[0]}, Pos ({best_slot[1]}, {best_slot[2]})")
            print(f"Total combined cost (Car + Lobby + Floor offset): {score}")
            print(f"Execution Time: {exec_time:.4f} seconds")
            if show_path:
                print("\nPath from Car → Slot:")
                for step in path_car:
                    print(f"  Floor {step[0]} → ({step[1]}, {step[2]})")
                print("\nPath from Lobby → Slot:")
                for step in path_lobby:
                    print(f"  Floor {step[0]} → ({step[1]}, {step[2]})")
        else:
            print("No valid slot found!")
            print(f"Execution Time: {exec_time:.4f} seconds")
