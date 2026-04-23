import type { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  tone?: "default" | "danger";
}

export function Button({ children, tone = "default", ...rest }: ButtonProps) {
  return (
    <button className={`button button-${tone}`} {...rest}>
      {children}
    </button>
  );
}

