
# Parking Lot Pathfinder

This program simulates an **optimal parking slot finder** using classic **pathfinding algorithms** — **A***, **Dijkstra**, and **BFS** — to determine the most efficient route inside a **multi-floor parking building**.

Each parking floor is represented as a **`.csv` map file** stored inside the `maps/` folder.

---

## Folder Structure

```
maps/
 ├── floor0.csv
 ├── floor1.csv
 └── floor2.csv
program.py
```

Each `.csv` file represents **one parking floor**, and all files are placed inside the `maps/` directory.

---

## Map Format (CSV)

* The map size is **flexible** (recommended: 20×20 for testing).
* Use commas (`,`) to separate each cell.
* Each cell contains **one character** from the symbol table below:

| Symbol | Meaning                                                 |
| :----- | :------------------------------------------------------ |
| `#`    | Wall / obstacle (cannot be passed)                      |
| `.`    | Normal road (bidirectional path)                        |
| `>`    | One-way road to the **right**                           |
| `<`    | One-way road to the **left**                            |
| `^`    | One-way road **upward**                                 |
| `v`    | One-way road **downward**                               |
| `S`    | Stair / elevator (connects the same cell across floors) |
| `C`    | Car (**starting point**)                                |
| `P`    | Regular parking slot (**default goal**)                 |
| `L`    | **Ladies parking slot**                                 |
| `D`    | **Disability parking slot**                             |
| `O`    | **Lobby** (destination after parking)                   |

---

## ⚙️ How It Works

1. The program loads all `.csv` files in the `maps/` folder (each file = one floor).
2. You choose which algorithm(s) to run:

   * `A*`
   * `Dijkstra`
   * `BFS`
   * `Run all` → runs all three and compares their times.
3. Then choose which **parking type** to look for:

   * Normal (`P`)
   * Ladies (`L`)
   * Disability (`D`)
4. Optionally, you can choose whether to **display the full path**.
5. The program finds the **best parking slot** based on:

   * Shortest path from the **car (`C`)** to the slot.
   * Shortest path from the **lobby (`O`)** to the same slot.
6. The **total combined cost** = distance(Car→Slot) + distance(Lobby→Slot).
7. The slot with the smallest combined cost is chosen as the **optimal parking spot**.
8. Each algorithm shows its **execution time in seconds**.

---

## Example Map (floor0.csv)

```
#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#
C,>,>,>,>,>,>,>,>,>,>,>,>,>,>,>,>,v,#
#,^,P,P,P,#,L,L,L,#,D,D,D,#,P,P,P,v,#
O,^,P,P,P,#,L,L,L,#,D,D,D,#,P,P,P,v,#
#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#,#
```

---

## How to Run

```bash
python program.py
```

Then follow the prompts:

```
[1] A*
[2] Dijkstra
[3] BFS
[4] Run all
Choose algorithm: 4

Parking Type:
[1] Normal
[2] Ladies
[3] Disability
Choose type: 1

Show paths? (y/n): n
```

---

## Example Output

```
=== Running A_STAR ===
Best slot: Floor 0, Pos (2, 8)
Total combined cost (Car + Lobby): 46
Execution Time: 0.0283 seconds

=== Running DIJKSTRA ===
Best slot: Floor 0, Pos (2, 8)
Total combined cost (Car + Lobby): 46
Execution Time: 0.0309 seconds

=== Running BFS ===
Best slot: Floor 0, Pos (2, 8)
Total combined cost (Car + Lobby): 46
Execution Time: 0.0271 seconds
```

If you chose `Show paths? = y`, the program also prints detailed coordinates for both routes:

```
Path from Car → Slot:
  Floor 0 → (1, 0)
  Floor 0 → (1, 1)
  ...

Path from Lobby → Slot:
  Floor 0 → (3, 0)
  Floor 0 → (3, 1)
  ...
```

---

## 🧠 Notes

* Each map **must contain at least**:

  * One car (`C`)
  * One lobby (`O`)
  * At least one parking slot (`P`, `L`, or `D`)
* Stairs/elevators (`S`) **must be aligned** across floors for vertical travel to work.
* Be careful with **one-way roads** (`> < ^ v`) — they can block paths if placed wrong.
* The program automatically detects and warns about missing key symbols (`missing C, P, or O`).
* You can test algorithm efficiency differences better using **larger maps** (like 30×30 or more).

---
