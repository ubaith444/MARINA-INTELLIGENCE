"use client";

import React, { useEffect, useState } from "react";
import { fetchHealth } from "@/lib/api";
import { Activity, ShieldCheck, ChevronDown, RefreshCw } from "lucide-react";

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export default function Header({ title, subtitle }: HeaderProps) {
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const [selectedSeason, setSelectedSeason] = useState("2026–27");

  useEffect(() => {
    let isMounted = true;
    fetchHealth()
      .then((data) => {
        if (isMounted) setIsBackendHealthy(data.status === "healthy");
      })
      .catch(() => {
        if (isMounted) setIsBackendHealthy(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <header className="h-16 px-6 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 flex items-center justify-between sticky top-0 z-40">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-sm font-bold text-slate-100 tracking-tight">
          {title || "Chennaiyin FC Performance Intelligence"}
        </h1>
        {subtitle && <p className="text-[11px] text-slate-400 font-medium">{subtitle}</p>}
      </div>

      {/* Right Controls: Season Selector & Health Indicator */}
      <div className="flex items-center space-x-3.5">
        {/* Season Selector */}
        <div className="flex items-center space-x-1.5 bg-slate-900 border border-slate-800 rounded-lg px-2.5 py-1 text-xs">
          <span className="text-slate-400 font-medium text-[11px]">Season:</span>
          <select
            value={selectedSeason}
            onChange={(e) => setSelectedSeason(e.target.value)}
            className="bg-transparent text-slate-200 font-semibold text-xs focus:outline-none cursor-pointer"
          >
            <option value="2026–27" className="bg-slate-900 text-slate-200">
              ISL 2026–27 (Active)
            </option>
            <option value="2025–26" className="bg-slate-900 text-slate-200">
              ISL 2025–26 (Archive)
            </option>
          </select>
        </div>

        {/* Backend Status Badge */}
        <div className="flex items-center space-x-2 bg-slate-900/90 border border-slate-800 px-3 py-1 rounded-lg text-xs font-mono">
          <span
            className={`w-2 h-2 rounded-full ${
              isBackendHealthy === true
                ? "bg-emerald-400 shadow-sm shadow-emerald-400/50"
                : isBackendHealthy === false
                ? "bg-amber-400"
                : "bg-slate-500 animate-pulse"
            }`}
          />
          <span className="text-[11px] text-slate-300">
            {isBackendHealthy === true
              ? "API Connected"
              : isBackendHealthy === false
              ? "API Offline (Mock/Demo)"
              : "Checking API..."}
          </span>
        </div>
      </div>
    </header>
  );
}
