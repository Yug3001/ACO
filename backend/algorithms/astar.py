# algorithms/astar.py
# --------------------
# A* Search Algorithm — deterministic path-planning baseline.
#
# WHY A* IS INCLUDED (as a non-Soft-Computing baseline)
# ======================================================
# A* is a classical, deterministic, heuristic-guided search algorithm.
# It is NOT a Soft Computing method (no randomness, no population,
# no learning from nature).  It is included in PathWise so that the
# stochastic Soft Computing algorithms (ACO, GA, PSO) can be compared
# against a method that is GUARANTEED to find the OPTIMAL (shortest)
# path when one exists.  This lets us see how close the bio-inspired
# methods come to the mathematical optimum.
#
# ALGORITHM
# =========
# A* maintains an open set (priority queue) of cells to explore,
# sorted by the evaluation function:
#
#     f(n) = g(n) + h(n)
#
# where:
#   g(n) = actual cost accumulated from Start to node n
#   h(n) = admissible heuristic estimate of cost from n to Goal
#          (must NEVER over-estimate the true remaining cost)
#
# HEURISTIC CHOICE
# ================
# For 8-directional movement (diagonal allowed):
#   h(n) = Chebyshev distance = max(|Δrow|, |Δcol|)
#   Admissible because: a diagonal step costs 1.414 and covers
#   both a row AND a column simultaneously, so Chebyshev never
#   over-estimates.
#
# For 4-directional movement:
#   h(n) = Manhattan distance = |Δrow| + |Δcol|
#
# COST MODEL
# ==========
#   Cardinal move  (up/down/left/right) → cost 1.0
#   Diagonal move  (all 4 diagonals)    → cost √2 ≈ 1.414
#
# OUTPUT
# ======
# 'iterations' in the result dict = number of nodes expanded by A*.
# 'convergence' = g(goal) each time a strictly shorter path to the goal
#   is discovered (usually just one entry since A* is optimal on first find).

import heapq
import time
from typing import Dict, List, Optional, Tuple
from environment.grid import GridEnvironment


def run_astar(grid: GridEnvironment) -> dict:
    """
    Execute A* search on *grid*.

    Args:
        grid : Shared GridEnvironment instance.

    Returns
    -------
    Standard PathWise result dict.
        'iterations'  = total nodes expanded.
        'convergence' = list of g(goal) values each time we found a shorter
                        path to the goal (typically [optimal_cost]).
    """
    t_start = time.time()

    start = tuple(grid.start)
    goal  = tuple(grid.goal)

    # g_score[cell] = best known actual cost from start to cell
    g_score: Dict[Tuple[int,int], float] = {start: 0.0}

    # came_from[cell] = predecessor on the best known path to cell
    came_from: Dict[Tuple[int,int], Optional[Tuple[int,int]]] = {start: None}

    # Open set: (f_score, tie_break_counter, cell)
    # tie_break_counter ensures stable heap ordering when f-scores tie
    open_heap: List = []
    counter   = 0
    heapq.heappush(open_heap, (grid.heuristic(start, goal), counter, start))
    counter += 1

    closed:         set   = set()    # fully expanded nodes
    nodes_expanded: int   = 0
    convergence:    list  = []       # track g(goal) improvements

    while open_heap:
        _f, _tie, current = heapq.heappop(open_heap)

        if current in closed:
            continue                  # stale heap entry — skip

        closed.add(current)
        nodes_expanded += 1

        if current == goal:
            break                     # Optimal path to goal found

        for neighbor in grid.get_neighbors(*current):
            if neighbor in closed:
                continue

            step_cost     = grid.move_cost(current, neighbor)
            tentative_g   = g_score[current] + step_cost

            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor]   = tentative_g
                came_from[neighbor] = current

                f_new = tentative_g + grid.heuristic(neighbor, goal)
                heapq.heappush(open_heap, (f_new, counter, neighbor))
                counter += 1

                # Record improvement toward goal
                if neighbor == goal:
                    convergence.append(round(tentative_g, 4))

    elapsed = time.time() - t_start

    # Reconstruct path by backtracking through came_from
    success = goal in came_from

    if success:
        path   = []
        cell   = goal
        while cell is not None:
            path.append(list(cell))
            cell = came_from.get(cell)
        path.reverse()
        path_length = len(path)
    else:
        path        = []
        path_length = -1

    return {
        "algorithm":        "A*",
        "success":          success,
        "path":             path,
        "path_length":      path_length,
        "execution_time":   round(elapsed, 4),
        "iterations":       nodes_expanded,
        "convergence":      convergence if convergence else (
                                [round(g_score.get(goal, -1), 4)] if success else []
                            ),
        "pheromone_matrix": None,
        "grid_info":        grid.to_dict()
    }
