"use client";

import React, { useState } from "react";
import Shell from "@/components/layout/Shell";
import FootballPitch from "@/components/pitch/FootballPitch";
import KpiCard from "@/components/ui/KpiCard";
import Badge from "@/components/ui/Badge";
import { Crosshair, ArrowRightLeft, Target, Shield, Compass } from "lucide-react";

export default function TacticalAnalysisPage() {
  const [fieldTilt, setFieldTilt] = useState({
    team_final_third_passes: 142,
    opponent_final_third_passes: 84,
    field_tilt_pct: 62.8,
    dominance: "HIGH",
  });

  return (
    <Shell
      title="Tactical Performance & Spatial Intelligence"
      subtitle="Pitch Analytics • Passing Networks • Shot Maps • Field Tilt (105m × 68m)"
    >
      {/* Tactical KPI Ribbon */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
        <KpiCard
          label="Field Tilt %"
          value={`${fieldTilt.field_tilt_pct}%`}
          subtext={`Territorial Dominance: ${fieldTilt.dominance}`}
          accent="green"
          icon={Compass}
        />
        <KpiCard
          label="Final 3rd Passes"
          value={fieldTilt.team_final_third_passes}
          subtext={`Opponent: ${fieldTilt.opponent_final_third_passes}`}
          accent="blue"
          icon={ArrowRightLeft}
        />
        <KpiCard
          label="Progressive Passes"
          value="48"
          subtext="≥ 10m towards goal or in box"
          accent="blue"
          icon={Crosshair}
        />
        <KpiCard
          label="Network Density"
          value="0.68"
          subtext="Strong structural connectivity"
          accent="green"
          icon={Shield}
        />
      </section>

      {/* Main Interactive Football Pitch */}
      <section className="space-y-4">
        <FootballPitch />
      </section>

      {/* Analytical Notes & Tactical Concepts Guide */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-blue-400 font-bold block mb-1">FIELD TILT (TERRITORIAL DOMINANCE)</span>
          <p className="text-slate-400 font-sans leading-relaxed text-[11px]">
            Measures the percentage of final third passes completed by Chennaiyin FC compared to
            the opponent. A ratio above 60% indicates proactive territorial pressure and game control.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-emerald-400 font-bold block mb-1">PROGRESSIVE PASSING</span>
          <p className="text-slate-400 font-sans leading-relaxed text-[11px]">
            Under Opta / Wyscout standards, a pass must originate outside the defensive 40% (x ≥ 42m)
            and advance the ball at least 10 meters closer to the opponent goal center or penetrate
            the 18-yard box.
          </p>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
          <span className="text-amber-400 font-bold block mb-1">PASSING NETWORK EDGES</span>
          <p className="text-slate-400 font-sans leading-relaxed text-[11px]">
            Node positions represent the median on-ball coordinates for each player. Line thickness
            scales directly with combination frequency (minimum 5 passes to appear as a connection).
          </p>
        </div>
      </section>
    </Shell>
  );
}
