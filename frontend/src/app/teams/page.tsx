"use client";

import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import KpiCard from "@/components/ui/KpiCard";
import Badge from "@/components/ui/Badge";
import LeadershipGroupSection from "@/components/team/LeadershipGroupSection";
import { fetchTeamAttacking, fetchTeamDefensive, fetchTeamPerformance, fetchTeams } from "@/lib/api";
import { AttackingAnalytics, DefensiveAnalytics, TeamSeasonPerformance } from "@/lib/types";
import {
  Shield,
  Target,
  Crosshair,
  Flame,
  AlertTriangle,
} from "lucide-react";

export default function TeamAnalysisPage() {
  const [attacking, setAttacking] = useState<AttackingAnalytics | null>(null);
  const [defensive, setDefensive] = useState<DefensiveAnalytics | null>(null);
  const [performance, setPerformance] = useState<TeamSeasonPerformance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadTeamData() {
      try {
        const teams = await fetchTeams();
        const cfc = teams.find((t) => t.slug === "chennaiyin-fc") || teams[0];
        const teamId = cfc ? cfc.id : "chennaiyin-fc";

        const [attData, defData, perfData] = await Promise.all([
          fetchTeamAttacking(teamId).catch(() => null),
          fetchTeamDefensive(teamId).catch(() => null),
          fetchTeamPerformance(teamId).catch(() => null),
        ]);

        if (!isMounted) return;
        if (attData) setAttacking(attData as AttackingAnalytics);
        if (defData) setDefensive(defData as DefensiveAnalytics);
        if (perfData) setPerformance(perfData as TeamSeasonPerformance);
        setLoading(false);
      } catch (err) {
        console.error("Failed to load team analytics:", err);
        if (isMounted) setLoading(false);
      }
    }

    loadTeamData();

    return () => {
      isMounted = false;
    };
  }, []);

  const att = attacking;
  const def = defensive;

  return (
    <Shell
      title="Team Analytics & Performance Profiles"
      subtitle="Chennaiyin FC Tactical Efficiency, Shot Quality & Defensive Resilience"
    >
      {/* Top Level Attack & Defense KPI Cards */}
      <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <KpiCard
          label="Shot Accuracy"
          value={`${att?.shooting_accuracy_pct ?? "—"}%`}
          subtext={`${att?.shots_on_target ?? 0} on target / ${att?.shots_total ?? 0}`}
          accent="blue"
          icon={Crosshair}
        />
        <KpiCard
          label="Shot Conversion"
          value={`${att?.conversion_rate_pct ?? "—"}%`}
          subtext={`${att?.goals_scored ?? 0} goals scored`}
          accent="green"
          icon={Target}
        />
        <KpiCard
          label="Shot Efficiency"
          value={att?.shot_efficiency ? `+${att.shot_efficiency}` : "—"}
          subtext="Goals vs xG overperformance"
          accent="green"
          icon={Flame}
        />
        <KpiCard
          label="Tackle Success"
          value={`${def?.tackle_success_pct ?? "—"}%`}
          subtext={`${def?.tackles_won ?? 0} won / ${def?.tackles_total ?? 0}`}
          accent="blue"
          icon={Shield}
        />
        <KpiCard
          label="Defensive Actions"
          value={def?.total_defensive_actions ?? "—"}
          subtext={`${def?.defensive_actions_per_match ?? "—"}/match`}
          accent="slate"
          icon={Shield}
        />
        <KpiCard
          label="Discipline Index"
          value={def?.discipline_index ?? "—"}
          subtext={`${def?.yellow_cards ?? 0}Y • ${def?.red_cards ?? 0}R`}
          accent={def && def.discipline_index > 10 ? "amber" : "slate"}
          icon={AlertTriangle}
        />
      </section>

      {/* Two-Column Deep Dives: Attack Breakdown vs Defensive Breakdown */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Attacking Profile */}
        <div className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-5">
          <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
            <div>
              <h3 className="text-xs font-bold text-[#246B45] uppercase tracking-widest font-mono">
                Attacking Output & Shot Quality
              </h3>
              <p className="text-[11px] text-[#718078]">Goals, expected goals (xG), and chance creation</p>
            </div>
            <Badge variant="green">Attacking Profile</Badge>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl">
              <span className="text-[10px] text-[#718078] font-sans block">Total Expected Goals (xG)</span>
              <span className="text-xl font-bold text-[#26332B]">{att?.expected_goals ?? "—"}</span>
              <span className="text-[10px] text-[#718078] block mt-0.5">{att?.expected_goals_per_match ?? "—"} / match</span>
            </div>

            <div className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl">
              <span className="text-[10px] text-[#718078] font-sans block">Big Chances Created</span>
              <span className="text-xl font-bold text-[#246B45]">{att?.big_chances_created ?? "—"}</span>
              <span className="text-[10px] text-[#718078] block mt-0.5">{att?.big_chances_missed ?? 0} missed</span>
            </div>
          </div>

          {/* Half-by-Half Goal Distribution */}
          <div className="p-4 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl space-y-2">
            <span className="text-xs font-bold text-[#26332B] block">Goal Timing by Match Half</span>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-[#718078]">1st Half: {att?.half_breakdown.first_half_goals} goals ({att?.half_breakdown.first_half_pct}%)</span>
              <span className="text-[#718078]">2nd Half: {att?.half_breakdown.second_half_goals} goals ({att?.half_breakdown.second_half_pct}%)</span>
            </div>
            <div className="h-2 w-full bg-[#E2EAE3] rounded-full overflow-hidden flex">
              <div style={{ width: `${att?.half_breakdown.first_half_pct || 40}%` }} className="bg-[#246B45]" />
              <div style={{ width: `${att?.half_breakdown.second_half_pct || 60}%` }} className="bg-[#174B32]" />
            </div>
          </div>

          {/* Top Goal Contributors */}
          <div>
            <span className="text-xs font-bold text-[#26332B] block mb-2">Player Goal Contributions</span>
            <div className="space-y-1.5 font-mono text-xs">
              {att?.top_contributors.map((c, idx) => (
                <div
                  key={c.player_id}
                  className="flex items-center justify-between p-2 rounded bg-[#F4F8F4] border border-[#E2EAE3]"
                >
                  <div className="flex items-center space-x-2">
                    <span className="w-4 text-[#718078] font-bold">{idx + 1}.</span>
                    <span className="text-[#26332B] font-sans font-semibold">{c.player_name}</span>
                  </div>
                  <div className="flex items-center space-x-3 text-right">
                    <span className="text-[#246B45] font-bold">{c.goals}G</span>
                    <span className="text-[#174B32] font-bold">{c.assists}A</span>
                    <Badge variant="green">{c.goal_contributions} Total</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Defensive Resilience Profile */}
        <div className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-5">
          <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
            <div>
              <h3 className="text-xs font-bold text-[#174B32] uppercase tracking-widest font-mono">
                Defensive Resilience & Discipline
              </h3>
              <p className="text-[11px] text-[#718078]">Duel win rates, clearances, and card management</p>
            </div>
            <Badge variant="green">Defensive Profile</Badge>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl">
              <span className="text-[10px] text-[#718078] font-sans block">Goals Conceded Per Match</span>
              <span className="text-xl font-bold text-[#26332B]">{def?.goals_conceded_per_match ?? "—"}</span>
              <span className="text-[10px] text-[#718078] block mt-0.5">{def?.goals_conceded ?? 0} total goals</span>
            </div>

            <div className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl">
              <span className="text-[10px] text-[#718078] font-sans block">Clean Sheet Rate</span>
              <span className="text-xl font-bold text-[#246B45]">{def?.clean_sheet_percentage ?? "—"}%</span>
              <span className="text-[10px] text-[#718078] block mt-0.5">{def?.clean_sheets ?? 0} clean sheets</span>
            </div>
          </div>

          {/* Defensive Action Breakdown */}
          <div className="p-4 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl space-y-3 font-mono text-xs">
            <span className="text-xs font-bold text-[#26332B] font-sans block">Defensive Action Breakdown</span>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 bg-white rounded border border-[#E2EAE3] flex justify-between shadow-2xs">
                <span className="text-[#718078] font-sans">Interceptions:</span>
                <span className="font-bold text-[#246B45]">{def?.interceptions ?? "—"}</span>
              </div>
              <div className="p-2 bg-white rounded border border-[#E2EAE3] flex justify-between shadow-2xs">
                <span className="text-[#718078] font-sans">Clearances:</span>
                <span className="font-bold text-[#26332B]">{def?.clearances ?? "—"}</span>
              </div>
              <div className="p-2 bg-white rounded border border-[#E2EAE3] flex justify-between shadow-2xs">
                <span className="text-[#718078] font-sans">Goalkeeper Saves:</span>
                <span className="font-bold text-[#174B32]">{def?.saves ?? "—"}</span>
              </div>
              <div className="p-2 bg-white rounded border border-[#E2EAE3] flex justify-between shadow-2xs">
                <span className="text-[#718078] font-sans">Blocked Shots:</span>
                <span className="font-bold text-[#D9A441]">{def?.blocked_shots ?? "—"}</span>
              </div>
            </div>
          </div>

          {/* Disciplinary Summary */}
          <div className="p-4 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl space-y-2">
            <span className="text-xs font-bold text-[#26332B] block">Disciplinary Sanctions</span>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-[#D9A441] font-bold">{def?.yellow_cards} Yellow Cards (1 pt each)</span>
              <span className="text-[#C65B56] font-bold">{def?.red_cards} Red Cards (3 pts each)</span>
            </div>
            <p className="text-[11px] text-[#718078] font-mono">
              Disciplinary Risk Index: <span className="font-bold text-[#26332B]">{def?.discipline_index}</span> (Low squad suspension risk).
            </p>
          </div>
        </div>
      </section>

      {/* Squad Leadership Group Overview */}
      <LeadershipGroupSection className="mt-6" />
    </Shell>
  );
}
