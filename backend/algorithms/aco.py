# algorithms/aco.py
# -----------------
# Ant Colony Optimization — Ant System (AS) variant — for grid path planning.
#
# ALGORITHM OVERVIEW
# ==================
# Multiple ants explore the grid simultaneously.  At every step each ant
# chooses the next cell probabilistically using:
#
#     p(j) ∝  τ(j)^α  ×  η(j)^β
#
# where:
#   τ(j)  = pheromone level of cell j
#   η(j)  = heuristic desirability = 1 / (heuristic_distance(j, goal) + ε)
#   α     = pheromone influence exponent  (higher → more exploitation)
#   β     = heuristic influence exponent  (higher → more greedy toward goal)
#
# PHEROMONE UPDATE (after each iteration):
#   1. Evaporate:  τ(j) ← (1 − ρ) × τ(j)          for every free cell j
#   2. Deposit:    τ(j) ← τ(j) + Q / L_k           for every cell in ant k's path
#   3. Elitist:    τ(j) ← τ(j) + Q_elite / L_best  for every cell in the global best path
#      (Elitist AS gives extra reward to the historically best path.)
#
# HOW THIS DIFFERS FROM THE ORIGINAL REPO
# ========================================
# * Python 3  (original was Python 2)
# * Uses common GridEnvironment instead of Map / Nodes classes
# * Adds α/β heuristic influence  (original was pheromone-only)
# * Adds max_path_len guard so ants cannot loop forever
# * Adds elitist pheromone update
# * Exposes 2-D pheromone matrix for UI heatmap visualisation
# * Returns the standard PathWise result dict

import time
import numpy as np
from typing import List, Tuple, Optional
from environment.grid import GridEnvironment


class AntColonyOptimization:
    """
    Ant System (AS) with elitist extension for grid-based path planning.

    Parameters
    ----------
    grid         : Shared GridEnvironment instance.
    n_ants       : Number of ants per iteration.
    n_iterations : Total number of ACO iterations.
    alpha        : Pheromone influence exponent (τ^α).
    beta         : Heuristic influence exponent (η^β).
    rho          : Evaporation rate ∈ (0, 1).
    Q            : Pheromone deposit constant for all ants.
    Q_elite      : Extra pheromone deposit for the global-best path (elitist AS).
    max_path_len : Upper bound on path length — prevents infinite loops.
    """

    # ------------------------------------------------------------------
    # Inner class: individual Ant
    # ------------------------------------------------------------------
    class Ant:
        """Represents one ant navigating the grid."""

        def __init__(self, start: Tuple[int,int], goal: Tuple[int,int]):
            self.start = start
            self.goal  = goal
            self.reset()

        def reset(self):
            """Reset ant to the start position for a new tour."""
            self.current      = self.start
            self.visited      = [self.start]          # ordered path
            self.visited_set  = {self.start}          # O(1) membership test
            self.reached_goal = False

        def move_to(self, cell: Tuple[int,int]):
            """Move ant to *cell* and flag if goal reached."""
            self.current = cell
            self.visited.append(cell)
            self.visited_set.add(cell)
            if cell == self.goal:
                self.reached_goal = True

        def get_path(self) -> List[Tuple[int,int]]:
            return list(self.visited)

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------
    def __init__(
        self,
        grid:         GridEnvironment,
        n_ants:       int   = 20,
        n_iterations: int   = 100,
        alpha:        float = 1.0,
        beta:         float = 2.0,
        rho:          float = 0.5,
        Q:            float = 100.0,
        Q_elite:      float = 200.0,
        max_path_len: Optional[int] = None
    ):
        self.grid         = grid
        self.n_ants       = n_ants
        self.n_iterations = n_iterations
        self.alpha        = alpha
        self.beta         = beta
        self.rho          = rho
        self.Q            = Q
        self.Q_elite      = Q_elite
        self.max_path_len = max_path_len or (grid.rows * grid.cols * 2)

        # Pheromone matrix  — free cells start at 1.0, obstacles at 0
        self.pheromone = np.ones((grid.rows, grid.cols), dtype=float)
        for (r, c) in grid.obstacles:
            self.pheromone[r][c] = 0.0

        # Create the colony
        self.ants = [self.Ant(grid.start, grid.goal) for _ in range(n_ants)]

        # Best solution tracking
        self.best_path:   Optional[List[Tuple[int,int]]] = None
        self.best_length: float                           = float('inf')

    # ------------------------------------------------------------------
    # Core ACO steps
    # ------------------------------------------------------------------

    def _select_next_cell(self, ant: 'AntColonyOptimization.Ant') -> Optional[Tuple[int,int]]:
        """
        Probabilistic next-cell selection (core ACO formula).

        p(j) = [τ(j)^α × η(j)^β] / Σ_k [τ(k)^α × η(k)^β]

        Unvisited neighbours are preferred; if all neighbours were already
        visited the ant is allowed to revisit (avoids getting stuck).
        """
        neighbours = self.grid.get_neighbors(*ant.current)
        if not neighbours:
            return None

        # Prefer unvisited cells to avoid needless backtracking
        unvisited = [n for n in neighbours if n not in ant.visited_set]
        candidates = unvisited if unvisited else neighbours

        scores = []
        for (r, c) in candidates:
            tau = self.pheromone[r][c] ** self.alpha
            dist = self.grid.heuristic((r, c), self.grid.goal)
            eta = (1.0 / (dist + 1e-10)) ** self.beta
            scores.append(tau * eta)

        total = sum(scores)
        if total == 0.0:
            # Uniform random fallback
            return candidates[np.random.randint(len(candidates))]

        probs = [s / total for s in scores]
        idx   = np.random.choice(len(candidates), p=probs)
        return candidates[idx]

    def _delete_loops(self, path: List[Tuple[int,int]]) -> List[Tuple[int,int]]:
        """
        Remove cycles from a path  (preserved from the original implementation).

        If a cell appears more than once, the segment between its first and last
        occurrence is cut out, leaving the shorter direct route.
        """
        result: List[Tuple[int,int]] = []
        seen: dict = {}
        for cell in path:
            key = tuple(cell)
            if key in seen:
                # Trim the loop: go back to first occurrence
                result = result[:seen[key] + 1]
                # Rebuild seen map
                seen = {tuple(result[i]): i for i in range(len(result))}
            else:
                seen[key] = len(result)
                result.append(cell)
        return result

    def _evaporate(self):
        """Global pheromone evaporation: τ ← (1 − ρ) × τ for every cell."""
        self.pheromone *= (1.0 - self.rho)
        # Keep obstacle cells at 0
        for (r, c) in self.grid.obstacles:
            self.pheromone[r][c] = 0.0

    def _deposit(self, path: List[Tuple[int,int]], amount: float):
        """
        Add pheromone along *path*.
        Deposit per cell = amount / path_length  (shorter paths deposit more).
        """
        deposit = amount / max(len(path), 1)
        for (r, c) in path:
            self.pheromone[r][c] += deposit

    # ------------------------------------------------------------------
    # Main run method
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """
        Execute the ACO algorithm and return the standard result dict.

        Returns
        -------
        dict with keys:
            algorithm, success, path, path_length, execution_time,
            iterations, convergence, pheromone_matrix, grid_info
        """
        t_start     = time.time()
        convergence = []   # best path length (cell count) after each iteration

        for _ in range(self.n_iterations):
            iter_paths = []

            for ant in self.ants:
                ant.reset()

                # Walk until goal reached or max length exceeded
                while not ant.reached_goal and len(ant.visited) < self.max_path_len:
                    nxt = self._select_next_cell(ant)
                    if nxt is None:
                        break
                    ant.move_to(nxt)

                if ant.reached_goal:
                    clean = self._delete_loops(ant.get_path())
                    iter_paths.append(clean)
                    if len(clean) < self.best_length:
                        self.best_length = len(clean)
                        self.best_path   = clean

            # ---- Pheromone update ----
            self._evaporate()
            for path in iter_paths:
                self._deposit(path, self.Q)                       # all successful ants
            if self.best_path is not None:
                self._deposit(self.best_path, self.Q_elite)       # elitist bonus

            convergence.append(
                int(self.best_length) if self.best_length < float('inf') else -1
            )

        elapsed = time.time() - t_start
        success = self.best_path is not None

        return {
            "algorithm":       "ACO",
            "success":         success,
            "path":            [list(p) for p in self.best_path] if success else [],
            "path_length":     int(self.best_length) if success else -1,
            "execution_time":  round(elapsed, 4),
            "iterations":      self.n_iterations,
            "convergence":     convergence,
            "pheromone_matrix": self.pheromone.tolist(),
            "grid_info":       self.grid.to_dict()
        }


# ------------------------------------------------------------------
# Convenience entry point
# ------------------------------------------------------------------

def run_aco(grid: GridEnvironment, **kwargs) -> dict:
    """
    Run ACO on *grid* with optional keyword parameters.

    Keyword args (all optional — defaults shown):
        n_ants=20, n_iterations=100, alpha=1.0, beta=2.0,
        rho=0.5, Q=100.0, Q_elite=200.0, max_path_len=None

    Returns
    -------
    Standard PathWise result dict.
    """
    return AntColonyOptimization(grid, **kwargs).run()
