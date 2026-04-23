import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  tone?: "green" | "red" | "amber" | "blue" | "muted";
}

export function Badge({ children, tone = "muted" }: BadgeProps) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}

