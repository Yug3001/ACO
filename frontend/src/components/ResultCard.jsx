// src/components/ResultCard.jsx
import React from "react";

export default function ResultCard({ result }) {
  if (!result) return null;
  const ok = result.success;
  const rows = [
    ["Algorithm", result.algorithm],
    ["Status", ok ? "Path Found" : "No Path Found"],
    ok ? ["Path Length", result.path_length + " cells"] : null,
    ["Exec Time", result.execution_time + " s"],
    ["Iterations", result.iterations],
    result.pheromone_matrix ? ["Pheromone Map", "Available"] : null,
  ].filter(Boolean);

  return (
    <div className="card" style={{ marginTop: 4 }}>
      <div className="section-title">Result</div>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <tbody>
          {rows.map(([label, value], i) => (
            <tr key={i} style={{ borderBottom: "1px solid #f1f5f9" }}>
              <td style={{ padding: "7px 0", color: "#64748b", width: "55%" }}>{label}</td>
              <td style={{ padding: "7px 0", textAlign: "right", fontWeight: label === "Status" ? 700 : 400 }}>
                {label === "Status" ? (
                  <span style={{
                    padding: "2px 10px", borderRadius: 12, fontSize: 11, fontWeight: 700,
                    background: ok ? "rgba(76,175,128,0.15)" : "rgba(255,87,87,0.15)",
                    color: ok ? "#15803d" : "#b91c1c",
                  }}>{value}</span>
                ) : value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}