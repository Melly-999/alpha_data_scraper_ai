import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Dashboard", path: "/terminal", icon: "D" },
  { label: "Global Markets", path: "/markets", icon: "M" },
  { label: "Watchlist", path: "/watchlist", icon: "W" },
  { label: "AI Workspace", path: "/workspace", icon: "AI" },
  { label: "Paper Run Preview", path: "/terminal/paper-run-preview", icon: "PR" },
  { label: "Open Design Tabs", path: "/terminal/open-design-tabs", icon: "OD" },
  { label: "Signals Feed", path: "/signals", icon: "S" },
  { label: "Risk Manager", path: "/risk", icon: "R" },
  { label: "Brokers", path: "/brokers", icon: "B" },
  { label: "Portfolio", path: "/portfolio", icon: "P" },
  { label: "Audit & Events", path: "/audit", icon: "A" },
  { label: "Settings", path: "/settings", icon: "G" },
];

export function LeftSidebar() {
  return (
    <aside className="terminal-sidebar">
      <div className="sidebar-section">
        <p className="terminal-eyebrow">Workspace</p>
        <nav className="terminal-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => (isActive ? "active" : undefined)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="sidebar-section compact-metrics">
        <p className="terminal-eyebrow">Execution</p>
        <div>
          <span>Orders</span>
          <strong>Denied</strong>
        </div>
        <div>
          <span>Live orders</span>
          <strong>Blocked</strong>
        </div>
        <div>
          <span>Mode</span>
          <strong>Paper RO</strong>
        </div>
      </div>
    </aside>
  );
}
