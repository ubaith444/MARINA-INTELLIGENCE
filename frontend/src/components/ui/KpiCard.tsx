import React from "react";
import { clsx } from "clsx";

interface KpiCardProps {
  label: string;
  value: string | number | null | undefined;
  subtext?: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  accent?: "blue" | "green" | "amber" | "slate";
  icon?: React.ComponentType<{ className?: string }>;
  className?: string;
}

export default function KpiCard({
  label,
  value,
  subtext,
  trend,
  trendValue,
  accent = "blue",
  icon: Icon,
  className,
}: KpiCardProps) {
  const accentClasses = {
    blue: "border-blue-900/30 hover:border-blue-700/50 bg-slate-900/90 text-blue-400",
    green: "border-emerald-900/30 hover:border-emerald-700/50 bg-slate-900/90 text-emerald-400",
    amber: "border-amber-900/30 hover:border-amber-700/50 bg-slate-900/90 text-amber-400",
    slate: "border-slate-800 hover:border-slate-700 bg-slate-900/80 text-slate-400",
  }[accent];

  const displayValue = value === null || value === undefined ? "—" : value;

  return (
    <div
      className={clsx(
        "relative p-4 rounded-xl border transition-all duration-150 flex flex-col justify-between shadow-sm",
        accentClasses,
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          {label}
        </span>
        {Icon && <Icon className="w-4 h-4 text-slate-400" />}
      </div>

      <div className="mt-2 flex items-baseline justify-between">
        <span className="text-2xl font-bold font-mono text-slate-100 tracking-tight">
          {displayValue}
        </span>
        {trendValue && (
          <span
            className={clsx(
              "text-xs font-mono font-medium flex items-center space-x-0.5",
              trend === "up"
                ? "text-emerald-400"
                : trend === "down"
                ? "text-rose-400"
                : "text-slate-400"
            )}
          >
            <span>{trend === "up" ? "▲" : trend === "down" ? "▼" : "•"}</span>
            <span>{trendValue}</span>
          </span>
        )}
      </div>

      {subtext && (
        <p className="mt-1 text-[11px] text-slate-400 font-medium truncate">{subtext}</p>
      )}
    </div>
  );
}
