import type { ReactNode } from "react";

interface DrawerProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
}

export function Drawer({ open, title, onClose, children }: DrawerProps) {
  return (
    <aside className={`drawer ${open ? "open" : ""}`} aria-hidden={!open}>
      <div className="drawer-header">
        <span className="drawer-title">{title}</span>
        <button type="button" className="drawer-close" onClick={onClose}>
          ×
        </button>
      </div>
      <div className="drawer-body">{children}</div>
    </aside>
  );
}
