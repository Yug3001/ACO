# api.py
# -------
# PathWise FastAPI backend
# Exposes REST endpoints that the React UI consumes.
#
# Endpoints:
#   GET  /api/health          -- health check
#   POST /api/run             -- run one algorithm
#   POST /api/compare         -- run all four algorithms on the same grid
#   POST /api/trials          -- run stochastic algorithms N times and get stats

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import traceback

from environment.grid import GridEnvironment
from algorithms.aco   import run_aco
from algorithms.genetic_algorithm import run_ga
from algorithms.pso   import run_pso
from algorithms.astar import run_astar
from comparison.runner  import run_trials
from comparison.metrics import compute_statistics

# ------------------------------------------------------------------ #
#  App setup                                                          #
# ------------------------------------------------------------------ #

app = FastAPI(
    title="PathWise API",
    description="Interactive Path Planning using Soft Computing Algorithms",
    version="1.0.0"
)

# Allow all origins so the React dev server can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------ #
#  Pydantic models                                                    #
# ------------------------------------------------------------------ #

class RunRequest(BaseModel):
    algorithm: str = Field(..., description="ACO | GA | PSO | A*")
    grid: List[List[str]] = Field(..., description="2D grid of symbols (S/F/E/O)")
    start: List[int] = Field(..., description="[row, col] of start cell")
    goal:  List[int] = Field(..., description="[row, col] of goal cell")
    allow_diagonal: bool = Field(True, description="8-dir movement if True")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class CompareRequest(BaseModel):
    grid: List[List[str]]
    start: List[int]
    goal:  List[int]
    allow_diagonal: bool = True
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TrialsRequest(BaseModel):
    grid: List[List[str]]
    start: List[int]
    goal:  List[int]
    allow_diagonal: bool = True
    n_trials: int = Field(3, ge=1, le=20)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

# ------------------------------------------------------------------ #
#  Helper: build GridEnvironment from request                        #
# ------------------------------------------------------------------ #

def _build_grid(grid_data: List[List[str]],
                start: List[int],
                goal:  List[int],
                allow_diagonal: bool = True) -> GridEnvironment:
    """
    Construct a GridEnvironment from the API request data.
    Places S and F markers at the requested positions before passing
    to GridEnvironment so it can find start and goal automatically.
    """
    # Deep-copy the grid and set S / F
    g = [list(row) for row in grid_data]
    sr, sc = start
    gr, gc = goal

    # Clear old S/F in case the client already set them (avoid duplicates)
    for r in range(len(g)):
        for c in range(len(g[r])):
            if g[r][c] in ('S', 'F', 'G'):
                g[r][c] = 'E'

    g[sr][sc] = 'S'
    g[gr][gc] = 'F'

    env = GridEnvironment(grid_array=g, allow_diagonal=allow_diagonal)
    return env


def _extract_params(parameters: dict, algo: str) -> dict:
    """Extract and type-cast algorithm-specific parameters from the request."""
    p = parameters or {}

    if algo == "ACO":
        return {
            "n_ants":       int(p.get("ants",        20)),
            "n_iterations": int(p.get("iterations",  100)),
            "alpha":      float(p.get("alpha",        1.0)),
            "beta":       float(p.get("beta",         2.0)),
            "rho":        float(p.get("evaporation",  0.5)),
            "Q":          float(p.get("Q",            100.0)),
            "Q_elite":    float(p.get("Q_elite",      200.0)),
        }
    elif algo == "GA":
        return {
            "population_size": int(p.get("population",    50)),
            "n_generations":   int(p.get("generations",   100)),
            "mutation_rate": float(p.get("mutation_rate", 0.2)),
            "crossover_rate":float(p.get("crossover_rate",0.8)),
            "elitism_count":   int(p.get("elitism",       2)),
            "tournament_size": int(p.get("tournament",    3)),
        }
    elif algo == "PSO":
        return {
            "n_particles":  int(p.get("particles",   30)),
            "n_iterations": int(p.get("iterations",  100)),
            "w":          float(p.get("inertia",      0.5)),
            "c1":         float(p.get("cognitive",    1.5)),
            "c2":         float(p.get("social",       1.5)),
        }
    else:  # A*
        return {}

# ------------------------------------------------------------------ #
#  Endpoints                                                          #
# ------------------------------------------------------------------ #

@app.get("/api/health")
def health():
    """Health check — returns OK if the backend is running."""
    return {"status": "ok", "message": "PathWise backend is running"}


@app.post("/api/run")
def run_algorithm(req: RunRequest):
    """
    Run ONE selected algorithm on the provided grid.

    Request body:
        algorithm       : "ACO" | "GA" | "PSO" | "A*"
        grid            : 2D array of symbols
        start           : [row, col]
        goal            : [row, col]
        allow_diagonal  : bool (default true)
        parameters      : algorithm-specific params dict

    Returns the standard PathWise result dict.
    """
    algo = req.algorithm.upper().strip()
    if algo not in ("ACO", "GA", "PSO", "A*", "ASTAR"):
        raise HTTPException(400, f"Unknown algorithm: {req.algorithm}")
    if algo == "ASTAR":
        algo = "A*"

    try:
        grid   = _build_grid(req.grid, req.start, req.goal, req.allow_diagonal)
        params = _extract_params(req.parameters or {}, algo)

        if algo == "ACO":
            result = run_aco(grid, **params)
        elif algo == "GA":
            result = run_ga(grid, **params)
        elif algo == "PSO":
            result = run_pso(grid, **params)
        else:  # A*
            result = run_astar(grid)

        # Remove numpy types — ensure plain Python serialisable result
        result["grid_info"] = grid.to_dict()
        return result

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(500, f"Algorithm error: {str(exc)}")


@app.post("/api/compare")
def compare_all(req: CompareRequest):
    """
    Run ALL four algorithms on the same grid and return their results.

    Returns:
        {
          "results": [aco_result, ga_result, pso_result, astar_result],
          "grid_info": { ... }
        }
    """
    try:
        grid = _build_grid(req.grid, req.start, req.goal, req.allow_diagonal)
        p    = req.parameters or {}

        results = [
            run_aco(grid,   **_extract_params(p, "ACO")),
            run_ga(grid,    **_extract_params(p, "GA")),
            run_pso(grid,   **_extract_params(p, "PSO")),
            run_astar(grid),
        ]

        for r in results:
            r.pop("pheromone_matrix", None)  # keep payload small for compare
            r.pop("grid_info", None)

        return {
            "results":   results,
            "grid_info": grid.to_dict()
        }

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(500, f"Comparison error: {str(exc)}")


@app.post("/api/trials")
def run_multiple_trials(req: TrialsRequest):
    """
    Run stochastic algorithms (ACO, GA, PSO) n_trials times and return stats.
    A* is run once (deterministic).

    Returns:
        {
          "statistics": { "ACO": {...}, "GA": {...}, "PSO": {...}, "A*": {...} },
          "all_results": { "ACO": [...], ... }
        }
    """
    try:
        grid   = _build_grid(req.grid, req.start, req.goal, req.allow_diagonal)
        p      = req.parameters or {}
        config = {
            "aco": _extract_params(p, "ACO"),
            "ga":  _extract_params(p, "GA"),
            "pso": _extract_params(p, "PSO"),
        }

        trials = run_trials(grid, config=config, n_trials=req.n_trials)
        stats  = compute_statistics(trials)

        # Strip pheromone matrices for bandwidth
        for algo_list in trials.values():
            for r in algo_list:
                r.pop("pheromone_matrix", None)
                r.pop("grid_info", None)

        return {
            "statistics":  stats,
            "all_results": trials
        }

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(500, f"Trials error: {str(exc)}")
