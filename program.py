import heapq
from typing import List, Tuple, Set, Optional

class MazeSolver:
    def __init__(self, maze: List[List[str]]):
        """
        Initialize the maze solver with A* algorithm
        
        Args:
            maze: 2D list representing the maze where:
                  '#' = wall
                  ' ' or '.' = path
                  'S' = start
                  'E' = exit/goal
        """
        self.maze = maze
        self.rows = len(maze)
        self.cols = len(maze[0]) if maze else 0
        self.start = None
        self.end = None
        self._find_start_and_end()
    
    def _find_start_and_end(self):
        """Find the start (S) and end (E) positions in the maze"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.maze[i][j] == 'S':
                    self.start = (i, j)
                elif self.maze[i][j] == 'E':
                    self.end = (i, j)
        
        if not self.start or not self.end:
            raise ValueError("Maze must contain both 'S' (start) and 'E' (exit) markers")
    
    def heuristic(self, pos: Tuple[int, int]) -> float:
        """
        Calculate Manhattan distance heuristic from pos to end
        
        Args:
            pos: Current position (row, col)
            
        Returns:
            Manhattan distance to the goal
        """
        return abs(pos[0] - self.end[0]) + abs(pos[1] - self.end[1])
    
    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions (up, down, left, right)
        
        Args:
            pos: Current position (row, col)
            
        Returns:
            List of valid neighbor positions
        """
        row, col = pos
        neighbors = []
        
        # Directions: up, down, left, right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Check if within bounds
            if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                # Check if not a wall
                if self.maze[new_row][new_col] != '#':
                    neighbors.append((new_row, new_col))
        
        return neighbors
    
    def solve(self) -> Optional[List[Tuple[int, int]]]:
        """
        Solve the maze using A* algorithm
        
        Returns:
            List of positions representing the path from start to end,
            or None if no path exists
        """
        # Priority queue: (f_score, counter, position)
        # counter is used to break ties consistently
        counter = 0
        open_set = [(0, counter, self.start)]
        counter += 1
        
        # Track visited nodes
        came_from = {}
        
        # g_score: cost from start to current node
        g_score = {self.start: 0}
        
        # f_score: g_score + heuristic (estimated total cost)
        f_score = {self.start: self.heuristic(self.start)}
        
        # Set of positions in open_set for faster lookup
        open_set_hash = {self.start}
        
        while open_set:
            # Get node with lowest f_score
            current_f, _, current = heapq.heappop(open_set)
            open_set_hash.remove(current)
            
            # Check if we reached the goal
            if current == self.end:
                return self._reconstruct_path(came_from, current)
            
            # Explore neighbors
            for neighbor in self.get_neighbors(current):
                # Tentative g_score
                tentative_g_score = g_score[current] + 1
                
                # If this path to neighbor is better than any previous one
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # Record the best path
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor)
                    
                    # Add to open set if not already there
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                        counter += 1
                        open_set_hash.add(neighbor)
        
        # No path found
        return None
    
    def _reconstruct_path(self, came_from: dict, current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from start to end
        
        Args:
            came_from: Dictionary mapping each position to its predecessor
            current: Current (final) position
            
        Returns:
            List of positions from start to end
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
    def visualize_solution(self, path: Optional[List[Tuple[int, int]]] = None):
        """
        Print the maze with the solution path marked
        
        Args:
            path: List of positions representing the solution path
        """
        if path is None:
            print("No solution found!")
            print("\nOriginal Maze:")
            for row in self.maze:
                print(''.join(row))
            return
        
        # Create a copy of the maze for visualization
        solution_maze = [row[:] for row in self.maze]
        
        # Mark the path (excluding start and end)
        for pos in path[1:-1]:
            solution_maze[pos[0]][pos[1]] = '*'
        
        print(f"Solution found! Path length: {len(path)}")
        print("\nMaze with solution (marked with *):")
        for row in solution_maze:
            print(''.join(row))


def read_maze_from_input() -> List[List[str]]:
    """
    Read maze from user input
    
    Returns:
        2D list representing the maze
    """
    print("Enter the maze (press Enter twice when done):")
    print("Use: '#' for walls, ' ' or '.' for paths, 'S' for start, 'E' for exit")
    print()
    
    maze = []
    while True:
        line = input()
        if not line:
            break
        maze.append(list(line))
    
    return maze


def main():
    print("=" * 50)
    print("A* Maze Solver")
    print("=" * 50)
    print()
    
    # Option 1: Use a predefined maze for testing
    print("Choose input method:")
    print("1. Use example maze")
    print("2. Enter custom maze")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        # Example maze
        maze = [
            list("##########"),
            list("#S.......#"),
            list("#.####.#.#"),
            list("#....#.#.#"),
            list("####.#.#.#"),
            list("#....#...#"),
            list("#.####.###"),
            list("#......#E#"),
            list("##########")
        ]
        print("\nUsing example maze:")
        for row in maze:
            print(''.join(row))
    else:
        # Custom maze input
        maze = read_maze_from_input()
    
    print("\n" + "=" * 50)
    
    try:
        # Create solver and solve the maze
        solver = MazeSolver(maze)
        print(f"Start position: {solver.start}")
        print(f"Exit position: {solver.end}")
        print("\nSolving maze using A* algorithm...")
        print()
        
        path = solver.solve()
        solver.visualize_solution(path)
        
        if path:
            print(f"\nPath coordinates: {path}")
            
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
