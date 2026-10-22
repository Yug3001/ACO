/* pathwise-ui/src/api.js
 * ----------------------
 * Centralized API client for communicating with the FastAPI backend.
 * All fetch calls are here — components import from this file.
 */

// Normalize: trim spaces, drop trailing slashes, drop accidental trailing "/api"
const rawUrl = (import.meta.env.VITE_API_URL || "").trim();
const cleanedUrl = rawUrl.replace(/\/+$/, "").replace(/\/api$/, "");

// Localhost fallback only in dev. In production a missing var fails loudly.
export const BASE_URL =
  cleanedUrl || (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

if (!BASE_URL) {
  console.error("VITE_API_URL is not set in this build. Set it in Vercel and redeploy.");
}

/** Fetch with a timeout so a hung request can't stall the UI forever. */
async function fetchWithTimeout(url, options = {}, ms = 15000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

/** Check if the backend is reachable. Throws a descriptive error on failure. */
export async function healthCheck() {
  if (!BASE_URL) throw new Error("VITE_API_URL missing in build");
  let res;
  try {
    res = await fetchWithTimeout(`${BASE_URL}/api/health`);
  } catch (e) {
    throw new Error(
      e.name === "AbortError"
        ? "Timed out (server may be cold-starting)"
        : "Network/CORS error (request blocked or server down)"
    );
  }
  if (!res.ok) throw new Error(`HTTP ${res.status} from /api/health`);
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
  const res = await fetchWithTimeout(
    `${BASE_URL}/api/run`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ algorithm, grid, start, goal, allow_diagonal: diagonal, parameters }),
    },
    90000
  );
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
  const res = await fetchWithTimeout(
    `${BASE_URL}/api/compare`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grid, start, goal, allow_diagonal: diagonal, parameters }),
    },
    120000
  );
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
  const res = await fetchWithTimeout(
    `${BASE_URL}/api/trials`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ grid, start, goal, allow_diagonal: diagonal, n_trials, parameters }),
    },
    180000
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Server error" }));
    throw new Error(err.detail || "Trials failed");
  }
  return res.json();
}