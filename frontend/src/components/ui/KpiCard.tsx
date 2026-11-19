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
  accent = "green",
  icon: Icon,
  className,
}: KpiCardProps) {
  const accentBorder = {
    green: "border-l-4 border-l-[#246B45]",
    blue: "border-l-4 border-l-[#003399]",
    amber: "border-l-4 border-l-[#D9A441]",
    slate: "border-l-4 border-l-[#CBDAD0]",
  }[accent];

  const displayValue = value === null || value === undefined ? "—" : value;

  return (
    <div
      className={clsx(
        "bg-[#FFFFFF] border border-[#E2EAE3] p-4 rounded-xl shadow-[0_1px_3px_rgba(38,51,43,0.04)] flex flex-col justify-between transition-all hover:border-[#CBDAD0]",
        accentBorder,
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold text-[#718078] uppercase tracking-wider font-mono">
          {label}
        </span>
        {Icon && <Icon className="w-4 h-4 text-[#718078]" />}
      </div>

      <div className="mt-2.5 flex items-baseline justify-between">
        <span className="text-2xl font-black font-mono text-[#26332B] tracking-tight">
          {displayValue}
        </span>
        {trendValue && (
          <span
            className={clsx(
              "text-xs font-mono font-bold flex items-center space-x-0.5",
              trend === "up"
                ? "text-[#246B45]"
                : trend === "down"
                ? "text-[#C65B56]"
                : "text-[#718078]"
            )}
          >
            <span>{trend === "up" ? "▲" : trend === "down" ? "▼" : "•"}</span>
            <span>{trendValue}</span>
          </span>
        )}
      </div>

      {subtext && (
        <p className="mt-1 text-[11px] text-[#718078] font-medium truncate">{subtext}</p>
      )}
    </div>
  );
}
