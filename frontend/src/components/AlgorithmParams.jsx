// src/components/AlgorithmParams.jsx
// -----------------------------------
// Renders the parameter inputs for the selected algorithm.
import React from "react";

function Field({ label, name, value, onChange, min, max, step = 1, help }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <label style={{ fontSize: 12, color: "#8a8fa8" }}>{label}</label>
        <span style={{ fontSize: 12, fontWeight: 700, color: "#e8eaf0" }}>{value}</span>
      </div>
      <input
        type="range"
        name={name}
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={e => onChange(name, Number(e.target.value))}
        style={{ width: "100%", accentColor: "#6c63ff", cursor: "pointer" }}
      />
      {help && <div style={{ fontSize: 11, color: "#555c7a", marginTop: 2 }}>{help}</div>}
    </div>
  );
}

export default function AlgorithmParams({ algorithm, params, onChange }) {
  const set = (k, v) => onChange({ ...params, [k]: v });

  if (algorithm === "ACO") return (
    <>
      <Field label="Number of Ants"      name="ants"        value={params.ants        ?? 20}   min={2}    max={100} onChange={set} help="More ants = broader exploration" />
      <Field label="Iterations"          name="iterations"  value={params.iterations   ?? 100}  min={10}   max={500} onChange={set} />
      <Field label="Alpha (pheromone)"   name="alpha"       value={params.alpha        ?? 1.0}  min={0.1}  max={5}   step={0.1} onChange={set} help="Higher = exploit stronger pheromone trails" />
      <Field label="Beta (heuristic)"    name="beta"        value={params.beta         ?? 2.0}  min={0.1}  max={5}   step={0.1} onChange={set} help="Higher = greedier toward goal" />
      <Field label="Evaporation Rate"    name="evaporation" value={params.evaporation  ?? 0.5}  min={0.05} max={0.95} step={0.05} onChange={set} help="How fast pheromones fade (0-1)" />
      <Field label="Q (pheromone const)" name="Q"           value={params.Q            ?? 100}  min={10}   max={500} onChange={set} />
    </>
  );

  if (algorithm === "GA") return (
    <>
      <Field label="Population Size"  name="population"    value={params.population    ?? 50}  min={10} max={200} onChange={set} />
      <Field label="Generations"      name="generations"   value={params.generations   ?? 100} min={10} max={500} onChange={set} />
      <Field label="Mutation Rate"    name="mutation_rate" value={params.mutation_rate  ?? 0.2} min={0.01} max={0.9} step={0.01} onChange={set} help="Probability of random change" />
      <Field label="Crossover Rate"   name="crossover_rate" value={params.crossover_rate ?? 0.8} min={0.1} max={1.0} step={0.05} onChange={set} help="Probability of combining two parents" />
      <Field label="Elitism Count"    name="elitism"       value={params.elitism       ?? 2}   min={1} max={10} onChange={set} help="Best N individuals always survive" />
    </>
  );

  if (algorithm === "PSO") return (
    <>
      <Field label="Particles"          name="particles"   value={params.particles  ?? 30}  min={5}   max={100} onChange={set} />
      <Field label="Iterations"         name="iterations"  value={params.iterations ?? 100} min={10}  max={500} onChange={set} />
      <Field label="Inertia (w)"        name="inertia"     value={params.inertia    ?? 0.5} min={0.1} max={1.0} step={0.05} onChange={set} help="Resistance to change direction" />
      <Field label="Cognitive (c1)"     name="cognitive"   value={params.cognitive  ?? 1.5} min={0.1} max={4.0} step={0.1} onChange={set} help="Pull toward personal best" />
      <Field label="Social (c2)"        name="social"      value={params.social     ?? 1.5} min={0.1} max={4.0} step={0.1} onChange={set} help="Pull toward global best" />
    </>
  );

  if (algorithm === "A*") return (
    <div style={{ lineHeight: 1.8, fontSize: 13, color: "#8a8fa8" }}>
      <div style={{ marginBottom: 8 }}>
        <span style={{ color: "#6c63ff", fontWeight: 700 }}>Heuristic:</span> Chebyshev distance<br />
        <span style={{ fontSize: 11 }}>h(n) = max(|dr|, |dc|) — optimal for 8-direction grids</span>
      </div>
      <div style={{ marginBottom: 8 }}>
        <span style={{ color: "#6c63ff", fontWeight: 700 }}>Movement:</span> 8-directional
      </div>
      <div style={{ background: "rgba(0,212,170,0.08)", border: "1px solid rgba(0,212,170,0.2)", borderRadius: 7, padding: "10px 12px", fontSize: 12, color: "#00d4aa" }}>
        A* is deterministic and always finds the optimal (shortest) path if one exists. No parameters needed.
      </div>
    </div>
  );

  return null;
}
