"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import FootballPitch from "@/components/pitch/FootballPitch";
import {
  fetchMatchById,
  fetchMatchTacticalReport,
  fetchPassingNetwork,
  fetchShotMap,
} from "@/lib/api";
import {
  Match,
  MatchTacticalReport,
  PassingNetwork,
  ShotMap,
} from "@/lib/types";
import {
  Calendar,
  MapPin,
  Users,
  Shield,
  Activity,
  ArrowLeft,
  Clock,
  Target,
} from "lucide-react";
import Link from "next/link";

export default function MatchDetailPage() {
  const params = useParams();
  const matchId = params?.id as string;

  const [match, setMatch] = useState<Match | null>(null);
  const [report, setReport] = useState<MatchTacticalReport | null>(null);
  const [network, setNetwork] = useState<PassingNetwork | null>(null);
  const [shotMap, setShotMap] = useState<ShotMap | null>(null);
  const [activeTab, setActiveTab] = useState<"STATS" | "PITCH" | "TIMELINE" | "LINEUPS">("STATS");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    Promise.all([
      fetchMatchById(matchId).catch(() => null),
      fetchMatchTacticalReport(matchId).catch(() => null),
      fetchPassingNetwork(matchId, "cfc-1").catch(() => null),
      fetchShotMap(matchId).catch(() => null),
    ]).then(([matchData, reportData, netData, shotsData]) => {
      if (!isMounted) return;
      if (matchData) setMatch(matchData);
      if (reportData) setReport(reportData);
      if (netData) setNetwork(netData);
      if (shotsData) setShotMap(shotsData);
      setLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, [matchId]);

  const homeStats = report?.home_team.statistics;
  const awayStats = report?.away_team.statistics;

  return (
    <Shell
      title={`Match Report • ${report?.home_team.name || "Chennaiyin FC"} vs ${report?.away_team.name || "East Bengal FC"}`}
      subtitle="ISL 2026–27 Fixture Analysis & Tactical Breakdown"
    >
      {/* Back Button */}
      <div className="flex items-center space-x-2">
        <Link
          href="/matches"
          className="text-xs font-semibold text-slate-400 hover:text-slate-200 flex items-center space-x-1.5 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Match Centre</span>
        </Link>
      </div>

      {/* Main Match Header & Scoreboard Banner */}
      <section className="bg-gradient-to-r from-blue-950 via-slate-900 to-slate-900 border border-blue-900/40 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          {/* Home Team */}
          <div className="flex items-center space-x-4 flex-1 justify-start md:justify-end">
            <div className="text-left md:text-right">
              <span className="text-[10px] text-blue-400 font-mono uppercase font-bold tracking-wider">
                Home Club
              </span>
              <h2 className="text-xl md:text-2xl font-black text-white">
                {report?.home_team.name || match?.home_team?.name || "Chennaiyin FC"}
              </h2>
            </div>
            <div className="w-14 h-14 rounded-2xl bg-blue-700/80 border border-blue-500/40 flex items-center justify-center font-black font-mono text-xl text-white shadow-lg">
              {report?.home_team.short_name || "CFC"}
            </div>
          </div>

          {/* Central Score Display */}
          <div className="flex flex-col items-center justify-center px-6 py-2 bg-slate-950/80 border border-slate-800 rounded-2xl shadow-inner min-w-[160px]">
            <span className="text-[10px] text-emerald-400 font-mono font-bold uppercase tracking-widest mb-1">
              {report?.match_status || "FINISHED"}
            </span>
            <div className="flex items-center space-x-4 font-mono font-black text-4xl text-white">
              <span className="text-emerald-400">{report?.home_team.score ?? 5}</span>
              <span className="text-slate-600">:</span>
              <span>{report?.away_team.score ?? 3}</span>
            </div>
            <span className="text-[10px] text-slate-400 font-mono mt-1">
              HT: {report?.half_by_half.first_half.score || "2-1"}
            </span>
          </div>

          {/* Away Team */}
          <div className="flex items-center space-x-4 flex-1 justify-start">
            <div className="w-14 h-14 rounded-2xl bg-slate-800 border border-slate-700 flex items-center justify-center font-black font-mono text-xl text-slate-200 shadow-lg">
              {report?.away_team.short_name || "EBFC"}
            </div>
            <div className="text-left">
              <span className="text-[10px] text-slate-400 font-mono uppercase font-bold tracking-wider">
                Visiting Club
              </span>
              <h2 className="text-xl md:text-2xl font-black text-white">
                {report?.away_team.name || match?.away_team?.name || "East Bengal FC"}
              </h2>
            </div>
          </div>
        </div>

        {/* Match Metadata Ribbon */}
        <div className="mt-6 pt-4 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 font-mono gap-3">
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-500" />
              <span>{report?.venue || "Jawaharlal Nehru Stadium, Chennai"}</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1.5">
              <Users className="w-3.5 h-3.5 text-slate-500" />
              <span>Attendance: {report?.attendance || 18500}</span>
            </span>
          </div>
          <div>
            <span>Referee: {report?.referee || "Tejas Nagvenkar"}</span>
          </div>
        </div>
      </section>

      {/* Tabs Selector */}
      <div className="flex items-center space-x-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 w-fit text-xs font-semibold">
        {(["STATS", "PITCH", "TIMELINE", "LINEUPS"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg transition-all ${
              activeTab === tab
                ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab === "STATS" && "Side-by-Side Statistics"}
            {tab === "PITCH" && "Tactical Pitch Visualizations"}
            {tab === "TIMELINE" && "Event Timeline"}
            {tab === "LINEUPS" && "Lineups & Formations"}
          </button>
        ))}
      </div>

      {/* TAB 1: SIDE-BY-SIDE STATS */}
      {activeTab === "STATS" && (
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
            <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest font-mono">
              Match Performance Indicators
            </h3>

            {/* Stat Row Component */}
            {[
              {
                label: "Ball Possession %",
                home: homeStats?.possession_pct ?? 54.0,
                away: awayStats?.possession_pct ?? 46.0,
                unit: "%",
              },
              {
                label: "Total Shots",
                home: homeStats?.shots_total ?? 16,
                away: awayStats?.shots_total ?? 10,
              },
              {
                label: "Shots on Target",
                home: homeStats?.shots_on_target ?? 8,
                away: awayStats?.shots_on_target ?? 4,
              },
              {
                label: "Expected Goals (xG)",
                home: homeStats?.expected_goals ?? 2.85,
                away: awayStats?.expected_goals ?? 1.45,
              },
              {
                label: "Pass Accuracy %",
                home: homeStats?.pass_accuracy_pct ?? 83.3,
                away: awayStats?.pass_accuracy_pct ?? 77.8,
                unit: "%",
              },
              {
                label: "Tackles Won",
                home: homeStats?.tackles_won ?? 14,
                away: awayStats?.tackles_won ?? 10,
              },
              {
                label: "Corner Kicks",
                home: homeStats?.corners ?? 6,
                away: awayStats?.corners ?? 3,
              },
              {
                label: "Yellow Cards",
                home: homeStats?.yellow_cards ?? 2,
                away: awayStats?.yellow_cards ?? 3,
              },
            ].map((stat, idx) => {
              const homeNum = Number(stat.home || 0);
              const awayNum = Number(stat.away || 0);
              const total = homeNum + awayNum || 1;
              const homePct = (homeNum / total) * 100;

              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-blue-400">
                      {stat.home}
                      {stat.unit}
                    </span>
                    <span className="text-slate-400 uppercase text-[11px] font-sans font-semibold">
                      {stat.label}
                    </span>
                    <span className="font-bold text-slate-300">
                      {stat.away}
                      {stat.unit}
                    </span>
                  </div>
                  {/* Two-Tone Comparison Bar */}
                  <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden flex">
                    <div
                      style={{ width: `${homePct}%` }}
                      className="bg-blue-600 transition-all duration-300"
                    />
                    <div
                      style={{ width: `${100 - homePct}%` }}
                      className="bg-slate-600 transition-all duration-300"
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Half-by-Half Breakdown Card */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
            <div>
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest font-mono mb-4">
                Half-by-Half Tactical Split
              </h3>

              <div className="space-y-4">
                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                    <span>1st Half (0-45&apos;)</span>
                    <Badge variant="blue">HT</Badge>
                  </div>
                  <div className="text-2xl font-black font-mono text-white text-center py-1">
                    {report?.half_by_half.first_half.score || "2-1"}
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1 border-t border-slate-800/60">
                    <span>CFC Goals: {report?.half_by_half.first_half.home_goals ?? 2}</span>
                    <span>Opp Goals: {report?.half_by_half.first_half.away_goals ?? 1}</span>
                  </div>
                </div>

                <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                    <span>2nd Half (46-90&apos;+)</span>
                    <Badge variant="green">FT</Badge>
                  </div>
                  <div className="text-2xl font-black font-mono text-emerald-400 text-center py-1">
                    {report?.half_by_half.second_half.score || "3-2"}
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1 border-t border-slate-800/60">
                    <span>CFC Goals: {report?.half_by_half.second_half.home_goals ?? 3}</span>
                    <span>Opp Goals: {report?.half_by_half.second_half.away_goals ?? 2}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-blue-950/30 border border-blue-900/40 rounded-xl text-[11px] text-blue-300 font-mono">
              ⚡ High-intensity tactical momentum in second half with 5 total goals scored.
            </div>
          </div>
        </section>
      )}

      {/* TAB 2: INTERACTIVE PITCH */}
      {activeTab === "PITCH" && (
        <section className="space-y-4">
          <FootballPitch
            shots={shotMap?.shots}
            passNodes={network?.nodes}
            passEdges={network?.edges}
          />
        </section>
      )}

      {/* TAB 3: TIMELINE */}
      {activeTab === "TIMELINE" && (
        <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
          <h3 className="text-xs font-bold text-slate-200 uppercase tracking-widest font-mono mb-6">
            Chronological Match Events
          </h3>

          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
            {(
              report?.timeline || [
                { minute: 12, period: "FIRST_HALF", event_type: "GOAL", team_name: "Chennaiyin FC", primary_player: "Farukh Choudhary", secondary_player: "Lukas Brambilla", description: "Right footed shot into top right corner." },
                { minute: 24, period: "FIRST_HALF", event_type: "GOAL", team_name: "Chennaiyin FC", primary_player: "Wilmar Jordan Gil", secondary_player: "Connor Shields", description: "Header from 6 yards." },
                { minute: 36, period: "FIRST_HALF", event_type: "GOAL", team_name: "East Bengal FC", primary_player: "Madih Talal", description: "Direct free kick." },
                { minute: 55, period: "SECOND_HALF", event_type: "PENALTY_GOAL", team_name: "Chennaiyin FC", primary_player: "Lukas Brambilla", description: "Penalty converted calmly." },
                { minute: 68, period: "SECOND_HALF", event_type: "GOAL", team_name: "Chennaiyin FC", primary_player: "Wilmar Jordan Gil", secondary_player: "Lukas Brambilla", description: "Tap in after goalkeeper rebound." },
                { minute: 76, period: "SECOND_HALF", event_type: "GOAL", team_name: "East Bengal FC", primary_player: "Dimitrios Diamantakos", description: "Close range finish." },
                { minute: 88, period: "SECOND_HALF", event_type: "GOAL", team_name: "Chennaiyin FC", primary_player: "Irfan Yadwad", secondary_player: "Wilmar Jordan Gil", description: "Counter-attacking finish." },
              ]
            ).map((evt, idx) => {
              const isGoal = evt.event_type.includes("GOAL");
              const isCfc = evt.team_name === "Chennaiyin FC";

              return (
                <div key={idx} className="relative flex items-start space-x-4">
                  <div
                    className={`w-5 h-5 rounded-full flex items-center justify-center font-bold text-[10px] -ml-6 border ${
                      isGoal
                        ? "bg-emerald-600 text-white border-emerald-400"
                        : "bg-slate-800 text-slate-300 border-slate-700"
                    }`}
                  >
                    {isGoal ? "⚽" : "•"}
                  </div>

                  <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3.5 flex-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-slate-200">
                        {evt.minute}&apos; — {evt.event_type.replace("_", " ")}
                      </span>
                      <span className={`text-[11px] font-mono font-semibold ${isCfc ? "text-blue-400" : "text-amber-400"}`}>
                        {evt.team_name}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-slate-100 font-semibold">
                      {evt.primary_player}
                      {evt.secondary_player && (
                        <span className="text-slate-400 font-normal"> (Assist: {evt.secondary_player})</span>
                      )}
                    </p>
                    {evt.description && (
                      <p className="mt-0.5 text-[11px] text-slate-400">{evt.description}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* TAB 4: LINEUPS */}
      {activeTab === "LINEUPS" && (
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-widest font-mono mb-4">
              Chennaiyin FC Starting XI (4-2-3-1)
            </h3>
            <div className="space-y-2 font-mono text-xs">
              {[
                { no: 1, name: "Samik Mitra", pos: "GK" },
                { no: 22, name: "Ankit Mukherjee", pos: "RB" },
                { no: 6, name: "Ryan Edwards (C)", pos: "CB" },
                { no: 3, name: "Bikash Yumnam", pos: "CB" },
                { no: 26, name: "Laldinliana Renthlei", pos: "LB" },
                { no: 8, name: "Jiteshwor Singh", pos: "DM" },
                { no: 10, name: "Connor Shields", pos: "CM" },
                { no: 14, name: "Lukas Brambilla", pos: "AM" },
                { no: 11, name: "Farukh Choudhary", pos: "LW" },
                { no: 7, name: "Vincy Barretto", pos: "RW" },
                { no: 9, name: "Wilmar Jordan Gil", pos: "CF" },
              ].map((p) => (
                <div key={p.no} className="flex items-center justify-between p-2 rounded bg-slate-950/60 border border-slate-800/80">
                  <div className="flex items-center space-x-2.5">
                    <span className="w-5 text-right font-bold text-slate-400">#{p.no}</span>
                    <span className="font-semibold text-slate-200">{p.name}</span>
                  </div>
                  <span className="text-[10px] text-blue-400 font-bold">{p.pos}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-widest font-mono mb-4">
              East Bengal FC Starting XI (4-3-3)
            </h3>
            <div className="space-y-2 font-mono text-xs">
              {[
                { no: 13, name: "Prabhsukhan Gill", pos: "GK" },
                { no: 12, name: "Mohammad Rakip", pos: "RB" },
                { no: 4, name: "Anwar Ali", pos: "CB" },
                { no: 26, name: "Hector Yuste", pos: "CB" },
                { no: 5, name: "Lalchungnunga", pos: "LB" },
                { no: 8, name: "Saul Crespo", pos: "CM" },
                { no: 6, name: "Jeakson Singh", pos: "DM" },
                { no: 10, name: "Madih Talal", pos: "AM" },
                { no: 11, name: "Nandhakumar Sekar", pos: "LW" },
                { no: 9, name: "Dimitrios Diamantakos", pos: "CF" },
                { no: 7, name: "Naorem Mahesh Singh", pos: "RW" },
              ].map((p) => (
                <div key={p.no} className="flex items-center justify-between p-2 rounded bg-slate-950/60 border border-slate-800/80">
                  <div className="flex items-center space-x-2.5">
                    <span className="w-5 text-right font-bold text-slate-400">#{p.no}</span>
                    <span className="font-semibold text-slate-200">{p.name}</span>
                  </div>
                  <span className="text-[10px] text-slate-400 font-bold">{p.pos}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </Shell>
  );
}
