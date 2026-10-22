// src/pages/AnalysisPage.jsx
// --------------------------
// Experiment / Analysis page: run multi-trial experiments with configurable params.
import React, { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, LineChart, Line, Legend, Cell,
} from "recharts";
import { runTrials } from "../api.js";

const COLORS = { ACO: "#6c63ff", GA: "#00d4aa", PSO: "#ffb347", "A*": "#ff5757" };
const ALGOS  = ["ACO", "GA", "PSO", "A*"];

function Slider({ label, name, value, min, max, step = 1, onChange, unit = "" }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
        <label style={{ fontSize: 12, color: "#8a8fa8" }}>{label}</label>
        <span style={{ fontSize: 12, fontWeight: 700 }}>{value}{unit}</span>
      </div>
      <input
        type="range" name={name} value={value} min={min} max={max} step={step}
        onChange={e => onChange(name, Number(e.target.value))}
        style={{ width: "100%", accentColor: "#6c63ff", cursor: "pointer" }}
      />
    </div>
  );
}

function StatRow({ label, value }) {
  return (
    <tr style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
      <td style={{ padding: "8px 10px", color: "#8a8fa8", fontSize: 12 }}>{label}</td>
      <td style={{ padding: "8px 10px", fontWeight: 700, textAlign: "right" }}>{value}</td>
    </tr>
  );
}

export default function AnalysisPage({ sharedGrid }) {
  const [nTrials, setNTrials]   = useState(3);
  const [running, setRunning]   = useState(false);
  const [stats, setStats]       = useState(null);
  const [allRes, setAllRes]     = useState(null);
  const [error, setError]       = useState(null);

  const [p, setP] = useState({
    ants: 20, iterations: 80, population: 40,
    mutation_rate: 0.2, evaporation: 0.5,
    particles: 25, inertia: 0.5, cognitive: 1.5, social: 1.5,
  });
  const set = (k, v) => setP(prev => ({ ...prev, [k]: v }));

  const handleRun = async () => {
    if (!sharedGrid?.grid)  { setError("Set up a grid on the Path Planner page."); return; }
    if (!sharedGrid?.start) { setError("Place a Start cell on the Path Planner page."); return; }
    if (!sharedGrid?.goal)  { setError("Place a Goal cell on the Path Planner page."); return; }
    setError(null); setStats(null); setAllRes(null); setRunning(true);
    try {
      const data = await runTrials(
        sharedGrid.grid, sharedGrid.start, sharedGrid.goal, true, nTrials, {
          ants: p.ants, iterations: p.iterations, evaporation: p.evaporation,
          population: p.population, mutation_rate: p.mutation_rate,
          particles: p.particles, inertia: p.inertia, cognitive: p.cognitive, social: p.social,
        }
      );
      setStats(data.statistics);
      setAllRes(data.all_results);
    } catch (e) {
      setError(e.message.includes("fetch") ? "Cannot reach backend." : e.message || "Experiment failed.");
    } finally { setRunning(false); }
  };

  // Build chart data
  const barData = (key, pct = false) =>
    ALGOS.map(a => {
      if (!stats?.[a]) return { name: a, value: 0 };
      const v = stats[a][key];
      return { name: a, value: v === -1 ? 0 : pct ? +(v * 100).toFixed(1) : v };
    });

  // Build avg convergence across trials
  const buildConv = () => {
    if (!allRes) return [];
    const stochasticAlgos = ALGOS.filter(a => a !== "A*");
    const maxLen = Math.max(...stochasticAlgos.flatMap(a => (allRes[a] || []).map(r => r.convergence?.length || 0)));
    return Array.from({ length: maxLen }, (_, i) => {
      const pt = { x: i };
      stochasticAlgos.forEach(a => {
        const vals = (allRes[a] || []).map(r => r.convergence?.[i]).filter(v => v != null && v !== -1);
        if (vals.length) pt[a] = +(vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(1);
      });
      return pt;
    });
  };

  const convData = buildConv();

  return (
    <div style={{ padding: 20 }}>
      <h2 style={{ fontWeight: 800, fontSize: 22, marginBottom: 3 }}>Analysis</h2>
      <p style={{ color: "#64748b", marginBottom: 20, fontSize: 13 }}>
        Multi-trial experiments for statistical comparison. Runs on the grid from the Path Planner page.
      </p>

      <div style={{ display: "flex", gap: 20, flexWrap: "wrap", alignItems: "flex-start" }}>

        {/* LEFT — config panel */}
        <div style={{ flex: "0 0 280px" }}>
          <div className="card" style={{ marginBottom: 12 }}>
            <div className="section-title">Trials</div>
            <label style={{ fontSize: 12, color: "#64748b", marginBottom: 4, display: "block" }}>Trials per stochastic algorithm</label>
            <select value={nTrials} onChange={e => setNTrials(Number(e.target.value))}
              style={{ background: "#f8fafc", color: "#1e293b", border: "1px solid #dde3ec", borderRadius: 7, padding: "7px 12px", fontSize: 13, width: "100%", outline: "none" }}>
              {[1,2,3,5,7,10].map(n => <option key={n} value={n}>{n} trial{n>1?"s":""}</option>)}
            </select>
          </div>

          <div className="card" style={{ marginBottom: 12 }}>
            <div className="section-title">ACO Parameters</div>
            <Slider label="Ants"        name="ants"        value={p.ants}        min={5}    max={100}  onChange={set} />
            <Slider label="Iterations"  name="iterations"  value={p.iterations}  min={20}   max={300}  onChange={set} />
            <Slider label="Evaporation" name="evaporation" value={p.evaporation} min={0.05} max={0.95} step={0.05} onChange={set} />
          </div>

          <div className="card" style={{ marginBottom: 12 }}>
            <div className="section-title">GA Parameters</div>
            <Slider label="Population"    name="population"    value={p.population}    min={10}   max={200} onChange={set} />
            <Slider label="Mutation Rate" name="mutation_rate" value={p.mutation_rate} min={0.01} max={0.5} step={0.01} onChange={set} />
          </div>

          <div className="card" style={{ marginBottom: 12 }}>
            <div className="section-title">PSO Parameters</div>
            <Slider label="Particles" name="particles" value={p.particles} min={5}   max={100} onChange={set} />
            <Slider label="Inertia"   name="inertia"   value={p.inertia}   min={0.1} max={1.0} step={0.05} onChange={set} />
            <Slider label="Cognitive" name="cognitive" value={p.cognitive} min={0.1} max={4.0} step={0.1} onChange={set} />
            <Slider label="Social"    name="social"    value={p.social}    min={0.1} max={4.0} step={0.1} onChange={set} />
          </div>

          <button
            className="btn-primary"
            onClick={handleRun} disabled={running}
            style={{
              width: "100%", padding: "14px 0", fontSize: 14, fontWeight: 800, borderRadius: 9,
            }}
          >
            {running ? `Running ${nTrials} trial${nTrials>1?"s":""}...` : "Run Experiment"}
          </button>

          {error && (
            <div style={{ marginTop: 10, background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#ef4444" }}>
              {error}
            </div>
          )}
        </div>

        {/* RIGHT — results */}
        <div style={{ flex: 1, minWidth: 300 }}>
          {!stats && !running && (
            <div className="card" style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
              <p style={{ fontSize: 36, marginBottom: 10 }}>&#128202;</p>
              <p style={{ fontWeight: 700, marginBottom: 6 }}>No results yet</p>
              <p style={{ fontSize: 12 }}>Configure the experiment and click <strong>Run Experiment</strong>.</p>
            </div>
          )}

          {stats && (
            <>
              {/* Stats table */}
              <div className="card" style={{ marginBottom: 14 }}>
                <div className="section-title">Statistical Summary ({nTrials} trial{nTrials>1?"s":""})</div>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid #dde3ec" }}>
                      {["Algorithm","Success %","Best Len","Avg Len","Std","Avg Time (s)"].map(h =>
                        <th key={h} style={{ padding: "8px 10px", textAlign: "left", fontSize: 12, color: "#64748b", fontWeight: 600 }}>{h}</th>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {ALGOS.map(a => {
                      const s = stats[a]; if (!s) return null;
                      return (
                        <tr key={a} style={{ borderBottom: "1px solid #f1f5f9" }}>
                          <td style={{ padding: "9px 10px", fontWeight: 700, color: COLORS[a] }}>{a}</td>
                          <td style={{ padding: "9px 10px" }}>{(s.success_rate * 100).toFixed(0)}%</td>
                          <td style={{ padding: "9px 10px" }}>{s.best_path_len !== -1 ? s.best_path_len : "N/A"}</td>
                          <td style={{ padding: "9px 10px" }}>{s.avg_path_len  !== -1 ? s.avg_path_len  : "N/A"}</td>
                          <td style={{ padding: "9px 10px" }}>{s.std_path_len}</td>
                          <td style={{ padding: "9px 10px" }}>{s.avg_exec_time}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
                <p style={{ marginTop: 8, fontSize: 11, color: "#64748b", fontStyle: "italic" }}>
                  A* is deterministic — it runs once and is replicated for display.
                </p>
              </div>

              {/* Avg Path Length chart */}
              <div className="card" style={{ marginBottom: 14 }}>
                <div className="section-title">Average Path Length</div>
                <ResponsiveContainer width="100%" height={170}>
                  <BarChart data={barData("avg_path_len")} margin={{ top: 6, right: 10, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} />
                    <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip contentStyle={{ background: "#fff", border: "1px solid #dde3ec", fontSize: 12, borderRadius: 6 }} />
                    <Bar dataKey="value" name="Avg Path Len" radius={[4,4,0,0]}>
                      {ALGOS.map((a, i) => <Cell key={i} fill={COLORS[a]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Success Rate chart */}
              <div className="card" style={{ marginBottom: 14 }}>
                <div className="section-title">Success Rate (%)</div>
                <ResponsiveContainer width="100%" height={170}>
                  <BarChart data={barData("success_rate", true)} margin={{ top: 6, right: 10, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="name" tick={{ fontSize: 12, fill: "#64748b" }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#64748b" }} />
                    <Tooltip contentStyle={{ background: "#fff", border: "1px solid #dde3ec", fontSize: 12, borderRadius: 6 }} formatter={v => [`${v}%`, "Success"]} />
                    <Bar dataKey="value" name="Success %" radius={[4,4,0,0]}>
                      {ALGOS.map((a, i) => <Cell key={i} fill={COLORS[a]} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Convergence comparison */}
              {convData.length > 0 && (
                <div className="card">
                  <div className="section-title">Avg Convergence Comparison (ACO / GA / PSO)</div>
                  <p style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }}>Average best path length per iteration across all trials</p>
                  <ResponsiveContainer width="100%" height={220}>
                    <LineChart data={convData} margin={{ top: 6, right: 20, left: 0, bottom: 4 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="x" label={{ value: "Iteration", position: "insideBottomRight", offset: -4, fontSize: 11, fill: "#64748b" }} tick={{ fontSize: 11, fill: "#64748b" }} />
                      <YAxis tick={{ fontSize: 11, fill: "#64748b" }} />
                      <Tooltip contentStyle={{ background: "#fff", border: "1px solid #dde3ec", fontSize: 12, borderRadius: 6 }} />
                      <Legend />
                      {["ACO","GA","PSO"].map(a => (
                        <Line key={a} type="monotone" dataKey={a} stroke={COLORS[a]} strokeWidth={2} dot={false} name={a} />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
