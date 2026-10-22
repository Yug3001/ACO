/* pathwise-ui/src/api.js
 * ----------------------
 * Centralized API client for communicating with the FastAPI backend.
 * All fetch calls are here — components import from this file.
 */

const BASE_URL = "http://127.0.0.1:8000";

/** Check if the backend is reachable. */
export async function healthCheck() {
  const res = await fetch(`${BASE_URL}/api/health`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
}

/**
 * Run one algorithm on the given grid.
 * @param {string} algorithm  - "ACO" | "GA" | "PSO" | "A*"
 * @param {string[][]} grid   - 2D array of symbols
 * @param {number[]} start    - [row, col]
 * @param {number[]} goal     - [row, col]
 * @param {boolean} diagonal  - allow diagonal movement
 * @param {object} parameters - algorithm-specific params
 */
export async function runAlgorithm(algorithm, grid, start, goal, diagonal, parameters) {
  const res = await fetch(`${BASE_URL}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ algorithm, grid, start, goal, allow_diagonal: diagonal, parameters }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || "Algorithm failed");
  }
  return res.json();
}

/**
 * Run all four algorithms on the same grid and return all results.
 */
export async function compareAll(grid, start, goal, diagonal, parameters) {
  const res = await fetch(`${BASE_URL}/api/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid, start, goal, allow_diagonal: diagonal, parameters }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || "Comparison failed");
  }
  return res.json();
}

/**
 * Run stochastic algorithms N times and return statistics.
 */
export async function runTrials(grid, start, goal, diagonal, n_trials, parameters) {
  const res = await fetch(`${BASE_URL}/api/trials`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid, start, goal, allow_diagonal: diagonal, n_trials, parameters }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || "Trials failed");
  }
  return res.json();
}
