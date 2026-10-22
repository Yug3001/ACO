// src/components/Navbar.jsx — Light theme navbar
import React from "react";

const pages = [
  { id: "planner",  label: "Path Planner" },
  { id: "compare",  label: "Compare" },
  { id: "analysis", label: "Analysis" },
];

export default function Navbar({ page, setPage, backendStatus }) {
  return (
    <nav style={{
      background: "#ffffff",
      borderBottom: "1px solid #dde3ec",
      padding: "0 28px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      height: 58,
      position: "sticky",
      top: 0,
      zIndex: 100,
      boxShadow: "0 1px 8px rgba(0,0,0,0.07)",
    }}>
      {/* Left: Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, width: "200px" }}>
        <div style={{ width: 32, height: 32, borderRadius: 9, background: "linear-gradient(135deg,#4f46e5,#7c3aed)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <span style={{ color: "#fff", fontWeight: 900, fontSize: 16 }}>P</span>
        </div>
        <div style={{ fontWeight: 800, fontSize: 18, color: "#1e293b", letterSpacing: "-0.02em" }}>
          PathWise
        </div>
      </div>

      {/* Center: Nav links */}
      <div style={{ display: "flex", gap: 8 }}>
        {pages.map(p => (
          <button
            key={p.id}
            onClick={() => setPage(p.id)}
            style={{
              padding: "7px 18px",
              borderRadius: 8,
              background: page === p.id ? "#eef2ff" : "transparent",
              color: page === p.id ? "#4f46e5" : "#64748b",
              fontWeight: page === p.id ? 700 : 500,
              fontSize: 14,
              border: "none",
              cursor: "pointer",
              transition: "all 0.15s",
            }}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Right: Empty spacer to center the nav links */}
      <div style={{ width: "200px" }}></div>
    </nav>
  );
}