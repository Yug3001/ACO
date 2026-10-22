# PathWise — Interactive Path Planning using Soft Computing Algorithms

## Overview

Build a complete, modular path-planning system on top of the existing ACO repository. The system runs ACO, GA, PSO, and A* on the same grid and exposes results in a common JSON format ready for a React + FastAPI frontend.

The existing code is **Python 2** and uses a graph-node-edge structure. We will **rewrite it cleanly in Python 3** while preserving the algorithmic spirit of the original Ant System.

---

## User Review Required

> [!IMPORTANT]
> The existing `aco/ant_colony.py` and `aco/map_class.py` are Python 2 code (uses `print` as a statement, `dtype='string'`, `np.int` which is deprecated). They cannot run on modern Python 3 without modification. The plan is to **rewrite and upgrade them to Python 3** while preserving the Ant System logic. The original files will be **kept as-is** (untouched) in the `aco/` directory for reference, and new clean implementations will live in the new `algorithms/` directory.

> [!IMPORTANT]
> The existing map format uses `S`, `F`, `E`, `O`. The new common grid will also support this format plus a new format with `S`, `G`, `.`, `X` as described in the spec. Both will be accepted by the environment module.

---

## Proposed Changes

### Component 1 — Common Environment

#### [NEW] `environment/grid.py`
- `GridEnvironment` class wrapping a 2D NumPy array
- Supports custom size, start, goal, obstacles
- Loads from `.txt` file (supports old `S/F/E/O` and new `S/G/./X` formats)
- Or constructed programmatically from a 2D list
- `get_neighbors(row, col, diagonal=False)` — returns valid free neighboring cells
- `is_valid(row, col)` — boundary + obstacle check
- `manhattan_distance(a, b)` — shared heuristic utility
- `to_dict()` — serializes grid to JSON-friendly dict for the API

#### [NEW] `environment/__init__.py`

---

### Component 2 — ACO (Ant Colony Optimization)

#### [NEW] `algorithms/aco.py`
Complete Python 3 rewrite of the Ant System, now using the common `GridEnvironment`.

Key upgrades over the original:
- **Alpha/Beta** parameters: probability uses `pheromone^α × heuristic^β` (heuristic = 1/Manhattan distance to goal)
- **Max path length** guard to prevent infinite loops (original had no limit)
- **Elitist pheromone update**: best path of each iteration gets extra pheromone
- Tracks **convergence history** (best path length per iteration)
- Exposes **pheromone matrix** as a 2D NumPy array for visualization
- Returns result in the **common result format**

Preserves from original:
- Ant class with `visited_nodes`, `actual_node`, `final_node_reached`
- `delete_loops()` post-processing
- Pheromone evaporation + deposition logic

#### [MODIFY] `aco/__init__.py`
Add a compatibility note comment. Do **not** delete or change the original `ant_colony.py` or `map_class.py`.

---

### Component 3 — Genetic Algorithm

#### [NEW] `algorithms/genetic_algorithm.py`
Path representation: a chromosome is a **sequence of (row, col) tuples** from start toward goal.

- **Initialization**: generate candidate paths using random walks + greedy bias toward goal
- **Fitness function**:
  - Heavily penalize paths that don't reach goal
  - Penalize path length (shorter = better)
  - Penalize obstacle hits and revisited cells
- **Selection**: Tournament selection (size=3)
- **Crossover**: Find a common cell in two parent paths and swap suffixes
- **Mutation**: Randomly change a segment of the path using a random walk
- **Repair**: After crossover/mutation, trim paths at obstacle hits; re-attach goal if possible
- **Elitism**: Always carry forward the top-N individuals unchanged
- Returns result in common format with convergence history

---

### Component 4 — Particle Swarm Optimization

#### [NEW] `algorithms/pso.py`
Discrete path-based PSO adaptation for grids.

**How continuous PSO maps to discrete path planning** (documented in code):
- **Particle** = a candidate path (sequence of grid cells)
- **Position** = the path sequence itself
- **Velocity** = a "mutation strength" scalar in [0,1] that controls how much the path changes per update
- **Personal best (pbest)** = shortest valid path found by this particle
- **Global best (gbest)** = shortest valid path found by any particle
- **Update rule**: New path = blend of current path influenced by pbest and gbest via crossover operations weighted by inertia (w), cognitive (c1), and social (c2) coefficients
- **Repair**: invalid paths are repaired by re-running a greedy segment from the break point
- Returns result in common format with convergence history

---

### Component 5 — A* Search

#### [NEW] `algorithms/astar.py`
Standard A* using a min-heap priority queue.
- `f(n) = g(n) + h(n)` where h = Manhattan distance
- Reconstructs path by backtracking `came_from` dict
- Returns result in common format (`iterations` = nodes expanded)

---

### Component 6 — Common Result Format

#### [NEW] `algorithms/__init__.py`
Exports `AlgorithmResult` TypedDict/dataclass defining the shared schema:
```python
{
  "algorithm": str,
  "success": bool,
  "path": List[Tuple[int,int]],
  "path_length": int,
  "execution_time": float,
  "iterations": int,
  "convergence": List[float],
  "pheromone_matrix": Optional[List[List[float]]],  # ACO only
  "grid_info": dict
}
```

---

### Component 7 — Comparison Module

#### [NEW] `comparison/runner.py`
- `run_all(grid_env, config)` — runs all 4 algorithms on the same grid
- `run_trials(grid_env, config, n_trials)` — runs stochastic algorithms multiple times
- Returns list of result dicts

#### [NEW] `comparison/metrics.py`
- `compute_statistics(results_list)` — computes best/avg path length, avg time, success rate per algorithm
- Returns a summary dict

---

### Component 8 — Visualization Data Formatter

#### [NEW] `visualization/data_formatter.py`
- `format_for_ui(grid_env, result)` — bundles grid + result into a single UI-ready payload
- `format_pheromone(pheromone_matrix)` — normalizes pheromone matrix to [0,1] for heatmap
- `format_convergence(convergence_list)` — returns chart-ready `{x, y}` pairs

---

### Component 9 — Experiment Runner

#### [NEW] `experiments/experiment_runner.py`
- Predefined experiment configs (small/medium/large grids)
- Runs comparison across multiple seeds
- Saves results to JSON files in `experiments/results/`

---

### Component 10 — Maps

#### [NEW] `maps/map_pathwise_small.txt`
A small 8×8 map with `S/G/./X` notation for testing.

#### [NEW] `maps/map_pathwise_medium.txt`
A 12×12 map for standard experiments.

---

### Component 11 — Entry Point & Config

#### [NEW] `main.py`
- CLI entry point: pick algorithm, map, parameters
- Demonstrates all 4 algorithms on a sample grid
- Prints results in table format

#### [NEW] `requirements.txt`
- `numpy`
- `scipy` (optional, for stats)
- Standard library: `heapq`, `random`, `time`, `json`, `typing`

#### [NEW] `README.md` (replace existing)
Full project README explaining all algorithms, parameters, how to run, and API contract.

---

## Verification Plan

### Automated Tests
```
python main.py
python experiments/experiment_runner.py
```

### Manual Verification
- All 4 algorithms run on the same grid without errors
- ACO, GA, PSO return `success: true` on solvable maps
- A* always finds optimal path if one exists
- Convergence histories are non-empty lists
- Pheromone matrix returned by ACO
- Common result format validated by printing JSON output
- Comparison runner collects and summarizes results from all 4 algorithms

---

## Open Questions

> [!NOTE]
> **Diagonal movement**: The original ACO used 8-directional movement. The new system defaults to 4-directional (Up/Down/Left/Right) per the spec, but has a configurable `diagonal=True` flag. Should diagonal movement be enabled by default to match the original behavior, or keep 4-directional as default?

> [!NOTE]
> **Map format**: Old maps use `S/F/E/O`. New maps use `S/G/./X`. The environment module will auto-detect and support both. The old maps in `maps/` will continue to work.
