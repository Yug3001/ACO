"""
main.py
=======
PathWise — Interactive Path Planning using Soft Computing Algorithms

CLI entry point.  Runs one or all algorithms on a chosen map and
prints a formatted result.

Usage examples
--------------
  python main.py                           # all algorithms on map1.txt
  python main.py --map maps/map2.txt       # different map
  python main.py --algo aco                # only ACO
  python main.py --trials 5               # 5 runs per stochastic algorithm
  python main.py --ants 30 --iters 150    # custom ACO parameters
"""

import argparse
import os
import sys

from environment.grid              import GridEnvironment
from algorithms.aco                import run_aco
from algorithms.genetic_algorithm  import run_ga
from algorithms.pso                import run_pso
from algorithms.astar              import run_astar
from comparison.runner             import run_all, run_trials
from comparison.metrics            import compute_statistics, print_comparison_table


BANNER = """
====================================================================
  PathWise -- Path Planning with Soft Computing
  Algorithms:  ACO  |  Genetic Algorithm  |  PSO  |  A*
====================================================================
"""


def parse_args():
    p = argparse.ArgumentParser(
        description="PathWise: compare path-planning algorithms on a grid."
    )
    p.add_argument("--map",    default="maps/map1.txt",
                   help="Map .txt file  (default: maps/map1.txt)")
    p.add_argument("--algo",   default="all",
                   choices=["aco","ga","pso","astar","all"],
                   help="Algorithm to run  (default: all)")
    p.add_argument("--trials", type=int, default=1,
                   help="Number of independent trials for stochastic algorithms")
    p.add_argument("--ants",   type=int,   default=20,  help="ACO: number of ants")
    p.add_argument("--iters",  type=int,   default=100, help="Iterations / generations")
    p.add_argument("--pop",    type=int,   default=50,
                   help="GA / PSO: population / swarm size")
    p.add_argument("--alpha",  type=float, default=1.0, help="ACO alpha (pheromone weight)")
    p.add_argument("--beta",   type=float, default=2.0, help="ACO beta  (heuristic weight)")
    return p.parse_args()


def _print_result(r: dict):
    """Print one algorithm result in a readable block."""
    sep    = "─" * 54
    status = "SUCCESS ✓" if r["success"] else "FAILED  ✗"
    print(f"\n{sep}")
    print(f"  Algorithm   : {r['algorithm']}")
    print(f"  Status      : {status}")
    if r["success"]:
        p = r["path"]
        preview = str(p[:6]) + ("..." if len(p) > 6 else "")
        print(f"  Path length : {r['path_length']} cells")
        print(f"  Path preview: {preview}")
    print(f"  Exec time   : {r['execution_time']} s")
    print(f"  Iterations  : {r['iterations']}")
    if r.get("convergence"):
        valid = [v for v in r["convergence"] if v != -1]
        if valid:
            print(f"  Convergence : start={valid[0]}  end={valid[-1]}")
    if r.get("pheromone_matrix"):
        mat = r["pheromone_matrix"]
        print(f"  Pheromone   : {len(mat)}×{len(mat[0])} matrix available")


def main():
    print(BANNER)
    args = parse_args()

    # ---- Load grid ----
    if not os.path.exists(args.map):
        print(f"[ERROR] Map file not found: {args.map}")
        sys.exit(1)

    print(f"Loading map: {args.map}")
    grid = GridEnvironment(map_file=args.map)
    print(f"Grid: {grid.rows}×{grid.cols}  |  "
          f"Start: {grid.start}  Goal: {grid.goal}  |  "
          f"Obstacles: {len(grid.obstacles)}  |  "
          f"Diagonal: {grid.allow_diagonal}\n")
    print(grid)
    print()

    # ---- Build parameter config ----
    config = {
        "aco": {"n_ants": args.ants,  "n_iterations": args.iters,
                "alpha": args.alpha,   "beta":         args.beta},
        "ga":  {"population_size": args.pop, "n_generations": args.iters},
        "pso": {"n_particles": args.pop,     "n_iterations":  args.iters},
    }

    # ---- Run ----
    if args.trials > 1:
        print(f"Running {args.trials} trials (stochastic algorithms) ...\n")
        trials = run_trials(grid, config=config, n_trials=args.trials)
        stats  = compute_statistics(trials)
        print_comparison_table(stats)
        return

    if args.algo == "all":
        results = run_all(grid, config=config)
        for r in results:
            _print_result(r)
    elif args.algo == "aco":
        _print_result(run_aco(grid, **config["aco"]))
    elif args.algo == "ga":
        _print_result(run_ga(grid,  **config["ga"]))
    elif args.algo == "pso":
        _print_result(run_pso(grid, **config["pso"]))
    elif args.algo == "astar":
        _print_result(run_astar(grid))

    print()


if __name__ == "__main__":
    main()

