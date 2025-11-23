from program import load_floors, find_best_slot, pathfind
import time

def test_floor_10():
    floors = load_floors("maps")
    print("Loaded floors:", len(floors))
    
    # Test A* with desired floor 10
    print("\n--- Testing A* Target Floor 10 ---")
    result = find_best_slot(floors, algo="a_star", target_symbol="P", desired_floor=10)
    if result:
        best_slot = result[0]
        print(f"Result Slot Floor: {best_slot[0]}")
        if best_slot[0] != 10:
            print("FAIL: Did not reach floor 10")
        else:
            print("SUCCESS: Reached floor 10")
    else:
        print("No slot found")
        # Debug: check if we can reach floor 10 manually
        # We can't easily access visited_order here because find_best_slot swallows it if None
        pass

    # Test BFS with desired floor 10
    print("\n--- Testing BFS Target Floor 10 ---")
    result = find_best_slot(floors, algo="bfs", target_symbol="P", desired_floor=10)
    if result:
        best_slot = result[0]
        print(f"Result Slot Floor: {best_slot[0]}")
        if best_slot[0] != 10:
            print("FAIL: Did not reach floor 10")
        else:
            print("SUCCESS: Reached floor 10")
    else:
        print("No slot found")

if __name__ == "__main__":
    test_floor_10()
