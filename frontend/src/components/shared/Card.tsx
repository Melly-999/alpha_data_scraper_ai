import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  right?: ReactNode;
  children: ReactNode;
}

export function Card({ title, right, children }: CardProps) {
  return (
    <section className="card card-terminal panel-glass">
      {title ? (
        <header className="card-header card-header-terminal">
          <span className="card-title">{title}</span>
          {right ? <div className="card-actions">{right}</div> : null}
        </header>
      ) : null}
      <div className="card-body">{children}</div>
    </section>
  );
}
