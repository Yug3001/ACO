# comparison/__init__.py
from comparison.runner  import run_all, run_trials
from comparison.metrics import compute_statistics, print_comparison_table

__all__ = ["run_all", "run_trials", "compute_statistics", "print_comparison_table"]
