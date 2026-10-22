// src/components/Navbar.jsx — Responsive, animated navbar
import React from "react";

const pages = [
  { id: "planner",  label: "Path Planner" },
  { id: "compare",  label: "Compare" },
  { id: "analysis", label: "Analysis" },
];

const STATUS_LABEL = {
  ok:       { text: "Online",     color: "#16a34a" },
  offline:  { text: "Offline",    color: "#dc2626" },
  checking: { text: "Connecting", color: "#d97706" },
};

export default function Navbar({ page, setPage, backendStatus }) {
  const s = STATUS_LABEL[backendStatus] || STATUS_LABEL.checking;

  return (
    <nav className="navbar">
      {/* Left: Logo */}
      <div className="navbar-logo">
        <div className="navbar-logo-icon">
          <span style={{ color: "#fff", fontWeight: 900, fontSize: 17, fontFamily: "Inter, sans-serif" }}>P</span>
        </div>
        <div style={{ fontWeight: 800, fontSize: 18, color: "#1e293b", letterSpacing: "-0.02em", whiteSpace: "nowrap" }}>
          PathWise
        </div>
      </div>

      {/* Center: Nav links */}
      <div className="navbar-links">
        {pages.map(p => (
          <button
            key={p.id}
            onClick={() => setPage(p.id)}
            className={`navbar-link${page === p.id ? " active" : ""}`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Right: Backend status */}
      <div className="navbar-status">
        <span className={`status-dot ${backendStatus}`} />
        <span style={{ color: s.color, fontWeight: 600, fontSize: 12 }}>{s.text}</span>
      </div>
    </nav>
  );
}