const navItems = ["Command", "Markets", "Signals", "Risk", "Broker", "Audit"];

export function LeftSidebar() {
  return (
    <aside className="terminal-sidebar">
      <div className="sidebar-section">
        <p className="terminal-eyebrow">Workspace</p>
        <nav className="terminal-nav">
          {navItems.map((item) => (
            <a key={item} href={`#${item.toLowerCase()}`}>
              {item}
            </a>
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
          <span>Live trade</span>
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
