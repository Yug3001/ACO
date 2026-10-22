// src/App.jsx — Root component with ErrorBoundary + backend health check
import React, { useState, useCallback, useEffect } from "react";
import Navbar       from "./components/Navbar.jsx";
import PlannerPage  from "./pages/PlannerPage.jsx";
import ComparePage  from "./pages/ComparePage.jsx";
import AnalysisPage from "./pages/AnalysisPage.jsx";
import { healthCheck } from "./api.js";

// ── Error Boundary ──────────────────────────────────────────────────────────
class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(err) { return { error: err }; }
  componentDidCatch(err, info) { console.error("PathWise caught error:", err, info); }
  render() {
    if (this.state.error) return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <div style={{ background: "#fee2e2", border: "1px solid #fca5a5", borderRadius: 12, padding: 32, display: "inline-block", maxWidth: 480 }}>
          <h2 style={{ color: "#b91c1c", marginBottom: 10 }}>Something went wrong</h2>
          <p style={{ color: "#7f1d1d", marginBottom: 16, fontSize: 13 }}>{this.state.error.message}</p>
          <button
            onClick={() => this.setState({ error: null })}
            style={{ background: "#dc2626", color: "#fff", border: "none", borderRadius: 8, padding: "10px 24px", cursor: "pointer", fontWeight: 700 }}
          >
            Try Again
          </button>
        </div>
      </div>
    );
    return this.props.children;
  }
}

// ── App ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [page, setPage]             = useState("planner");
  const [backendStatus, setStatus]  = useState("checking");
  const [sharedGrid, setSharedGrid] = useState({ grid: null, start: null, goal: null });

  useEffect(() => {
    const check = async () => {
      try { await healthCheck(); setStatus("ok"); }
      catch { setStatus("offline"); }
    };
    check();
    const id = setInterval(check, 8000);
    return () => clearInterval(id);
  }, []);

  const handleSetSharedGrid = useCallback((g) => setSharedGrid(g), []);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <Navbar page={page} setPage={setPage} backendStatus={backendStatus} />

      {backendStatus === "offline" && (
        <div style={{ background: "#fff7ed", borderBottom: "1px solid #fed7aa", padding: "10px 24px", fontSize: 13, color: "#92400e", display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontWeight: 700 }}>⚠ Backend offline.</span>
          Run: <code style={{ background: "#fff", border: "1px solid #fed7aa", padding: "2px 8px", borderRadius: 5, fontSize: 12 }}>cd backend &amp;&amp; uvicorn api:app --reload</code>
          in a terminal.
        </div>
      )}

      <main>
        <ErrorBoundary>
          {page === "planner"  && <PlannerPage  setSharedGrid={handleSetSharedGrid} />}
          {page === "compare"  && <ComparePage  sharedGrid={sharedGrid} />}
          {page === "analysis" && <AnalysisPage sharedGrid={sharedGrid} />}
        </ErrorBoundary>
      </main>
    </div>
  );
}