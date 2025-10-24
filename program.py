import csv
import math
import heapq
import os

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

# ---------- PATHFINDING (A*) ----------
def heuristic(a, b):
    # 3D Manhattan distance
    return abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2])

def get_neighbors(pos, floors):
    z, y, x = pos
    neighbors = []
    height, width = len(floors[0]), len(floors[0][0])
    #height, width = len(floors[z]), len(floors[z][0])

    
    # moves in same floor
    for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
        ny, nx = y + dy, x + dx
        if 0 <= ny < height and 0 <= nx < width:
            if floors[z][ny][nx] != "#":
                neighbors.append((z, ny, nx))
    
    # check vertical (stairs/elevator)
    if floors[z][y][x] == "S":
        if z + 1 < len(floors) and floors[z+1][y][x] == "S":
            neighbors.append((z+1, y, x))
        if z - 1 >= 0 and floors[z-1][y][x] == "S":
            neighbors.append((z-1, y, x))
    return neighbors

def a_star(floors, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            # reconstruct path
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

# ---------- SLOT SEARCH ----------
def find_positions(floors, symbol):
    positions = []
    for z, floor in enumerate(floors):
        for y, row in enumerate(floor):
            for x, val in enumerate(row):
                if val == symbol:
                    positions.append((z, y, x))
    return positions

def find_best_slot(floors):
    entrances = find_positions(floors, "E")
    cars = find_positions(floors, "C")
    slots = find_positions(floors, "P")
    
    if not entrances or not cars or not slots:
        print("missing E, C, or P")
        return None
    
    car = cars[0]
    
    # pick top 5 nearest by heuristic distance to entrance
    scored = sorted(slots, key=lambda s: heuristic(car, s))
    candidates = scored[:5]
    
    best_slot = None
    best_path = None
    best_cost = float("inf")
    
    for slot in candidates:
        path = a_star(floors, car, slot)
        if path and len(path) < best_cost:
            best_cost = len(path)
            best_slot = slot
            best_path = path
    
    return best_slot, best_path, best_cost

# ---------- MAIN ----------
if __name__ == "__main__":
    floors = load_floors("maps")  # folder name
    best_slot, path, cost = find_best_slot(floors)
    
    if best_slot:
        print(f"Best slot: Floor {best_slot[0]}, Pos ({best_slot[1]}, {best_slot[2]})")
        print(f"Total cost: {cost}")
        print("Path:")
        for step in path:
            print(f"  Floor {step[0]} → ({step[1]}, {step[2]})")
    else:
        print("No valid slot found!")
