// src/components/Grid.jsx — Responsive grid with touch + animation support
import React, { useRef, useCallback } from "react";

function cellColor(cell, isPath, isStart, isGoal, phVal) {
  if (isStart) return { bg: "linear-gradient(135deg,#16a34a,#15803d)", border: "#15803d", label: "S", labelColor: "#fff", glow: "0 0 8px rgba(22,163,74,0.6)" };
  if (isGoal)  return { bg: "linear-gradient(135deg,#dc2626,#b91c1c)", border: "#b91c1c", label: "G", labelColor: "#fff", glow: "0 0 8px rgba(220,38,38,0.6)" };
  if (cell === "O") return { bg: "linear-gradient(135deg,#334155,#1e293b)", border: "#1e293b", label: "", labelColor: "", glow: "none" };
  if (isPath)  return { bg: "linear-gradient(135deg,#818cf8,#6366f1)", border: "#6366f1", label: "", labelColor: "", glow: "0 0 6px rgba(99,102,241,0.5)" };
  if (phVal > 0.08) {
    const a = Math.min(phVal * 0.7, 0.8).toFixed(2);
    return { bg: `rgba(217,119,6,${a})`, border: "#f59e0b", label: "", labelColor: "", glow: "none" };
  }
  return { bg: "#f8fafc", border: "#e2e8f0", label: "", labelColor: "", glow: "none" };
}

export default function Grid({ grid, path = [], start, goal, onCellClick, pheromone = null, cellSize = 40 }) {
  const dragging = useRef(false);
  const rows = grid ? grid.length : 0;
  const cols = rows > 0 ? grid[0].length : 0;

  const pathSet = new Set();
  if (Array.isArray(path)) {
    path.forEach(p => { if (Array.isArray(p) && p.length === 2) pathSet.add(`${p[0]},${p[1]}`); });
  }

  const handleMouse = useCallback((e, r, c) => {
    if (e.type === "mousedown") { dragging.current = true; onCellClick(r, c); }
    if (e.type === "mouseup")   { dragging.current = false; }
    if (e.type === "mousemove" && dragging.current) onCellClick(r, c);
  }, [onCellClick]);

  // Touch support for mobile
  const handleTouch = useCallback((e, r, c) => {
    e.preventDefault();
    if (e.type === "touchstart") { dragging.current = true; onCellClick(r, c); }
    if (e.type === "touchend")   { dragging.current = false; }
    if (e.type === "touchmove") {
      const touch = e.touches[0];
      const el = document.elementFromPoint(touch.clientX, touch.clientY);
      if (el?.dataset?.row && el?.dataset?.col) {
        onCellClick(Number(el.dataset.row), Number(el.dataset.col));
      }
    }
  }, [onCellClick]);

  if (!rows) return <div style={{ color: "#94a3b8", padding: 20 }}>Empty grid</div>;

  return (
    <div className="grid-scroll-wrapper">
      <div
        style={{
          display: "inline-grid",
          gridTemplateColumns: `repeat(${cols}, ${cellSize}px)`,
          gap: 2,
          background: "linear-gradient(135deg, #e2e8f0, #cbd5e1)",
          padding: 6,
          borderRadius: 14,
          border: "1px solid #cbd5e1",
          boxShadow: "inset 0 2px 8px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.08)",
          userSelect: "none",
        }}
        onMouseLeave={() => { dragging.current = false; }}
      >
        {grid.map((row, r) => row.map((cell, c) => {
          const key = `${r},${c}`;
          const isSt  = start && start[0] === r && start[1] === c;
          const isGl  = goal  && goal[0]  === r && goal[1]  === c;
          const isPth = pathSet.has(key) && !isSt && !isGl;
          const phVal = (pheromone && Array.isArray(pheromone[r])) ? (pheromone[r][c] ?? 0) : 0;
          const { bg, border, label, labelColor, glow } = cellColor(cell, isPth, isSt, isGl, phVal);

          return (
            <div
              key={key}
              data-row={r}
              data-col={c}
              title={`(${r},${c})`}
              style={{
                width: cellSize,
                height: cellSize,
                background: bg,
                border: `1.5px solid ${border}`,
                borderRadius: 5,
                cursor: "pointer",
                userSelect: "none",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 800,
                fontSize: Math.max(9, cellSize * 0.28),
                color: labelColor,
                transition: "background 0.12s, transform 0.1s, box-shadow 0.12s",
                boxShadow: glow,
                animation: isPth ? "pathAppear 0.15s ease both" : "none",
              }}
              onMouseDown={e => handleMouse(e, r, c)}
              onMouseMove={e => handleMouse(e, r, c)}
              onMouseUp={e => handleMouse(e, r, c)}
              onTouchStart={e => handleTouch(e, r, c)}
              onTouchMove={e => handleTouch(e, r, c)}
              onTouchEnd={e => handleTouch(e, r, c)}
            >
              {label}
            </div>
          );
        }))}
      </div>
    </div>
  );
}