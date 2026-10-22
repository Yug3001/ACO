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
      <div style={{ padding: 40, textAlign: "center" }} className="animate-fade-in">
        <div style={{ background: "#fee2e2", border: "1px solid #fca5a5", borderRadius: 16, padding: 36, display: "inline-block", maxWidth: 480, boxShadow: "0 4px 24px rgba(220,38,38,0.12)" }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>⚠️</div>
          <h2 style={{ color: "#b91c1c", marginBottom: 10 }}>Something went wrong</h2>
          <p style={{ color: "#7f1d1d", marginBottom: 20, fontSize: 13 }}>{this.state.error.message}</p>
          <button
            onClick={() => this.setState({ error: null })}
            style={{ background: "linear-gradient(135deg,#dc2626,#b91c1c)", color: "#fff", border: "none", borderRadius: 10, padding: "10px 28px", cursor: "pointer", fontWeight: 700, fontSize: 14 }}
          >
            Try Again
          </button>
        </div>
      </div>
    );
    return this.props.children;
  }
}

// ── Backend Banner ───────────────────────────────────────────────────────────
function BackendBanner({ status }) {
  if (status === "ok") return null;

  if (status === "checking") return (
    <div className="backend-banner checking">
      <span className="status-dot checking" />
      <span style={{ fontWeight: 600 }}>Connecting to backend…</span>
      <span style={{ color: "#a16207", fontSize: 12 }}>Please wait a moment.</span>
    </div>
  );

  // offline
  return (
    <div className="backend-banner offline">
      <span className="status-dot offline" />
      <span style={{ fontWeight: 700 }}>⚠ Backend offline.</span>
      <span style={{ color: "#a16207", fontSize: 12 }}>
        The server may be waking up (Render free tier takes ~30–60s). Retrying automatically…
      </span>
    </div>
  );
}

// ── App ─────────────────────────────────────────────────────────────────────
export default function App() {
  const [page, setPage]             = useState("planner");
  const [backendStatus, setStatus]  = useState("checking");
  const [sharedGrid, setSharedGrid] = useState({ grid: null, start: null, goal: null });

  useEffect(() => {
    let firstCheck = true;
    const check = async () => {
      try {
        await healthCheck();
        setStatus("ok");
      } catch {
        // On first check, show "checking" for a bit longer before "offline"
        if (firstCheck) {
          firstCheck = false;
          setTimeout(() => setStatus(prev => prev !== "ok" ? "offline" : "ok"), 3000);
        } else {
          setStatus("offline");
        }
      }
    };
    check();
    const id = setInterval(check, 10000);
    return () => clearInterval(id);
  }, []);

  const handleSetSharedGrid = useCallback((g) => setSharedGrid(g), []);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <Navbar page={page} setPage={setPage} backendStatus={backendStatus} />

      <BackendBanner status={backendStatus} />

      <main>
        <ErrorBoundary>
          <div className="page-enter" key={page}>
            {page === "planner"  && <PlannerPage  setSharedGrid={handleSetSharedGrid} />}
            {page === "compare"  && <ComparePage  sharedGrid={sharedGrid} />}
            {page === "analysis" && <AnalysisPage sharedGrid={sharedGrid} />}
          </div>
        </ErrorBoundary>
      </main>
    </div>
  );
}