# Parking Lot Pathfinder

**Parking Lot Pathfinder** is a pathfinding simulation tool that finds the optimal parking slot in a multi-floor parking building. It uses classic algorithms (**A***, **Dijkstra**, **BFS**, **Greedy BFS**) to determine the most efficient route.

This project includes both a **Web UI** (Flask-based) and a **CLI** version.

---

## Features

- **Algorithms**: A*, Dijkstra, BFS, Greedy BFS.
- **Multi-floor Support**: Navigates through multiple floors using stairs/elevators.
- **Parking Types**: Normal, Ladies, Disability.
- **Optimization**: Considers distance from entry (Car), distance to Lobby, and floor preference.
- **Visualization**: Web interface to visualize the path and results.

---

## Folder Structure

```
.
├── app.py              # Flask Web Application
├── program.py          # Core Pathfinding Logic & CLI
├── requirements.txt    # Python dependencies
├── maps/               # CSV Map files (Floor layouts)
│   ├── floor0.csv
│   ├── floor1.csv
│   └── ...
├── static/
│   └── style.css       # Web UI Styles
└── templates/
    ├── index.html      # Input Form
    └── result.html     # Results Page
```

---

## Installation

1. **Create a virtual environment** (optional but recommended):
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

---

## Usage

### Option 1: Web UI (Recommended)

1. Run the Flask application:
   ```cmd
   python app.py
   ```
2. Open your browser and navigate to: `http://127.0.0.1:5000/`
3. Select the algorithm, parking type, desired floor, and preference.
4. View the optimal slot and the calculated path.

### Option 2: Command Line Interface (CLI)

1. Run the program script:
   ```cmd
   python program.py
   ```
2. Follow the interactive prompts to select algorithms and parameters.

---

## Map Format (CSV)

Maps are stored in the `maps/` folder. Each `.csv` file represents one floor.
Cells are comma-separated.

| Symbol | Meaning                                              |
| :----- | :--------------------------------------------------- |
| `#`    | Wall / obstacle                                      |
| `.`    | Normal road                                          |
| `>`    | One-way road (Right)                                 |
| `<`    | One-way road (Left)                                  |
| `^`    | One-way road (Up)                                    |
| `v`    | One-way road (Down)                                  |
| `S`    | Stair / Elevator (Vertical connection)               |
| `C`    | Car (Start point)                                    |
| `P`    | Regular Parking Slot                                 |
| `L`    | Ladies Parking Slot                                  |
| `D`    | Disability Parking Slot                              |
| `O`    | Lobby (Destination)                                  |

> **Note**: Stairs (`S`) must be aligned across floors to allow vertical movement.

---

## How It Works

The program finds the **best parking slot** by calculating a combined cost:

```
cost = distance(Car→Slot) * w_car + distance(Lobby→Slot) * w_lobby + (|floor - desired_floor| * 5)
```

- **Car→Slot**: Distance from entry to the parking spot.
- **Lobby→Slot**: Walking distance from the parking spot to the lobby.
- **Floor Preference**: Penalizes floors further from the desired floor.

The slot with the **lowest cost** is selected.

