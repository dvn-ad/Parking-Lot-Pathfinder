# Parking Lot Pathfinder

A web-based application that helps users find the optimal parking slot in a multi-story parking complex. It utilizes various pathfinding algorithms to calculate the best route based on user preferences, such as proximity to the lobby or the car entrance.

## Features

- **Multiple Pathfinding Algorithms**: Choose between A*, Dijkstra, BFS, and Greedy BFS.
- **Parking Types**: Support for Normal (P), Ladies (L), and Disability (D) parking slots.
- **User Preferences**:
    -   Prioritize parking closer to the **Lobby** or the **Car Entrance**.
    -   Specify a **Desired Floor**.
- **Visual Navigation**: Displays the path from the car entrance to the parking slot and from the slot to the nearest lobby on a grid map.
- **Performance Comparison**: Option to run all algorithms simultaneously to compare execution time and path efficiency.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/dvn-ad/Parking-Lot-Pathfinder.git
    cd Parking-Lot-Pathfinder
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Start the Flask application:
    ```bash
    python app.py
    ```

2.  Open your web browser and navigate to:
    ```
    http://127.0.0.1:5000
    ```

3.  Select your preferences:
    -   **Algorithm**: Choose a specific algorithm or "Run all".
    -   **Parking Type**: Normal, Ladies, or Disability.
    -   **Desired Floor**: (Optional) Enter a floor number.
    -   **Preference**: Closer to Lobby or Car.
    -   **Show Path**: Check to visualize the route.

4.  Click **Find Slot** to see the results.

## Map Legend

The parking lot maps are defined in CSV files within the `maps/` directory.

-   `.`: Road / Driveway
-   `#`: Wall / Obstacle
-   `C`: Car Entrance (Start Point)
-   `O`: Lobby / Pedestrian Exit
-   `p`, `l`, `d`: Available Parking Slots (Normal, Ladies, Disability)
-   `N`: Ramp Up (Naik) - Connects to `E` on the floor above.
-   `T`: Ramp Down (Turun) - Connects to `e` on the floor below.
-   `E`: Entrance from floor below.
-   `e`: Entrance from floor above.
-   `>`, `<`, `^`, `v`: One-way directional arrows.

## Algorithms Implemented

-   **A* (A-Star)**: Uses a heuristic (Manhattan distance) to find the shortest path efficiently.
-   **Dijkstra**: Guarantees the shortest path but explores more nodes than A*.
-   **BFS (Breadth-First Search)**: Explores all neighbors layer by layer; guarantees shortest path in unweighted graphs.
-   **Greedy BFS**: Prioritizes nodes closer to the goal based on heuristic; faster but does not guarantee the shortest path.
