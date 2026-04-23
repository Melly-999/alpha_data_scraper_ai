import { NavLink } from "react-router-dom";

const items = [
  ["dashboard", "Dashboard"],
  ["signals", "Signals"],
  ["positions", "Positions"],
  ["blotter", "Trade Blotter"],
  ["risk", "Risk Manager"],
  ["mt5", "MT5 Bridge"],
  ["logs", "Logs"],
  ["settings", "Settings"],
] as const;

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">MT</div>
        <div>
          <div className="brand-title">MellyTrade</div>
          <div className="brand-subtitle">Phase 1 Terminal</div>
        </div>
      </div>
      <nav className="sidebar-nav">
        {items.map(([to, label]) => (
          <NavLink
            key={to}
            to={`/${to}`}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

