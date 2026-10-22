// src/components/ConvergenceChart.jsx
import React from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";

export default function ConvergenceChart({ convergence = [], algorithm, color = "#6c63ff" }) {
  const data = convergence.filter(pt => pt.y !== -1 && pt.y > 0);
  if (data.length === 0) return null;

  const xLabel = algorithm === "GA" ? "Generation" : "Iteration";

  return (
    <div className="card" style={{ marginTop: 14 }}>
      <div className="section-title">Convergence — {algorithm}</div>
      <p style={{ fontSize: 11, color: "#555c7a", marginBottom: 8 }}>
        Best path length per {xLabel.toLowerCase()} (lower is better)
      </p>
      <ResponsiveContainer width="100%" height={190}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis
            dataKey="x"
            tick={{ fontSize: 11, fill: "#8a8fa8" }}
            label={{ value: xLabel, position: "insideBottomRight", offset: -4, fontSize: 11, fill: "#555c7a" }}
          />
          <YAxis tick={{ fontSize: 11, fill: "#8a8fa8" }} />
          <Tooltip
            contentStyle={{ background: "#1a1d27", border: "1px solid #2a2d3e", fontSize: 12, borderRadius: 6 }}
            labelFormatter={v => `${xLabel} ${v}`}
            formatter={v => [`${v} cells`, "Best Path"]}
          />
          <Line
            type="monotone" dataKey="y"
            stroke={color} strokeWidth={2}
            dot={false} activeDot={{ r: 4, fill: color }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
