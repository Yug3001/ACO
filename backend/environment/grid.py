# environment/grid.py
# -------------------
# Common grid environment shared by all PathWise algorithms.
#
# Map symbols (old format — primary):
#   S = Start       F = Goal/Final    E = Empty    O = Obstacle
# Map symbols (new format — also supported):
#   S = Start       G = Goal          . = Empty    X = Obstacle
#
# Movement: 8-directional by default (4 cardinal + 4 diagonal).
# Heuristic for 8-dir: Chebyshev distance  h = max(|dr|, |dc|)
# Heuristic for 4-dir: Manhattan distance  h = |dr| + |dc|

import numpy as np
from typing import List, Tuple, Optional, Set


class GridEnvironment:
    """
    2D grid environment for path planning, shared by ACO, GA, PSO and A*.

    Attributes:
        rows (int)              : Number of rows in the grid.
        cols (int)              : Number of columns in the grid.
        start (Tuple[int,int])  : (row, col) of the start cell.
        goal  (Tuple[int,int])  : (row, col) of the goal cell.
        obstacles (set)         : Set of (row, col) obstacle positions.
        occupancy (ndarray)     : 2-D array — 1=free, 0=obstacle.
        allow_diagonal (bool)   : True → 8-dir movement (default).
    """

    # ---- Symbol tables (support both old and new map formats) ----
    OBSTACLE_SYMBOLS = {'O', 'X'}
    FREE_SYMBOLS     = {'E', '.'}
    START_SYMBOLS    = {'S'}
    GOAL_SYMBOLS     = {'F', 'G'}

    def __init__(
        self,
        grid_array: Optional[List] = None,
        map_file:   Optional[str]  = None,
        allow_diagonal: bool = True          # 8-directional by default
    ):
        """
        Initialise the grid environment.

        Args:
            grid_array     : 2-D list of strings  OR  NumPy array of strings.
            map_file       : Path to a .txt map file (space-separated symbols).
            allow_diagonal : If True, ants/agents may move diagonally (default True).

        Exactly one of grid_array / map_file must be supplied.
        """
        self.allow_diagonal = allow_diagonal

        if map_file is not None:
            self.grid = self._load_from_file(map_file)
        elif grid_array is not None:
            self.grid = np.array(grid_array, dtype=str)
        else:
            raise ValueError("Provide either grid_array or map_file.")

        self.rows, self.cols = self.grid.shape
        self.start:     Tuple[int, int]      = self._find_symbol(self.START_SYMBOLS)
        self.goal:      Tuple[int, int]      = self._find_symbol(self.GOAL_SYMBOLS)
        self.obstacles: Set[Tuple[int, int]] = self._find_obstacles()
        self.occupancy: np.ndarray           = self._build_occupancy()

        if self.start is None:
            raise ValueError("No start cell (S) found in the map.")
        if self.goal is None:
            raise ValueError("No goal cell (F or G) found in the map.")

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _load_from_file(self, path: str) -> np.ndarray:
        """Parse a text map — one row per line, symbols separated by spaces."""
        rows = []
        with open(path, 'r') as fh:
            for line in fh:
                stripped = line.strip()
                if stripped:
                    rows.append(stripped.split())
        return np.array(rows, dtype=str)

    def _find_symbol(self, symbols: Set[str]) -> Optional[Tuple[int, int]]:
        """Return (row, col) of the first cell matching any symbol in *symbols*."""
        for sym in symbols:
            positions = np.argwhere(self.grid == sym)
            if len(positions) > 0:
                return (int(positions[0][0]), int(positions[0][1]))
        return None

    def _find_obstacles(self) -> Set[Tuple[int, int]]:
        """Collect all obstacle cell coordinates into a set."""
        obs = set()
        for sym in self.OBSTACLE_SYMBOLS:
            for pos in np.argwhere(self.grid == sym):
                obs.add((int(pos[0]), int(pos[1])))
        return obs

    def _build_occupancy(self) -> np.ndarray:
        """Binary matrix: 1 = free/walkable, 0 = obstacle."""
        occ = np.ones((self.rows, self.cols), dtype=int)
        for (r, c) in self.obstacles:
            occ[r][c] = 0
        return occ

    # ------------------------------------------------------------------ #
    #  Public API used by every algorithm                                  #
    # ------------------------------------------------------------------ #

    def is_valid(self, row: int, col: int) -> bool:
        """True if (row, col) is inside the grid boundaries and not an obstacle."""
        return (0 <= row < self.rows and
                0 <= col < self.cols and
                self.occupancy[row][col] == 1)

    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Return all valid neighbouring cells reachable from (row, col).

        8 directions when allow_diagonal=True (default):
            NW  N  NE
             W  .  E
            SW  S  SE

        4 directions when allow_diagonal=False:
                N
             W  .  E
                S
        """
        if self.allow_diagonal:
            deltas = [(-1,-1),(-1,0),(-1,1),
                      ( 0,-1),        ( 0,1),
                      ( 1,-1),( 1,0),( 1,1)]
        else:
            deltas = [(-1,0),(1,0),(0,-1),(0,1)]

        return [
            (row + dr, col + dc)
            for dr, dc in deltas
            if self.is_valid(row + dr, col + dc)
        ]

    def move_cost(self, a: Tuple[int,int], b: Tuple[int,int]) -> float:
        """
        Cost of a single step from cell a to adjacent cell b.
        Diagonal move  → cost = sqrt(2) ≈ 1.414
        Cardinal move  → cost = 1.0
        """
        dr = abs(b[0] - a[0])
        dc = abs(b[1] - a[1])
        return 1.414 if (dr == 1 and dc == 1) else 1.0

    def manhattan_distance(self, a: Tuple[int,int], b: Tuple[int,int]) -> float:
        """L1 distance: |Δrow| + |Δcol|.  Admissible heuristic for 4-dir grids."""
        return float(abs(a[0]-b[0]) + abs(a[1]-b[1]))

    def chebyshev_distance(self, a: Tuple[int,int], b: Tuple[int,int]) -> float:
        """
        L∞ distance: max(|Δrow|, |Δcol|).
        Admissible heuristic for 8-dir grids because a diagonal move covers
        both a row step AND a column step simultaneously.
        """
        return float(max(abs(a[0]-b[0]), abs(a[1]-b[1])))

    def heuristic(self, a: Tuple[int,int], b: Tuple[int,int]) -> float:
        """Auto-select the correct admissible heuristic for the movement mode."""
        if self.allow_diagonal:
            return self.chebyshev_distance(a, b)
        return self.manhattan_distance(a, b)

    def to_dict(self) -> dict:
        """Serialise the environment to a JSON-compatible dictionary (for the API)."""
        return {
            "rows": self.rows,
            "cols": self.cols,
            "start": list(self.start),
            "goal":  list(self.goal),
            "obstacles": [list(o) for o in sorted(self.obstacles)],
            "allow_diagonal": self.allow_diagonal,
            "grid": self.grid.tolist()
        }

    def __repr__(self) -> str:
        """Pretty-print the grid to the console."""
        lines = []
        for r in range(self.rows):
            lines.append("  " + " ".join(self.grid[r]))
        return "\n".join(lines)
