# visualization/data_formatter.py
# ---------------------------------
# Formats PathWise results and grid data for the React + FastAPI frontend.
#
# All output is plain Python dicts / lists (fully JSON-serialisable).
# No numpy arrays, no tuples — only Python primitives.

import numpy as np
from typing import List, Optional
from environment.grid import GridEnvironment


def format_for_ui(grid_env: GridEnvironment, result: dict) -> dict:
    """
    Bundle a grid environment and a single algorithm result into one
    complete UI-ready payload.

    Returned schema:
    {
      "grid"       : GridEnvironment.to_dict(),
      "result"     : algorithm result (without pheromone_matrix and grid_info),
      "path_cells" : [[row, col], ...]  — cells in the best path,
      "pheromone"  : normalised pheromone heatmap dict  (ACO only, else null),
      "convergence": [{"x": iter_index, "y": path_length}, ...]
    }
    """
    pheromone_data = None
    if result.get("pheromone_matrix") is not None:
        pheromone_data = format_pheromone(result["pheromone_matrix"])

    return {
        "grid":        grid_env.to_dict(),
        "result":      {k: v for k, v in result.items()
                        if k not in ("pheromone_matrix", "grid_info")},
        "path_cells":  result.get("path", []),
        "pheromone":   pheromone_data,
        "convergence": format_convergence(result.get("convergence", [])),
    }


def format_pheromone(pheromone_matrix: List[List[float]]) -> dict:
    """
    Normalise the ACO pheromone matrix to [0, 1] for UI heatmap rendering.

    Returns:
    {
      "matrix"  : [[float, ...], ...],   # 2-D, values in [0, 1]
      "min_raw" : float,                 # original minimum pheromone
      "max_raw" : float                  # original maximum pheromone
    }
    """
    mat     = np.array(pheromone_matrix, dtype=float)
    min_val = float(mat.min())
    max_val = float(mat.max())
    rng     = max_val - min_val

    if rng < 1e-10:
        normalised = mat.tolist()
    else:
        normalised = ((mat - min_val) / rng).tolist()

    return {
        "matrix":   normalised,
        "min_raw":  round(min_val, 6),
        "max_raw":  round(max_val, 6),
    }


def format_convergence(convergence: List[float]) -> List[dict]:
    """
    Convert a convergence list (path length after each iteration) to
    chart-ready [{x, y}] format, skipping -1 entries (no valid path yet).

    Returns:
    [{"x": iteration_index, "y": path_length}, ...]
    """
    return [
        {"x": i, "y": v}
        for i, v in enumerate(convergence)
        if v != -1
    ]


def format_multi_result(grid_env: GridEnvironment, results: List[dict]) -> dict:
    """
    Format results from multiple algorithms into a single comparison payload
    for the React dashboard.

    Returns:
    {
      "grid"      : GridEnvironment.to_dict(),
      "algorithms": {
          "ACO": format_for_ui(...),
          "GA" : format_for_ui(...),
          "PSO": format_for_ui(...),
          "A*" : format_for_ui(...)
      }
    }
    """
    return {
        "grid": grid_env.to_dict(),
        "algorithms": {
            r["algorithm"]: format_for_ui(grid_env, r)
            for r in results
        }
    }
