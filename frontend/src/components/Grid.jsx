// src/components/Grid.jsx — Light theme interactive grid
import React, { useRef, useCallback } from "react";

function cellColor(cell, isPath, isStart, isGoal, phVal) {
  if (isStart) return { bg: "#16a34a", border: "#15803d", label: "S", labelColor: "#fff" };
  if (isGoal)  return { bg: "#dc2626", border: "#b91c1c", label: "G", labelColor: "#fff" };
  if (cell === "O") return { bg: "#334155", border: "#1e293b", label: "", labelColor: "" };
  if (isPath)  return { bg: "#818cf8", border: "#6366f1", label: "", labelColor: "" };
  if (phVal > 0.08) {
    const a = Math.min(phVal * 0.7, 0.8).toFixed(2);
    return { bg: `rgba(217,119,6,${a})`, border: "#f59e0b", label: "", labelColor: "" };
  }
  return { bg: "#f8fafc", border: "#e2e8f0", label: "", labelColor: "" };
}

export default function Grid({ grid, path = [], start, goal, onCellClick, pheromone = null, cellSize = 40 }) {
  const dragging = useRef(false);
  const rows = grid ? grid.length : 0;
  const cols = rows > 0 ? grid[0].length : 0;

  // Build path lookup set safely
  const pathSet = new Set();
  if (Array.isArray(path)) {
    path.forEach(p => { if (Array.isArray(p) && p.length === 2) pathSet.add(`${p[0]},${p[1]}`); });
  }

  const handleMouse = useCallback((e, r, c) => {
    if (e.type === "mousedown") { dragging.current = true; onCellClick(r, c); }
    if (e.type === "mouseup")   { dragging.current = false; }
    if (e.type === "mousemove" && dragging.current) onCellClick(r, c);
  }, [onCellClick]);

  if (!rows) return <div style={{ color: "#94a3b8", padding: 20 }}>Empty grid</div>;

  return (
    <div
      style={{ display: "inline-grid", gridTemplateColumns: `repeat(${cols}, ${cellSize}px)`, gap: 2, background: "#e2e8f0", padding: 6, borderRadius: 12, border: "1px solid #cbd5e1", boxShadow: "inset 0 2px 8px rgba(0,0,0,0.06)", userSelect: "none" }}
      onMouseLeave={() => { dragging.current = false; }}
    >
      {grid.map((row, r) => row.map((cell, c) => {
        const key = `${r},${c}`;
        const isSt  = start && start[0] === r && start[1] === c;
        const isGl  = goal  && goal[0]  === r && goal[1]  === c;
        const isPth = pathSet.has(key) && !isSt && !isGl;
        const phVal = (pheromone && Array.isArray(pheromone[r])) ? (pheromone[r][c] ?? 0) : 0;
        const { bg, border, label, labelColor } = cellColor(cell, isPth, isSt, isGl, phVal);

        return (
          <div
            key={key}
            title={`(${r},${c})`}
            style={{
              width: cellSize, height: cellSize,
              background: bg,
              border: `1.5px solid ${border}`,
              borderRadius: 4,
              cursor: "pointer",
              userSelect: "none",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 800, fontSize: Math.max(9, cellSize * 0.28),
              color: labelColor,
              transition: "background 0.1s, transform 0.08s",
              boxShadow: (isSt || isGl) ? "0 2px 8px rgba(0,0,0,0.15)" : "none",
            }}
            onMouseDown={e => handleMouse(e, r, c)}
            onMouseMove={e => handleMouse(e, r, c)}
            onMouseUp={e => handleMouse(e, r, c)}
          >
            {label}
          </div>
        );
      }))}
    </div>
  );
}