# experiments/experiment_runner.py
# ---------------------------------
# Pre-defined experiments for the PathWise project.
# Run this file directly to execute all experiments and save results to JSON.

import os
import json
from typing import Dict, List, Optional

from environment.grid      import GridEnvironment
from comparison.runner     import run_all, run_trials
from comparison.metrics    import compute_statistics, print_comparison_table
from visualization.data_formatter import format_multi_result


RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def _save(filename: str, data: dict):
    """Save *data* as pretty-printed JSON in RESULTS_DIR."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, default=str)
    print(f"  Saved → {path}")


# ------------------------------------------------------------------ #
#  Experiment 1 — Quick demo (single run, small map)                 #
# ------------------------------------------------------------------ #

def run_quick_demo(map_file: str = "maps/map1.txt") -> List[dict]:
    """
    Run every algorithm once on *map_file* and print a one-line summary.
    Good for quickly checking the system works end-to-end.
    """
    print("\n" + "=" * 60)
    print("  EXPERIMENT 1 — Quick Demo (single run)")
    print("=" * 60)

    grid = GridEnvironment(map_file=map_file)
    print(f"  Map: {map_file}  |  {grid.rows}×{grid.cols}  |  "
          f"Start:{grid.start}  Goal:{grid.goal}  "
          f"Obstacles:{len(grid.obstacles)}\n")

    results = run_all(grid)

    print("\n  Results:")
    for r in results:
        ok  = "OK  " if r["success"] else "FAIL"
        ln  = r["path_length"] if r["success"] else "N/A"
        print(f"    [{ok}]  {r['algorithm']:<5}  len={ln:<5}  "
              f"time={r['execution_time']}s  iters={r['iterations']}")

    _save("exp1_quick_demo.json", format_multi_result(grid, results))
    return results


# ------------------------------------------------------------------ #
#  Experiment 2 — Multi-trial stochastic comparison                  #
# ------------------------------------------------------------------ #

def run_multi_trial(
    map_file: str           = "maps/map2.txt",
    n_trials: int           = 5,
    config:   Optional[Dict]= None
) -> Dict[str, dict]:
    """
    Run stochastic algorithms *n_trials* times on *map_file* and
    report statistics.  A* is run once (deterministic).
    """
    print("\n" + "=" * 60)
    print(f"  EXPERIMENT 2 — Multi-trial ({n_trials} trials)")
    print("=" * 60)

    grid = GridEnvironment(map_file=map_file)
    print(f"  Map: {map_file}  |  {grid.rows}×{grid.cols}\n")

    trials = run_trials(grid, config=config, n_trials=n_trials)
    stats  = compute_statistics(trials)
    print_comparison_table(stats)

    _save(f"exp2_multi_trial_{n_trials}x.json", {
        "map_file": map_file,
        "n_trials": n_trials,
        "statistics": stats
    })
    return stats


# ------------------------------------------------------------------ #
#  Experiment 3 — Map comparison                                     #
# ------------------------------------------------------------------ #

def run_map_comparison(
    map_files: Optional[List[str]] = None,
    n_trials:  int                  = 3
) -> Dict[str, Dict[str, dict]]:
    """
    Compare algorithm performance across multiple maps.
    """
    if map_files is None:
        map_files = [
            "maps/map1.txt",
            "maps/map_pathwise_small.txt",
            "maps/map2.txt",
            "maps/map_pathwise_medium.txt",
        ]

    print("\n" + "=" * 60)
    print("  EXPERIMENT 3 — Multi-map Comparison")
    print("=" * 60)

    all_stats: Dict[str, Dict[str, dict]] = {}

    for mf in map_files:
        if not os.path.exists(mf):
            print(f"  [!] Not found: {mf} — skipping")
            continue
        print(f"\n  --- {mf} ---")
        try:
            grid   = GridEnvironment(map_file=mf)
            print(f"  Grid: {grid.rows}×{grid.cols}")
            trials = run_trials(grid, n_trials=n_trials)
            stats  = compute_statistics(trials)
            print_comparison_table(stats)
            all_stats[mf] = stats
        except Exception as exc:
            print(f"  [!] Error: {exc}")

    _save("exp3_map_comparison.json", all_stats)
    return all_stats


# ------------------------------------------------------------------ #
#  Entry point                                                        #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    run_quick_demo()
    run_multi_trial(n_trials=3)
    run_map_comparison(n_trials=3)
