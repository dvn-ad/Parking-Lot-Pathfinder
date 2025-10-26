# Parking Lot Pathfinder

**Parking Lot Pathfinder** is a program that simulates an **optimal parking slot finder** using classic **pathfinding algorithms** — **A***, **Dijkstra**, **BFS**, and **Greedy BFS** — to determine the most efficient route inside a **multi-floor parking building**.

Each parking floor is represented as a **`.csv` map file** stored inside the `maps/` folder.

---

## Folder Structure

```
maps/
 ├── floor0.csv
 ├── floor1.csv
 ├── floor2.csv
 ├── floor3.csv
 ├── floor4.csv
 ├── floor5.csv
 ├── floor6.csv
 ├── floor7.csv
 ├── floor8.csv
 └── floor9.csv
program.py
```

Each `.csv` file represents **one parking floor**.

---

## Map Format (CSV)

* The map size is flexible (recommended **20×20** for testing).
* Cells are **comma-separated**, one symbol per cell.

| Symbol | Meaning                                              |
| :----- | :--------------------------------------------------- |
| `#`    | Wall / obstacle (cannot be passed)                   |
| `.`    | Normal road (bidirectional)                          |
| `>`    | One-way road to the **right**                        |
| `<`    | One-way road to the **left**                         |
| `^`    | One-way road **upward**                              |
| `v`    | One-way road **downward**                            |
| `S`    | Stair / elevator (connects vertically across floors) |
| `C`    | Car (**starting point**)                             |
| `P`    | Regular parking slot (**default goal**)              |
| `L`    | **Ladies parking slot**                              |
| `D`    | **Disability parking slot**                          |
| `O`    | **Lobby** (destination after parking)                |

> ⚠️ Stairs (`S`) must be aligned across floors to allow vertical movement.

---

## How It Works

1. Loads all `.csv` files from the `maps/` folder.

2. User chooses algorithm(s):

   * `A*`
   * `Dijkstra`
   * `BFS`
   * `Greedy BFS`
   * `Run all` → runs all four and compares execution times.

3. User chooses **parking type**:

   * Normal (`P`)
   * Ladies (`L`)
   * Disability (`D`)

4. User inputs a **desired floor** — program prioritizes slots closer to this floor.

5. Optionally, display the **full path**.

6. The program finds the **best parking slot** by considering:

   * Shortest path from **Car → Slot**
   * Shortest path from **Lobby → Slot**
   * Distance from **desired floor**

7. **Combined cost formula**:

   ```
   cost = distance(Car→Slot) * w_car + distance(Lobby→Slot) * w_lobby + (|floor - desired_floor| * 5)
   ```

   * `w_car` and `w_lobby` are weights depending on user preference.
   * Floor difference is multiplied by **5** to penalize far floors.

8. Slot with **lowest cost** is chosen as **optimal**.

9. Execution time for each algorithm is printed.

---

## Example Map (`floor0.csv`)

```
#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#
C,>,>,>,>,>,>,>,>,>,>,>,>,>,>,>,>,v,#,#
#,^,P,P,P,#,L,L,L,#,D,D,D,#,P,P,P,v,#
O,^,P,P,P,#,L,L,L,#,D,D,D,#,P,P,P,v,#
#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#
```

---

## Running the Program

```bash
python program.py
```

Follow the prompts:

```
[1] A*
[2] Dijkstra
[3] BFS
[4] Greedy BFS
[5] Run all
Choose algorithm: 5

Parking Type:
[1] Normal
[2] Ladies
[3] Disability
Choose type: 1

Enter desired floor number (0 = ground):
Desired floor: 5

Show paths? (y/n): n
```

---

## Example Output

```
=== Running A* ===
Best slot: Floor 4, Pos (3, 9)
Total combined cost (Car + Lobby + Floor offset): 52
Execution Time: 0.0312 seconds

=== Running Dijkstra ===
Best slot: Floor 4, Pos (3, 9)
Total combined cost (Car + Lobby + Floor offset): 52
Execution Time: 0.0345 seconds

=== Running BFS ===
Best slot: Floor 4, Pos (3, 9)
Total combined cost (Car + Lobby + Floor offset): 52
Execution Time: 0.0301 seconds

=== Running Greedy BFS ===
Best slot: Floor 4, Pos (3, 9)
Total combined cost (Car + Lobby + Floor offset): 52
Execution Time: 0.0298 seconds
```

If `Show paths = y`, detailed paths are printed:

```
Path from Car → Slot:
  Floor 0 → (2, 1)
  Floor 0 → (2, 2)
  ...

Path from Lobby → Slot:
  Floor 0 → (4, 1)
  Floor 0 → (4, 2)
  ...
```

---

## Notes

* Each map **must contain at least**:

  * One Car (`C`)
  * One Lobby (`O`)
  * At least one parking slot (`P`, `L`, or `D`)

* Be careful with **one-way roads** (`> < ^ v`) — wrong placement may block paths.

* The program automatically warns about missing symbols.

* Larger maps (e.g., 30×30+) give better comparisons between algorithms.

* Adjust **floor penalty multiplier** in the code if you want to change floor preference weighting.

---
