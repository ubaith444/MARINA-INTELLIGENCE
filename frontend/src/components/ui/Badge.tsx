import React from "react";
import { clsx } from "clsx";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "blue" | "green" | "amber" | "rose" | "slate" | "form-w" | "form-d" | "form-l";
  size?: "sm" | "md";
  className?: string;
}

export default function Badge({
  children,
  variant = "slate",
  size = "sm",
  className,
}: BadgeProps) {
  const variantStyles = {
    blue: "bg-blue-950/80 text-blue-300 border-blue-800/60",
    green: "bg-emerald-950/80 text-emerald-300 border-emerald-800/60",
    amber: "bg-amber-950/80 text-amber-300 border-amber-800/60",
    rose: "bg-rose-950/80 text-rose-300 border-rose-800/60",
    slate: "bg-slate-900 text-slate-300 border-slate-800",
    "form-w": "bg-emerald-600/90 text-white font-bold border-emerald-500",
    "form-d": "bg-amber-600/90 text-white font-bold border-amber-500",
    "form-l": "bg-rose-600/90 text-white font-bold border-rose-500",
  }[variant];

  const sizeStyles = {
    sm: "px-2 py-0.5 text-[10px]",
    md: "px-2.5 py-1 text-xs",
  }[size];

  return (
    <span
      className={clsx(
        "inline-flex items-center justify-center font-mono rounded border uppercase tracking-wider",
        variantStyles,
        sizeStyles,
        className
      )}
    >
      {children}
    </span>
  );
}
