"use client";

import React, { useEffect, useState } from "react";
import { fetchHealth } from "@/lib/api";
import { Activity, ShieldCheck, ChevronDown, CheckCircle2, AlertCircle } from "lucide-react";

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
    <header className="h-16 px-6 bg-[#FFFFFF] border-b border-[#E2EAE3] flex items-center justify-between sticky top-0 z-30 shadow-[0_1px_2px_rgba(38,51,43,0.03)]">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-sm font-bold text-[#26332B] tracking-tight">
          {title || "Chennaiyin FC Performance Intelligence"}
        </h1>
        {subtitle && <p className="text-[11px] text-[#718078] font-medium">{subtitle}</p>}
      </div>

      {/* Right Controls: Season Selector & Health Indicator */}
      <div className="flex items-center space-x-3">
        {/* Season Selector */}
        <div className="flex items-center space-x-1.5 bg-[#F4F8F4] border border-[#E2EAE3] rounded-lg px-2.5 py-1 text-xs">
          <span className="text-[#718078] font-medium text-[11px]">Season:</span>
          <select
            value={selectedSeason}
            onChange={(e) => setSelectedSeason(e.target.value)}
            className="bg-transparent text-[#26332B] font-semibold text-xs focus:outline-none cursor-pointer"
          >
            <option value="2026–27" className="bg-[#FFFFFF] text-[#26332B]">
              ISL 2026–27 (Active)
            </option>
            <option value="2025–26" className="bg-[#FFFFFF] text-[#26332B]">
              ISL 2025–26 (Archive)
            </option>
          </select>
        </div>

        {/* Backend Status Badge */}
        <div className="flex items-center space-x-2 bg-[#F4F8F4] border border-[#E2EAE3] px-3 py-1 rounded-lg text-xs font-mono">
          <span
            className={`w-2 h-2 rounded-full ${
              isBackendHealthy === true
                ? "bg-[#246B45]"
                : isBackendHealthy === false
                ? "bg-[#D9A441]"
                : "bg-[#718078] animate-pulse"
            }`}
          />
          <span className="text-[11px] font-medium text-[#26332B]">
            {isBackendHealthy === true
              ? "Verified API Feed"
              : isBackendHealthy === false
              ? "API Offline (Cached)"
              : "Connecting..."}
          </span>
        </div>
      </div>
    </header>
  );
}
