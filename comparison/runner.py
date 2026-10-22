# comparison/runner.py
# --------------------
# Runs all four path-planning algorithms on the SAME grid and
# collects their results in a unified format.
#
# Two entry points are provided:
#   run_all()    — single run of every algorithm
#   run_trials() — multiple runs for stochastic algorithms (ACO, GA, PSO)
#                  (A* is deterministic so it runs only once)

import time
from typing import Dict, List, Optional
from environment.grid import GridEnvironment
from algorithms.aco   import run_aco
from algorithms.genetic_algorithm import run_ga
from algorithms.pso   import run_pso
from algorithms.astar import run_astar


# ---- Default parameter sets (can be overridden via config dict) ----

DEFAULT_ACO = {
    "n_ants":       20,
    "n_iterations": 100,
    "alpha":        1.0,
    "beta":         2.0,
    "rho":          0.5,
    "Q":            100.0,
    "Q_elite":      200.0,
}

DEFAULT_GA = {
    "population_size": 50,
    "n_generations":   100,
    "mutation_rate":   0.2,
    "crossover_rate":  0.8,
    "elitism_count":   2,
    "tournament_size": 3,
}

DEFAULT_PSO = {
    "n_particles":  30,
    "n_iterations": 100,
    "w":            0.5,
    "c1":           1.5,
    "c2":           1.5,
}


def run_all(grid: GridEnvironment, config: Optional[Dict] = None) -> List[dict]:
    """
    Run ACO, GA, PSO and A* once on *grid* and return all results.

    Args:
        grid   : Shared GridEnvironment (same for all algorithms).
        config : Optional dict with keys 'aco', 'ga', 'pso' to override
                 default parameters.  Example:
                     config = {'aco': {'n_ants': 30}, 'ga': {'n_generations': 200}}

    Returns
    -------
    List of four result dicts (one per algorithm), in order: ACO, GA, PSO, A*.
    """
    cfg = config or {}
    aco_p = {**DEFAULT_ACO, **cfg.get('aco', {})}
    ga_p  = {**DEFAULT_GA,  **cfg.get('ga',  {})}
    pso_p = {**DEFAULT_PSO, **cfg.get('pso', {})}

    results = []

    print("[ACO] Running Ant Colony Optimization ...")
    results.append(run_aco(grid, **aco_p))

    print("[GA ] Running Genetic Algorithm ...")
    results.append(run_ga(grid, **ga_p))

    print("[PSO] Running Particle Swarm Optimization ...")
    results.append(run_pso(grid, **pso_p))

    print("[A* ] Running A* Search ...")
    results.append(run_astar(grid))

    return results


def run_trials(
    grid:     GridEnvironment,
    config:   Optional[Dict] = None,
    n_trials: int = 5
) -> Dict[str, List[dict]]:
    """
    Run stochastic algorithms (ACO, GA, PSO) *n_trials* times on *grid*.
    A* is deterministic and is run only once (replicated for uniform structure).

    Args:
        grid     : Shared GridEnvironment.
        config   : Optional parameter overrides (same as run_all).
        n_trials : Number of independent runs per stochastic algorithm.

    Returns
    -------
    Dict  {algorithm_name: [result_dict, ...]}
    with *n_trials* entries for ACO, GA, PSO and one entry (replicated) for A*.
    """
    cfg   = config or {}
    aco_p = {**DEFAULT_ACO, **cfg.get('aco', {})}
    ga_p  = {**DEFAULT_GA,  **cfg.get('ga',  {})}
    pso_p = {**DEFAULT_PSO, **cfg.get('pso', {})}

    all_results: Dict[str, List[dict]] = {
        "ACO": [], "GA": [], "PSO": [], "A*": []
    }

    print(f"Running {n_trials} trials per stochastic algorithm ...")
    for trial in range(1, n_trials + 1):
        print(f"  Trial {trial}/{n_trials}", end=" | ", flush=True)

        r_aco = run_aco(grid, **aco_p)
        r_ga  = run_ga(grid,  **ga_p)
        r_pso = run_pso(grid, **pso_p)

        all_results["ACO"].append(r_aco)
        all_results["GA"].append(r_ga)
        all_results["PSO"].append(r_pso)

        statuses = " ".join(
            f"{n}:{'OK' if r['success'] else 'FAIL'}"
            for n, r in [("ACO", r_aco), ("GA", r_ga), ("PSO", r_pso)]
        )
        print(statuses)

    print("[A* ] Running A* (deterministic — single run) ...")
    astar_result = run_astar(grid)
    # Replicate so every algorithm has the same number of entries
    all_results["A*"] = [astar_result] * n_trials

    return all_results
