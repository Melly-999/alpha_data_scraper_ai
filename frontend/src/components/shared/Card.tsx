import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  right?: ReactNode;
  children: ReactNode;
}

export function Card({ title, right, children }: CardProps) {
  return (
    <section className="card">
      {title ? (
        <header className="card-header">
          <span className="card-title">{title}</span>
          {right ? <div className="card-actions">{right}</div> : null}
        </header>
      ) : null}
      <div className="card-body">{children}</div>
    </section>
  );
}
