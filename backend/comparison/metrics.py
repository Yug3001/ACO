# comparison/metrics.py
# ---------------------
# Statistical summarisation of algorithm results across multiple trials.

import statistics
from typing import Dict, List


def compute_statistics(trials_by_algorithm: Dict[str, List[dict]]) -> Dict[str, dict]:
    """
    Compute performance statistics per algorithm across multiple trials.

    Args:
        trials_by_algorithm : Output of run_trials() — maps algorithm name
                              to a list of result dicts (one per trial).

    Returns
    -------
    Dict mapping each algorithm name to a statistics dict:
        algorithm       : str   — algorithm name
        n_trials        : int   — total number of trials
        n_successful    : int   — trials that found a valid path
        success_rate    : float — n_successful / n_trials
        best_path_len   : int   — shortest path found across all trials (-1 if none)
        avg_path_len    : float — mean path length of successful trials (-1 if none)
        std_path_len    : float — std-dev of path lengths  (0 if ≤1 success)
        avg_exec_time   : float — mean execution time (seconds)
        min_exec_time   : float — fastest trial
        max_exec_time   : float — slowest trial

    NOTE: We do NOT declare any algorithm "best" — that is for the user to
    interpret based on their grid and parameter configuration.
    """
    summary = {}

    for algo, results in trials_by_algorithm.items():
        successful = [r for r in results if r.get("success", False)]
        lengths    = [r["path_length"] for r in successful]
        times      = [r["execution_time"] for r in results]

        summary[algo] = {
            "algorithm":     algo,
            "n_trials":      len(results),
            "n_successful":  len(successful),
            "success_rate":  round(len(successful) / len(results), 3) if results else 0.0,
            "best_path_len": min(lengths)  if lengths else -1,
            "avg_path_len":  round(statistics.mean(lengths), 2)  if lengths else -1,
            "std_path_len":  round(statistics.stdev(lengths), 2) if len(lengths) > 1 else 0.0,
            "avg_exec_time": round(statistics.mean(times), 4) if times else 0.0,
            "min_exec_time": round(min(times), 4)             if times else 0.0,
            "max_exec_time": round(max(times), 4)             if times else 0.0,
        }

    return summary


def print_comparison_table(summary: Dict[str, dict]):
    """Pretty-print the statistics as a comparison table."""
    col = 74
    print("\n" + "=" * col)
    print("  PATHWISE — ALGORITHM COMPARISON RESULTS")
    print("=" * col)
    print(f"  {'Algo':<6} {'Success':>8} {'BestLen':>8} {'AvgLen':>8} "
          f"{'Std':>6} {'AvgTime(s)':>11} {'Trials':>7}")
    print("-" * col)

    for algo, s in summary.items():
        sr  = f"{s['success_rate']*100:.0f}%"
        bl  = str(s['best_path_len']) if s['best_path_len'] != -1 else "N/A"
        al  = str(s['avg_path_len'])  if s['avg_path_len']  != -1 else "N/A"
        std = str(s['std_path_len'])
        t   = f"{s['avg_exec_time']:.4f}"
        n   = str(s['n_trials'])
        print(f"  {algo:<6} {sr:>8} {bl:>8} {al:>8} {std:>6} {t:>11} {n:>7}")

    print("=" * col)
    print("  NOTE: A* is deterministic — path length is always optimal.")
    print("        ACO / GA / PSO are stochastic — results vary per run.")
    print()
