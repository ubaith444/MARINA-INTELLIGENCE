"use client";

import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import KpiCard from "@/components/ui/KpiCard";
import Badge from "@/components/ui/Badge";
import GoalTrendChart from "@/components/charts/GoalTrendChart";
import { fetchTeamAttacking, fetchTeamDefensive, fetchTeamPerformance } from "@/lib/api";
import { AttackingAnalytics, DefensiveAnalytics, TeamSeasonPerformance } from "@/lib/types";
import {
  Shield,
  Target,
  Crosshair,
  Flame,
  Award,
  AlertTriangle,
  ArrowUpRight,
} from "lucide-react";
import Link from "next/link";

export default function TeamAnalysisPage() {
  const [attacking, setAttacking] = useState<AttackingAnalytics | null>(null);
  const [defensive, setDefensive] = useState<DefensiveAnalytics | null>(null);
  const [performance, setPerformance] = useState<TeamSeasonPerformance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    Promise.all([
      fetchTeamAttacking("cfc-1").catch(() => null),
      fetchTeamDefensive("cfc-1").catch(() => null),
      fetchTeamPerformance("cfc-1").catch(() => null),
    ]).then(([attData, defData, perfData]) => {
      if (!isMounted) return;
      if (attData) setAttacking(attData);
      else {
        setAttacking({
          team_id: "cfc-1",
          team_name: "Chennaiyin FC",
          matches_analyzed: 3,
          goals_scored: 8,
          goals_per_match: 2.67,
          shots_total: 44,
          shots_per_match: 14.67,
          shots_on_target: 20,
          shots_off_target: 16,
          blocked_shots: 8,
          shooting_accuracy_pct: 45.45,
          conversion_rate_pct: 18.18,
          expected_goals: 6.45,
          expected_goals_per_match: 2.15,
          shot_efficiency: 1.55,
          big_chances_created: 11,
          big_chances_missed: 4,
          half_breakdown: {
            first_half_goals: 3,
            second_half_goals: 5,
            first_half_pct: 37.5,
            second_half_pct: 62.5,
          },
          top_contributors: [
            { player_id: "p1", player_name: "Wilmar Jordan Gil", goals: 3, assists: 1, goal_contributions: 4 },
            { player_id: "p2", player_name: "Lukas Brambilla", goals: 1, assists: 2, goal_contributions: 3 },
            { player_id: "p3", player_name: "Farukh Choudhary", goals: 2, assists: 0, goal_contributions: 2 },
            { player_id: "p4", player_name: "Irfan Yadwad", goals: 1, assists: 0, goal_contributions: 1 },
            { player_id: "p5", player_name: "Connor Shields", goals: 0, assists: 1, goal_contributions: 1 },
          ],
        });
      }

      if (defData) setDefensive(defData);
      else {
        setDefensive({
          team_id: "cfc-1",
          team_name: "Chennaiyin FC",
          matches_analyzed: 3,
          goals_conceded: 4,
          goals_conceded_per_match: 1.33,
          clean_sheets: 1,
          clean_sheet_percentage: 33.3,
          expected_goals_conceded: 3.85,
          expected_goals_conceded_per_match: 1.28,
          tackles_total: 48,
          tackles_won: 36,
          tackle_success_pct: 75.0,
          interceptions: 33,
          clearances: 56,
          saves: 11,
          blocked_shots: 10,
          total_defensive_actions: 147,
          defensive_actions_per_match: 49.0,
          yellow_cards: 6,
          red_cards: 0,
          discipline_index: 6,
        });
      }

      setLoading(false);
    });

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
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest font-mono">
                Attacking Output & Shot Quality
              </h3>
              <p className="text-[11px] text-slate-400">Goals, expected goals ($xG$), and chance creation</p>
            </div>
            <Badge variant="blue">Attacking Profile</Badge>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-400 font-sans block">Total Expected Goals (xG)</span>
              <span className="text-xl font-bold text-white">{att?.expected_goals ?? "—"}</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{att?.expected_goals_per_match ?? "—"} / match</span>
            </div>

            <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-400 font-sans block">Big Chances Created</span>
              <span className="text-xl font-bold text-emerald-400">{att?.big_chances_created ?? "—"}</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{att?.big_chances_missed ?? 0} missed</span>
            </div>
          </div>

          {/* Half-by-Half Goal Distribution */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-2">
            <span className="text-xs font-bold text-slate-200 block">Goal Timing by Match Half</span>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-slate-400">1st Half: {att?.half_breakdown.first_half_goals} goals ({att?.half_breakdown.first_half_pct}%)</span>
              <span className="text-slate-400">2nd Half: {att?.half_breakdown.second_half_goals} goals ({att?.half_breakdown.second_half_pct}%)</span>
            </div>
            <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
              <div style={{ width: `${att?.half_breakdown.first_half_pct || 40}%` }} className="bg-blue-600" />
              <div style={{ width: `${att?.half_breakdown.second_half_pct || 60}%` }} className="bg-emerald-500" />
            </div>
          </div>

          {/* Top Goal Contributors */}
          <div>
            <span className="text-xs font-bold text-slate-200 block mb-2">Player Goal Contributions</span>
            <div className="space-y-1.5 font-mono text-xs">
              {att?.top_contributors.map((c, idx) => (
                <div
                  key={c.player_id}
                  className="flex items-center justify-between p-2 rounded bg-slate-950/60 border border-slate-800"
                >
                  <div className="flex items-center space-x-2">
                    <span className="w-4 text-slate-500 font-bold">{idx + 1}.</span>
                    <span className="text-slate-200 font-sans font-semibold">{c.player_name}</span>
                  </div>
                  <div className="flex items-center space-x-3 text-right">
                    <span className="text-emerald-400 font-bold">{c.goals}G</span>
                    <span className="text-blue-400 font-bold">{c.assists}A</span>
                    <Badge variant="blue">{c.goal_contributions} Total</Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Defensive Resilience Profile */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono">
                Defensive Resilience & Discipline
              </h3>
              <p className="text-[11px] text-slate-400">Duel win rates, clearances, and card management</p>
            </div>
            <Badge variant="green">Defensive Profile</Badge>
          </div>

          <div className="grid grid-cols-2 gap-3 font-mono text-xs">
            <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-400 font-sans block">Goals Conceded Per Match</span>
              <span className="text-xl font-bold text-white">{def?.goals_conceded_per_match ?? "—"}</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{def?.goals_conceded ?? 0} total goals</span>
            </div>

            <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-xl">
              <span className="text-[10px] text-slate-400 font-sans block">Clean Sheet Rate</span>
              <span className="text-xl font-bold text-emerald-400">{def?.clean_sheet_percentage ?? "—"}%</span>
              <span className="text-[10px] text-slate-500 block mt-0.5">{def?.clean_sheets ?? 0} clean sheets</span>
            </div>
          </div>

          {/* Defensive Action Breakdown */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-3 font-mono text-xs">
            <span className="text-xs font-bold text-slate-200 font-sans block">Defensive Action Breakdown</span>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 bg-slate-900/80 rounded border border-slate-800/80 flex justify-between">
                <span className="text-slate-400 font-sans">Interceptions:</span>
                <span className="font-bold text-blue-400">{def?.interceptions ?? "—"}</span>
              </div>
              <div className="p-2 bg-slate-900/80 rounded border border-slate-800/80 flex justify-between">
                <span className="text-slate-400 font-sans">Clearances:</span>
                <span className="font-bold text-slate-200">{def?.clearances ?? "—"}</span>
              </div>
              <div className="p-2 bg-slate-900/80 rounded border border-slate-800/80 flex justify-between">
                <span className="text-slate-400 font-sans">Goalkeeper Saves:</span>
                <span className="font-bold text-emerald-400">{def?.saves ?? "—"}</span>
              </div>
              <div className="p-2 bg-slate-900/80 rounded border border-slate-800/80 flex justify-between">
                <span className="text-slate-400 font-sans">Blocked Shots:</span>
                <span className="font-bold text-amber-400">{def?.blocked_shots ?? "—"}</span>
              </div>
            </div>
          </div>

          {/* Disciplinary Summary */}
          <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-xl space-y-2">
            <span className="text-xs font-bold text-slate-200 block">Disciplinary Sanctions</span>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-amber-400 font-bold">{def?.yellow_cards} Yellow Cards (1 pt each)</span>
              <span className="text-rose-400 font-bold">{def?.red_cards} Red Cards (3 pts each)</span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono">
              Disciplinary Risk Index: <span className="font-bold text-slate-100">{def?.discipline_index}</span> (Low squad suspension risk).
            </p>
          </div>
        </div>
      </section>
    </Shell>
  );
}
