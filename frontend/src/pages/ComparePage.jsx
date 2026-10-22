// src/pages/ComparePage.jsx
// -------------------------
// Runs all four algorithms on the same grid and shows a comparison.
import React, { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import Grid from "../components/Grid.jsx";
import { compareAll } from "../api.js";

const COLORS = { ACO: "#6c63ff", GA: "#00d4aa", PSO: "#ffb347", "A*": "#ff5757" };
const ALGOS  = ["ACO", "GA", "PSO", "A*"];

export default function ComparePage({ sharedGrid }) {
  const [running, setRunning]   = useState(false);
  const [results, setResults]   = useState([]);
  const [error, setError]       = useState(null);
  const [viewAlgo, setViewAlgo] = useState(null);

  const validate = () => {
    if (!sharedGrid?.grid)  return "No grid found. Configure a grid on the Path Planner page first.";
    if (!sharedGrid?.start) return "No Start cell set. Go to Path Planner and place a Start.";
    if (!sharedGrid?.goal)  return "No Goal cell set. Go to Path Planner and place a Goal.";
    return null;
  };

  const handleCompare = async () => {
    const err = validate();
    if (err) { setError(err); return; }
    setError(null);
    setRunning(true);
    setResults([]);
    setViewAlgo(null);
    try {
      const data = await compareAll(sharedGrid.grid, sharedGrid.start, sharedGrid.goal, true, {});
      setResults(data.results || []);
    } catch (e) {
      setError(
        e.message.includes("fetch") || e.message.includes("connect")
          ? "Unable to connect to the backend. Make sure uvicorn is running."
          : e.message || "Comparison failed."
      );
    } finally {
      setRunning(false);
    }
  };

  const activeResult = viewAlgo ? results.find(r => r.algorithm === viewAlgo) : null;

  const pathLenData = ALGOS.map(a => {
    const r = results.find(x => x.algorithm === a);
    return { name: a, value: r?.success ? r.path_length : 0, fill: COLORS[a] };
  });

  const timeData = ALGOS.map(a => {
    const r = results.find(x => x.algorithm === a);
    return { name: a, value: r ? r.execution_time : 0, fill: COLORS[a] };
  });

  const cellSize = sharedGrid?.grid
    ? Math.max(22, Math.min(44, Math.floor(400 / Math.max(sharedGrid.grid.length, sharedGrid.grid[0]?.length || 1))))
    : 36;

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ fontWeight: 800, fontSize: 22, marginBottom: 3 }}>Compare Algorithms</h2>
      <p style={{ color: "#64748b", marginBottom: 20, fontSize: 13 }}>
        Run all four algorithms on the same environment. Results are measured from actual execution — not simulated.
      </p>

      <div style={{ display: "flex", gap: 20, flexWrap: "wrap", alignItems: "flex-start" }}>

        {/* LEFT — Grid preview */}
        <div style={{ flex: "0 0 auto" }}>
          {sharedGrid?.grid ? (
            <>
              <Grid
                grid={sharedGrid.grid}
                path={activeResult?.path || []}
                start={sharedGrid.start}
                goal={sharedGrid.goal}
                onCellClick={() => {}}
                cellSize={cellSize}
              />
              {results.length > 0 && (
                <div style={{ display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" }}>
                  {ALGOS.map(a => {
                    const r = results.find(x => x.algorithm === a);
                    if (!r) return null;
                    const active = viewAlgo === a;
                    return (
                      <button
                        key={a}
                        onClick={() => setViewAlgo(active ? null : a)}
                        style={{
                          padding: "6px 12px", borderRadius: 7, fontSize: 12, fontWeight: 700,
                          background: active ? COLORS[a] : "transparent",
                          border: `1.5px solid ${COLORS[a]}`,
                          color: active ? "#fff" : COLORS[a],
                          opacity: r.success ? 1 : 0.4, cursor: "pointer",
                        }}
                      >
                        {r.success ? "View " : "No path "}{a}
                      </button>
                    );
                  })}
                </div>
              )}
            </>
          ) : (
            <div className="card" style={{ padding: 40, textAlign: "center", color: "#64748b", maxWidth: 320 }}>
              <p style={{ fontSize: 28, marginBottom: 10 }}>Grid</p>
              <p>Set up a grid on the <strong>Path Planner</strong> page first, then come back here.</p>
            </div>
          )}
        </div>

        {/* RIGHT — Controls + table + charts */}
        <div style={{ flex: 1, minWidth: 300 }}>
          <button
            className="btn-primary"
            onClick={handleCompare}
            disabled={running}
            style={{
              width: "100%", padding: "14px 0", fontSize: 15, fontWeight: 800,
              borderRadius: 9, marginBottom: 16,
            }}
          >
            {running ? "Running all algorithms..." : "Run Comparison"}
          </button>

          {error && (
            <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: "10px 14px", marginBottom: 14, fontSize: 13, color: "#ef4444" }}>
              {error}
            </div>
          )}

          {results.length > 0 && (
            <>
              {/* Results table */}
              <div className="card" style={{ marginBottom: 14 }}>
                <div className="section-title">Results</div>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid #dde3ec" }}>
                      {["Algorithm","Path Length","Time (s)","Iterations","Status"].map(h => (
                        <th key={h} style={{ padding: "8px 10px", textAlign: "left", fontSize: 12, color: "#64748b", fontWeight: 600 }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.map(r => (
                      <tr key={r.algorithm} style={{ borderBottom: "1px solid #f1f5f9" }}>
                        <td style={{ padding: "9px 10px", fontWeight: 700, color: COLORS[r.algorithm] }}>{r.algorithm}</td>
                        <td style={{ padding: "9px 10px" }}>{r.success ? r.path_length : "—"}</td>
                        <td style={{ padding: "9px 10px" }}>{r.execution_time}</td>
                        <td style={{ padding: "9px 10px" }}>{r.iterations}</td>
                        <td style={{ padding: "9px 10px" }}>
                          <span className={r.success ? "tag tag-success" : "tag tag-danger"}>
                            {r.success ? "Found" : "Failed"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p style={{ marginTop: 10, fontSize: 11, color: "#64748b", fontStyle: "italic" }}>
                  ACO, GA, PSO are stochastic — results vary between runs. A* always returns the optimal path.
                </p>
              </div>

              {/* Path Length chart */}
              <div className="card" style={{ marginBottom: 14 }}>
                <div className="section-title">Path Length (cells)</div>
                <ResponsiveContainer width="100%" height={170}>
                  <BarChart data={pathLenData} margin={{ top: 6, right: 10, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} />
                    <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip contentStyle={{ background: "#fff", border: "1px solid #dde3ec", fontSize: 12, borderRadius: 6 }} />
                    <Bar dataKey="value" name="Path Length" radius={[4, 4, 0, 0]}>
                      {pathLenData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Execution Time chart */}
              <div className="card">
                <div className="section-title">Execution Time (seconds)</div>
                <ResponsiveContainer width="100%" height={170}>
                  <BarChart data={timeData} margin={{ top: 6, right: 10, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} />
                    <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip contentStyle={{ background: "#fff", border: "1px solid #dde3ec", fontSize: 12, borderRadius: 6 }} formatter={v => [`${v}s`, "Time"]} />
                    <Bar dataKey="value" name="Time (s)" radius={[4, 4, 0, 0]}>
                      {timeData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          )}

          {results.length === 0 && !running && !error && (
            <div className="card" style={{ textAlign: "center", padding: 48, color: "#64748b" }}>
              <p style={{ fontSize: 36, marginBottom: 10 }}>⚡</p>
              <p style={{ fontWeight: 700, marginBottom: 6 }}>Ready to compare</p>
              <p style={{ fontSize: 12 }}>Click <strong>Run Comparison</strong> to execute all four algorithms and see the measured results.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
