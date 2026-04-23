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
          <span>{title}</span>
          {right}
        </header>
      ) : null}
      <div className="card-body">{children}</div>
    </section>
  );
}

