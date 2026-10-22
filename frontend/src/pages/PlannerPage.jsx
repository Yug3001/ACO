// src/pages/PlannerPage.jsx
// -------------------------
// Main page: interactive grid editor + algorithm selector + run + results.
import React, { useState, useCallback, useEffect } from "react";
import Grid from "../components/Grid.jsx";
import AlgorithmParams from "../components/AlgorithmParams.jsx";
import ResultCard from "../components/ResultCard.jsx";
import ConvergenceChart from "../components/ConvergenceChart.jsx";
import { useGrid } from "../hooks/useGrid.js";
import { runAlgorithm } from "../api.js";

const ALGORITHMS  = ["ACO", "GA", "PSO", "A*"];
const ALGO_COLORS = { ACO: "#6c63ff", GA: "#00d4aa", PSO: "#ffb347", "A*": "#ff5757" };
const ALGO_DESC   = {
  ACO: "Ant Colony Optimization — pheromone-guided search",
  GA:  "Genetic Algorithm — evolution-based search",
  PSO: "Particle Swarm Optimization — swarm intelligence",
  "A*": "A* Search — deterministic optimal baseline",
};

const MODES = [
  { id: "obstacle", label: "Obstacle", key: "O" },
  { id: "start",    label: "Set Start", key: "S" },
  { id: "goal",     label: "Set Goal",  key: "G" },
  { id: "erase",    label: "Erase",     key: "E" },
];

export default function PlannerPage({ setSharedGrid }) {
  const {
    rows, cols, grid, start, goal,
    resetGrid, resizeGrid,
    toggleObstacle, placeStart, placeGoal, setCell,
    addRandomObstacles, clearObstacles,
  } = useGrid(10, 10);

  const [mode, setMode]         = useState("obstacle");
  const [algorithm, setAlgo]    = useState("ACO");
  const [params, setParams]     = useState({});
  const [running, setRunning]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const [animPath, setAnimPath] = useState([]);
  const [pheromone, setPheromone] = useState(null);

  // Share grid state with Compare/Analysis pages
  useEffect(() => {
    setSharedGrid({ grid, start, goal });
  }, [grid, start, goal, setSharedGrid]);

  const handleCellClick = useCallback((r, c) => {
    if (mode === "start")    { placeStart(r, c); return; }
    if (mode === "goal")     { placeGoal(r, c);  return; }
    if (mode === "erase")    { setCell(r, c, "E"); return; }
    toggleObstacle(r, c);
  }, [mode, placeStart, placeGoal, setCell, toggleObstacle]);

  const validate = () => {
    if (!start) return "Please place a Start cell. Click [Set Start] then click a grid cell.";
    if (!goal)  return "Please place a Goal cell. Click [Set Goal] then click a grid cell.";
    if (start[0] === goal[0] && start[1] === goal[1]) return "Start and Goal cannot be the same cell.";
    return null;
  };

  useEffect(() => {
    return () => { if (window.animTimer) clearInterval(window.animTimer); };
  }, []);

  const animatePath = useCallback((fullPath) => {
    if (!fullPath || fullPath.length === 0) return;
    setAnimPath([]);
    let i = 0;
    const delay = Math.max(20, Math.min(80, 1200 / fullPath.length));
    if (window.animTimer) clearInterval(window.animTimer);
    window.animTimer = setInterval(() => {
      if (i >= fullPath.length) { clearInterval(window.animTimer); return; }
      setAnimPath(fullPath.slice(0, i + 1));
      i++;
    }, delay);
  }, []);

  const handleRun = async () => {
    const err = validate();
    if (err) { setError(err); return; }
    setError(null);
    setResult(null);
    setAnimPath([]);
    setPheromone(null);
    setRunning(true);
    try {
      const data = await runAlgorithm(algorithm, grid, start, goal, true, params);
      setResult(data);
      if (data.success && data.path?.length > 0) {
        animatePath(data.path);
      }
      if (data.pheromone_matrix) setPheromone(data.pheromone_matrix);
    } catch (e) {
      setError(
        e.message.includes("fetch") || e.message.includes("connect")
          ? "Unable to connect to the backend. Make sure the FastAPI server is running on port 8000."
          : e.message || "Algorithm execution failed."
      );
    } finally {
      setRunning(false);
    }
  };

  const convergenceData = (result?.convergence || []).map((y, x) => ({ x, y }));
  const cellSize = Math.max(22, Math.min(46, Math.floor(500 / Math.max(cols, rows))));

  return (
    <div style={{ display: "flex", gap: 20, padding: "20px 20px", alignItems: "flex-start", flexWrap: "wrap" }}>

      {/* ============ LEFT — GRID AREA ============ */}
      <div style={{ flex: "1 1 500px", minWidth: 0 }}>
        <h2 style={{ fontWeight: 800, fontSize: 22, marginBottom: 3 }}>Path Planner</h2>
        <p style={{ color: "#64748b", marginBottom: 16, fontSize: 13 }}>
          Interactive Path Planning using Soft Computing Algorithms
        </p>

        {/* Mode toolbar */}
        <div style={{ display: "flex", gap: 6, marginBottom: 10, flexWrap: "wrap", alignItems: "center" }}>
          {MODES.map(m => (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              style={{
                padding: "7px 14px", borderRadius: 7, fontWeight: 600, fontSize: 12,
                background: mode === m.id ? "#eef2ff" : "transparent",
                color:      mode === m.id ? "#4f46e5" : "#64748b",
                border:    `1.5px solid ${mode === m.id ? "#4f46e5" : "#dde3ec"}`,
                cursor: "pointer",
              }}
            >
              {m.label}
            </button>
          ))}
          <span style={{ width: 1, height: 24, background: "#dde3ec", margin: "0 4px" }} />
          <button className="btn-secondary" style={{ fontSize: 12, padding: "6px 12px" }} onClick={() => addRandomObstacles(0.22)}>Random</button>
          <button className="btn-secondary" style={{ fontSize: 12, padding: "6px 12px" }} onClick={clearObstacles}>Clear</button>
          <button className="btn-secondary" style={{ fontSize: 12, padding: "6px 12px" }} onClick={resetGrid}>Reset</button>
        </div>

        {/* Grid size selector */}
        <div style={{ display: "flex", gap: 6, marginBottom: 14, alignItems: "center" }}>
          <span style={{ fontSize: 12, color: "#64748b" }}>Grid size:</span>
          {[8, 10, 12, 15, 20].map(s => (
            <button
              key={s}
              onClick={() => { resizeGrid(s, s); setResult(null); setAnimPath([]); setPheromone(null); }}
              style={{ padding: "4px 10px", borderRadius: 6, fontSize: 11, fontWeight: 700, background: rows === s ? "#4f46e5" : "transparent", color: rows === s ? "#fff" : "#64748b", border: `1px solid ${rows === s ? "#4f46e5" : "#dde3ec"}`, cursor: "pointer" }}
            >
              {s}x{s}
            </button>
          ))}
        </div>

        {/* The grid */}
        <Grid
          grid={grid}
          path={animPath}
          start={start}
          goal={goal}
          onCellClick={handleCellClick}
          pheromone={pheromone}
          cellSize={cellSize}
        />

        {/* Convergence chart */}
        {result && convergenceData.filter(p => p.y !== -1).length > 0 && algorithm !== "A*" && (
          <ConvergenceChart convergence={convergenceData} algorithm={algorithm} color={ALGO_COLORS[algorithm]} />
        )}
      </div>

      {/* ============ RIGHT — CONTROL PANEL ============ */}
      <div style={{ flex: "0 0 270px", display: "flex", flexDirection: "column", gap: 12 }}>

        {/* Algorithm selector */}
        <div className="card">
          <div className="section-title">Select Algorithm</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 10 }}>
            {ALGORITHMS.map(a => (
              <button
                key={a}
                onClick={() => { setAlgo(a); setResult(null); setAnimPath([]); setPheromone(null); setError(null); }}
                style={{
                  padding: "10px 6px", borderRadius: 7, fontWeight: 700, fontSize: 12, cursor: "pointer",
                  background: algorithm === a ? `${ALGO_COLORS[a]}15` : "transparent",
                  color:      algorithm === a ? ALGO_COLORS[a]         : "#64748b",
                  border:    `1.5px solid ${algorithm === a ? ALGO_COLORS[a] : "#dde3ec"}`,
                }}
              >
                {a}
              </button>
            ))}
          </div>
          <p style={{ fontSize: 11, color: "#64748b", lineHeight: 1.5 }}>{ALGO_DESC[algorithm]}</p>
        </div>

        {/* Parameters */}
        <div className="card">
          <div className="section-title">Parameters</div>
          <AlgorithmParams algorithm={algorithm} params={params} onChange={setParams} />
        </div>

        {/* RUN button */}
        <button
          className="btn-primary"
          onClick={handleRun}
          disabled={running}
          style={{
            padding: "14px 0", borderRadius: 9, fontSize: 15, fontWeight: 800, width: "100%",
          }}
        >
          {running ? "Running..." : "Run Algorithm"}
        </button>

        {/* Error */}
        {error && (
          <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#ef4444", lineHeight: 1.5 }}>
            {error}
          </div>
        )}

        {/* Result card */}
        <ResultCard result={result} />

        {/* Legend */}
        <div className="card">
          <div className="section-title">Legend</div>
          {[
            { bg: "#16a34a",                  label: "Start cell" },
            { bg: "#dc2626",                  label: "Goal cell" },
            { bg: "#334155",                  label: "Obstacle" },
            { bg: "#f8fafc",                  label: "Free cell" },
            { bg: "rgba(129,140,248,0.7)",    label: "Path" },
            { bg: "rgba(217,119,6,0.6)",      label: "Pheromone (ACO only)" },
          ].map(({ bg, label }) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
              <span style={{ width: 14, height: 14, borderRadius: 3, background: bg, border: "1px solid rgba(0,0,0,0.1)", flexShrink: 0, display: "inline-block" }} />
              <span style={{ fontSize: 12, color: "#64748b" }}>{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
