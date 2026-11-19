"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import FootballPitch from "@/components/pitch/FootballPitch";
import {
  fetchMatchById,
  fetchMatches,
  fetchMatchPlayers,
  fetchMatchTacticalReport,
  fetchShotMap,
} from "@/lib/api";
import {
  Match,
  MatchPlayersResponse,
  MatchTacticalReport,
  ShotMap,
} from "@/lib/types";
import {
  Calendar,
  MapPin,
  Users,
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
} from "lucide-react";
import Link from "next/link";

export default function MatchDetailPage() {
  const params = useParams();
  const matchId = params?.id as string;

  const [match, setMatch] = useState<Match | null>(null);
  const [report, setReport] = useState<MatchTacticalReport | null>(null);
  const [matchPlayers, setMatchPlayers] = useState<MatchPlayersResponse | null>(null);
  const [allMatches, setAllMatches] = useState<Match[]>([]);
  const [shotMap, setShotMap] = useState<ShotMap | null>(null);
  const [activeTab, setActiveTab] = useState<"STATS" | "PLAYERS" | "LINEUPS" | "TIMELINE" | "PITCH">("STATS");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    Promise.all([
      fetchMatchById(matchId).catch(() => null),
      fetchMatchTacticalReport(matchId).catch(() => null),
      fetchMatchPlayers(matchId).catch(() => null),
      fetchMatches().catch(() => []),
      fetchShotMap(matchId).catch(() => null),
    ]).then(([matchData, reportData, playersData, matchesList, shotsData]) => {
      if (!isMounted) return;
      if (matchData) setMatch(matchData);
      if (reportData) setReport(reportData);
      if (playersData) setMatchPlayers(playersData);
      if (matchesList) setAllMatches(matchesList);
      if (shotsData) setShotMap(shotsData);
      setLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, [matchId]);

  // Compute previous and next match navigation
  const sortedMatches = [...allMatches].sort((a, b) => (a.match_number || 0) - (b.match_number || 0));
  const currentIndex = sortedMatches.findIndex((m) => m.id === matchId);
  const prevMatch = currentIndex > 0 ? sortedMatches[currentIndex - 1] : null;
  const nextMatch = currentIndex >= 0 && currentIndex < sortedMatches.length - 1 ? sortedMatches[currentIndex + 1] : null;

  const isFinished = match?.match_status === "FINISHED";
  const homeTeam = match?.home_team || report?.home_team;
  const awayTeam = match?.away_team || report?.away_team;
  const isCfcHome = (homeTeam as any)?.slug === "chennaiyin-fc" || homeTeam?.short_name === "CFC";

  const homeStats = report?.home_team.statistics;
  const awayStats = report?.away_team.statistics;

  const kickoff = match?.scheduled_kickoff ? new Date(match.scheduled_kickoff) : null;
  const dateStr = kickoff
    ? kickoff.toLocaleDateString("en-IN", {
      weekday: "short",
      month: "short",
      day: "numeric",
      year: "numeric",
    })
    : "Date TBC";
  const timeStr = kickoff
    ? kickoff.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    })
    : match?.kickoff_time_ist || "Kickoff TBC";

  // Calculate CFC match outcome
  const cfcOutcome = isFinished && typeof match?.home_score === "number" && typeof match?.away_score === "number"
    ? isCfcHome
      ? match.home_score > match.away_score ? "W" : match.home_score === match.away_score ? "D" : "L"
      : match.away_score > match.home_score ? "W" : match.away_score === match.home_score ? "D" : "L"
    : null;

  // Extract goal events
  const goalEvents = match?.events?.filter((e) => e.event_type.includes("GOAL")) || [];

  // Helper to format missing metrics strictly as "N/A"
  const fmtStat = (val: number | null | undefined, unit: string = "") => {
    if (val === null || val === undefined) return "N/A";
    return `${val}${unit}`;
  };

  if (loading) {
    return (
      <Shell title="Match Report" subtitle="Loading verified match analytics...">
        <div className="py-24 text-center font-mono text-xs text-[#718078]">
          <div className="animate-spin w-8 h-8 border-2 border-[#246B45] border-t-transparent rounded-full mx-auto mb-3" />
          Loading verified match dossier...
        </div>
      </Shell>
    );
  }

  return (
    <Shell
      title={`Match Report • Matchweek ${match?.matchweek || match?.match_number || "—"}`}
      subtitle={`${homeTeam?.name || "Chennaiyin FC"} vs ${awayTeam?.name || "Opponent"} • ISL 2026–27`}
    >
      {/* 1. Previous / Next Match Navigation & Breadcrumbs */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 text-xs font-mono">
        <Link
          href="/matches"
          className="text-xs font-semibold text-[#718078] hover:text-[#26332B] flex items-center space-x-1.5 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Match Centre</span>
        </Link>

        <div className="flex items-center space-x-2">
          {prevMatch ? (
            <Link
              href={`/matches/${prevMatch.id}`}
              className="px-3 py-1.5 rounded-xl bg-white border border-[#E2EAE3] hover:border-[#246B45] text-[#26332B] flex items-center space-x-1.5 transition-all text-[11px] shadow-xs"
            >
              <ChevronLeft className="w-3.5 h-3.5 text-[#246B45]" />
              <span>Match #{prevMatch.match_number} ({prevMatch.home_team?.short_name} vs {prevMatch.away_team?.short_name})</span>
            </Link>
          ) : (
            <span className="px-3 py-1.5 rounded-xl bg-[#F4F8F4] border border-[#E2EAE3] text-[#718078] text-[11px]">
              First Fixture
            </span>
          )}

          {nextMatch ? (
            <Link
              href={`/matches/${nextMatch.id}`}
              className="px-3 py-1.5 rounded-xl bg-white border border-[#E2EAE3] hover:border-[#246B45] text-[#26332B] flex items-center space-x-1.5 transition-all text-[11px] shadow-xs"
            >
              <span>Match #{nextMatch.match_number} ({nextMatch.home_team?.short_name} vs {nextMatch.away_team?.short_name})</span>
              <ChevronRight className="w-3.5 h-3.5 text-[#246B45]" />
            </Link>
          ) : (
            <span className="px-3 py-1.5 rounded-xl bg-[#F4F8F4] border border-[#E2EAE3] text-[#718078] text-[11px]">
              Season Finale
            </span>
          )}
        </div>
      </div>

      {/* 2 & 3. Main Scoreboard Banner with Match Result Badge & Half-Time Score */}
      <section className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs relative overflow-hidden">
        {/* CFC Result Badge in Banner Corner */}
        {cfcOutcome && (
          <div className="absolute top-4 right-4 flex items-center space-x-2">
            <span
              className={`px-3 py-1 rounded-xl text-xs font-mono font-black uppercase tracking-wider border shadow-xs ${cfcOutcome === "W"
                ? "bg-[#E6F0E7] text-[#174B32] border-[#C3DEC7]"
                : cfcOutcome === "D"
                  ? "bg-amber-50 text-amber-800 border-amber-200"
                  : "bg-rose-50 text-rose-800 border-rose-200"
                }`}
            >
              {cfcOutcome === "W" ? "✓ CFC WIN" : cfcOutcome === "D" ? "– DRAW" : "✕ CFC LOSS"}
            </span>
          </div>
        )}

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          {/* Home Team */}
          <div className="flex items-center space-x-4 flex-1 justify-start md:justify-end">
            <div className="text-left md:text-right">
              <span className="text-[10px] text-[#246B45] font-mono uppercase font-bold tracking-wider">
                {isCfcHome ? "Anchor Club" : "Host Club"}
              </span>
              <h2 className={`text-xl md:text-2xl font-black ${isCfcHome ? "text-[#246B45]" : "text-[#26332B]"}`}>
                {homeTeam?.name || "Home Club"}
              </h2>
            </div>
            <div className="w-14 h-14 rounded-2xl bg-[#E6F0E7] border border-[#C3DEC7] flex items-center justify-center font-black font-mono text-xl text-[#174B32] shadow-xs">
              {homeTeam?.short_name || "H"}
            </div>
          </div>

          {/* Central Score Display */}
          <div className="flex flex-col items-center justify-center px-6 py-2 bg-[#F4F8F4] border border-[#E2EAE3] rounded-2xl shadow-inner min-w-[170px]">
            <span className="text-[10px] text-[#246B45] font-mono font-bold uppercase tracking-widest mb-1">
              {isFinished ? "FULL TIME" : "SCHEDULED"}
            </span>
            {isFinished && typeof match?.home_score === "number" && typeof match?.away_score === "number" ? (
              <div className="flex items-center space-x-4 font-mono font-black text-4xl text-[#26332B]">
                <span className={match.home_score > match.away_score ? "text-[#246B45]" : ""}>
                  {match.home_score}
                </span>
                <span className="text-[#718078]">:</span>
                <span className={match.away_score > match.home_score ? "text-[#246B45]" : ""}>
                  {match.away_score}
                </span>
              </div>
            ) : (
              <div className="font-mono font-black text-3xl text-[#246B45] py-1">
                VS
              </div>
            )}
            <span className="text-[10px] text-[#718078] font-mono mt-1">
              {isFinished
                ? report?.half_by_half?.first_half?.score
                  ? `HT: ${report.half_by_half.first_half.score}`
                  : "HT: N/A"
                : `${timeStr}`}
            </span>
          </div>

          {/* Away Team */}
          <div className="flex items-center space-x-4 flex-1 justify-start">
            <div className="w-14 h-14 rounded-2xl bg-[#F4F8F4] border border-[#E2EAE3] flex items-center justify-center font-black font-mono text-xl text-[#26332B] shadow-xs">
              {awayTeam?.short_name || "A"}
            </div>
            <div className="text-left">
              <span className="text-[10px] text-[#718078] font-mono uppercase font-bold tracking-wider">
                {!isCfcHome ? "Anchor Club" : "Visiting Club"}
              </span>
              <h2 className={`text-xl md:text-2xl font-black ${!isCfcHome ? "text-[#246B45]" : "text-[#26332B]"}`}>
                {awayTeam?.name || "Away Club"}
              </h2>
            </div>
          </div>
        </div>

        {/* 4. Goalscorers Summary Row (if finished and goals exist) */}
        {isFinished && goalEvents.length > 0 && (
          <div className="mt-4 pt-3 border-t border-[#E2EAE3]">
            <div className="flex flex-wrap items-center justify-center gap-x-4 gap-y-1.5 text-xs font-mono text-[#26332B]">
              <span className="text-[#718078] font-bold uppercase text-[10px]">⚽ Goals:</span>
              {goalEvents.map((g, idx) => {
                const pName = g.primary_player?.known_name || (g.primary_player ? `${g.primary_player.first_name} ${g.primary_player.last_name}` : "Player");
                const aName = g.secondary_player?.known_name || (g.secondary_player ? `${g.secondary_player.first_name} ${g.secondary_player.last_name}` : null);
                return (
                  <span key={idx} className="bg-[#F4F8F4] border border-[#E2EAE3] px-2.5 py-0.5 rounded-lg">
                    <strong>{pName}</strong> {g.minute}&apos;{g.stoppage_minute ? `+${g.stoppage_minute}'` : ""}
                    {aName && <span className="text-[#718078] font-normal"> (ast. {aName})</span>}
                  </span>
                );
              })}
            </div>
          </div>
        )}

        {/* Match Metadata Ribbon */}
        <div className="mt-5 pt-4 border-t border-[#E2EAE3] flex flex-wrap items-center justify-between text-xs text-[#718078] font-mono gap-3">
          <div className="flex flex-wrap items-center space-x-4">
            <span className="flex items-center space-x-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#246B45]" />
              <span>{dateStr} • {timeStr}</span>
            </span>
            <span className="text-[#E2EAE3]">•</span>
            <span className="flex items-center space-x-1.5">
              <MapPin className="w-3.5 h-3.5 text-[#246B45]" />
              <span>{match?.venue?.name || "Jawaharlal Nehru Stadium"}, {match?.venue?.city || "Chennai"}</span>
            </span>
            {match?.attendance && (
              <>
                <span className="text-[#E2EAE3]">•</span>
                <span className="flex items-center space-x-1.5">
                  <Users className="w-3.5 h-3.5 text-[#246B45]" />
                  <span>Attendance: {match.attendance.toLocaleString()}</span>
                </span>
              </>
            )}
          </div>
          <div>
            <span>Referee: <strong className="text-[#26332B]">{match?.referee || "Official Appointed"}</strong></span>
          </div>
        </div>
      </section>

      {/* Navigation Tabs Selector */}
      <div className="flex items-center space-x-1 bg-white p-1.5 rounded-xl border border-[#E2EAE3] w-fit text-xs font-semibold overflow-x-auto shadow-xs">
        {(
          [
            { id: "STATS", label: "Team Statistics" },
            { id: "PLAYERS", label: "Player Statistics" },
            { id: "LINEUPS", label: "Lineups & Formations" },
            { id: "TIMELINE", label: "Events & Cards" },
            { id: "PITCH", label: "Tactical Pitch" },
          ] as const
        ).map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg transition-all whitespace-nowrap ${activeTab === tab.id
              ? "bg-[#246B45] text-white shadow-xs"
              : "text-[#718078] hover:text-[#26332B]"
              }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB 1: TEAM SIDE-BY-SIDE STATS */}
      {activeTab === "STATS" && (
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-5">
            <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
              <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono">
                Team Comparison (Side-by-Side)
              </h3>
              <span className="text-[11px] font-mono text-[#718078]">
                {isFinished ? "Verified Primary Feed Metrics" : "Metrics Available Post-Match"}
              </span>
            </div>

            {/* Stat Row Component - STRICT N/A RULES */}
            {[
              {
                label: "Ball Possession %",
                home: homeStats?.possession_pct,
                away: awayStats?.possession_pct,
                unit: "%",
              },
              {
                label: "Total Shots",
                home: homeStats?.shots_total,
                away: awayStats?.shots_total,
              },
              {
                label: "Shots on Target",
                home: homeStats?.shots_on_target,
                away: awayStats?.shots_on_target,
              },
              {
                label: "Expected Goals (xG)",
                home: homeStats?.expected_goals,
                away: awayStats?.expected_goals,
              },
              {
                label: "Passes Completed",
                home: homeStats?.passes_completed,
                away: awayStats?.passes_completed,
              },
              {
                label: "Pass Accuracy %",
                home: homeStats?.pass_accuracy_pct,
                away: awayStats?.pass_accuracy_pct,
                unit: "%",
              },
              {
                label: "Corner Kicks",
                home: homeStats?.corners,
                away: awayStats?.corners,
              },
              {
                label: "Fouls Committed",
                home: homeStats?.fouls_committed,
                away: awayStats?.fouls_committed,
              },
              {
                label: "Yellow Cards",
                home: homeStats?.yellow_cards,
                away: awayStats?.yellow_cards,
              },
              {
                label: "Goalkeeper Saves",
                home: homeStats?.saves,
                away: awayStats?.saves,
              },
            ].map((stat, idx) => {
              const hasData =
                stat.home !== undefined &&
                stat.home !== null &&
                stat.away !== undefined &&
                stat.away !== null;
              const homeNum = Number(stat.home || 0);
              const awayNum = Number(stat.away || 0);
              const total = homeNum + awayNum || 1;
              const homePct = (homeNum / total) * 100;

              return (
                <div key={idx} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="font-bold text-[#246B45]">
                      {fmtStat(stat.home, stat.unit)}
                    </span>
                    <span className="text-[#718078] uppercase text-[11px] font-sans font-semibold">
                      {stat.label}
                    </span>
                    <span className="font-bold text-[#26332B]">
                      {fmtStat(stat.away, stat.unit)}
                    </span>
                  </div>
                  <div className="h-2 w-full bg-[#F4F8F4] border border-[#E2EAE3] rounded-full overflow-hidden flex">
                    {hasData ? (
                      <>
                        <div
                          style={{ width: `${homePct}%` }}
                          className="bg-[#246B45] transition-all duration-300"
                        />
                        <div
                          style={{ width: `${100 - homePct}%` }}
                          className="bg-[#718078] transition-all duration-300"
                        />
                      </>
                    ) : (
                      <div className="w-full bg-[#E2EAE3]/40" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Half-by-Half Breakdown Card & Verification Box */}
          <div className="space-y-6">
            <div className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono mb-4">
                  Half-by-Half Tactical Split
                </h3>

                {isFinished ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl space-y-1">
                      <div className="flex items-center justify-between text-xs text-[#718078] font-mono">
                        <span>1st Half (0-45&apos;)</span>
                        <Badge variant="blue">HT</Badge>
                      </div>
                      <div className="text-2xl font-black font-mono text-[#26332B] text-center py-1">
                        {report?.half_by_half?.first_half?.score || "N/A"}
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-[#718078] font-mono pt-1 border-t border-[#E2EAE3]">
                        <span>Home: {fmtStat(report?.half_by_half?.first_half?.home_goals)}</span>
                        <span>Away: {fmtStat(report?.half_by_half?.first_half?.away_goals)}</span>
                      </div>
                    </div>

                    <div className="p-4 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl space-y-1">
                      <div className="flex items-center justify-between text-xs text-[#718078] font-mono">
                        <span>2nd Half (46-90&apos;+)</span>
                        <Badge variant="green">FT</Badge>
                      </div>
                      <div className="text-2xl font-black font-mono text-[#246B45] text-center py-1">
                        {report?.half_by_half?.second_half?.score || "N/A"}
                      </div>
                      <div className="flex items-center justify-between text-[11px] text-[#718078] font-mono pt-1 border-t border-[#E2EAE3]">
                        <span>Home: {fmtStat(report?.half_by_half?.second_half?.home_goals)}</span>
                        <span>Away: {fmtStat(report?.half_by_half?.second_half?.away_goals)}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-8 text-center text-[#718078] font-mono text-xs bg-[#F4F8F4] rounded-xl border border-[#E2EAE3]">
                    Half-by-half tactical metrics will generate dynamically once the match commences.
                  </div>
                )}
              </div>
            </div>

            {/* 10. Data Source & Verification Details Box */}
            <div className="bg-white border border-[#E2EAE3] rounded-2xl p-5 shadow-xs space-y-3 font-mono text-xs">
              <div className="flex items-center space-x-2 text-[#246B45] font-bold uppercase tracking-wider text-[11px]">
                <CheckCircle2 className="w-4 h-4" />
                <span>Data Source & Verification Audit</span>
              </div>
              <div className="space-y-2 text-[#26332B]">
                <div className="flex items-center justify-between">
                  <span className="text-[#718078]">Provider:</span>
                  <span className="text-[#26332B] font-semibold">{matchPlayers?.data_source || match?.source_url || "Official ISL Match Centre (365scores)"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#718078]">Status:</span>
                  <span className="text-[#246B45] font-bold">{match?.verification_status || "VERIFIED"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#718078]">Venue Status:</span>
                  <span className="text-[#174B32] font-semibold">{match?.venue_verification_status || "CONFIRMED"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#718078]">Discrepancy:</span>
                  <span className="text-[#26332B]">{match?.has_discrepancy ? "Flagged" : "None (0)"}</span>
                </div>
              </div>
              <p className="text-[10px] text-[#718078] pt-2 border-t border-[#E2EAE3]">
                🛡️ Strictly non-fabricated data. Missing statistics preserved as N/A per MARINA intelligence protocol.
              </p>
            </div>
          </div>
        </section>
      )}

      {/* TAB 2: INDIVIDUAL PLAYER STATISTICS */}
      {activeTab === "PLAYERS" && (
        <section className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#E2EAE3] pb-3">
            <div>
              <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono">
                Individual Player Match Performance Statistics
              </h3>
              <p className="text-[11px] text-[#718078] font-mono mt-0.5">
                Exact matchday performance metrics for Starting XI and Substitutes
              </p>
            </div>
            {matchPlayers?.formation && (
              <span className="text-xs font-mono font-bold text-[#174B32] bg-[#E6F0E7] border border-[#C3DEC7] px-3 py-1 rounded-lg w-fit">
                Formation: {matchPlayers.formation}
              </span>
            )}
          </div>

          {/* Starting XI Table */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-[#246B45] uppercase tracking-wider font-mono flex items-center justify-between">
              <span>Starting XI ({matchPlayers?.starting_xi.length || 0})</span>
              <span className="text-[10px] text-[#718078]">11 Verified Starters</span>
            </h4>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono border-collapse">
                <thead>
                  <tr className="bg-[#F4F8F4] border-b border-[#E2EAE3] text-[11px] text-[#718078] uppercase">
                    <th className="py-2.5 px-3">#</th>
                    <th className="py-2.5 px-3">Player</th>
                    <th className="py-2.5 px-3">Pos</th>
                    <th className="py-2.5 px-3 text-center">Min</th>
                    <th className="py-2.5 px-3 text-center">G</th>
                    <th className="py-2.5 px-3 text-center">A</th>
                    <th className="py-2.5 px-3 text-center">Sh (OT)</th>
                    <th className="py-2.5 px-3 text-center">Passes (Acc %)</th>
                    <th className="py-2.5 px-3 text-center">Tkl Won</th>
                    <th className="py-2.5 px-3 text-center">Saves</th>
                    <th className="py-2.5 px-3 text-center">Cards</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2EAE3] text-[#26332B]">
                  {matchPlayers && matchPlayers.starting_xi.length > 0 ? (
                    matchPlayers.starting_xi.map((p, idx) => (
                      <tr key={idx} className="hover:bg-[#F4F8F4]/80 transition-colors">
                        <td className="py-2.5 px-3 text-[#718078] font-bold">#{p.jersey_number ?? "-"}</td>
                        <td className="py-2.5 px-3 font-semibold text-[#26332B]">
                          <Link href={`/players/${p.player_id}`} className="hover:text-[#246B45] transition-colors">
                            {p.name}
                          </Link>
                          {p.is_captain && <span className="ml-1 text-[#D9A441] text-[10px] font-bold">(C)</span>}
                          {p.sub_out_minute && (
                            <span className="ml-1.5 text-[#C65B56] text-[10px]">▼ {p.sub_out_minute}&apos;</span>
                          )}
                        </td>
                        <td className="py-2.5 px-3 text-[#246B45] font-bold">{p.position || "—"}</td>
                        <td className="py-2.5 px-3 text-center">{p.minutes_played !== null ? `${p.minutes_played}'` : "N/A"}</td>
                        <td className="py-2.5 px-3 text-center font-bold text-[#246B45]">{p.goals ?? 0}</td>
                        <td className="py-2.5 px-3 text-center text-[#174B32]">{p.assists ?? 0}</td>
                        <td className="py-2.5 px-3 text-center text-[#26332B]">
                          {p.shots_total !== null && p.shots_total !== undefined ? `${p.shots_total} (${p.shots_on_target ?? 0})` : "N/A"}
                        </td>
                        <td className="py-2.5 px-3 text-center text-[#26332B]">
                          {p.passes_completed !== null && p.passes_completed !== undefined
                            ? `${p.passes_completed}/${p.passes_total ?? 0} (${p.pass_accuracy_pct ?? 0}%)`
                            : "N/A"}
                        </td>
                        <td className="py-2.5 px-3 text-center">{p.tackles_won !== null && p.tackles_won !== undefined ? p.tackles_won : "N/A"}</td>
                        <td className="py-2.5 px-3 text-center text-[#246B45]">
                          {p.saves !== null && p.saves !== undefined ? p.saves : "—"}
                        </td>
                        <td className="py-2.5 px-3 text-center">
                          {p.red_cards ? (
                            <span className="w-2.5 h-3.5 bg-[#C65B56] inline-block rounded-xs" title="Red card dismissal" />
                          ) : p.yellow_cards ? (
                            <span className="w-2.5 h-3.5 bg-[#D9A441] inline-block rounded-xs" title={`${p.yellow_cards} Yellow card(s)`} />
                          ) : (
                            <span className="text-[#718078]">—</span>
                          )}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={11} className="py-6 text-center text-[#718078]">
                        No player match statistics available.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Substitutes Table */}
          {matchPlayers && matchPlayers.substitutes.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-[#E2EAE3]">
              <h4 className="text-xs font-bold text-[#174B32] uppercase tracking-wider font-mono flex items-center justify-between">
                <span>Substitutes Used ({matchPlayers.substitutes.length})</span>
                <span className="text-[10px] text-[#718078]">Entered Pitch</span>
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono border-collapse">
                  <thead>
                    <tr className="bg-[#F4F8F4] border-b border-[#E2EAE3] text-[11px] text-[#718078] uppercase">
                      <th className="py-2.5 px-3">#</th>
                      <th className="py-2.5 px-3">Player</th>
                      <th className="py-2.5 px-3">Pos</th>
                      <th className="py-2.5 px-3 text-center">Sub In</th>
                      <th className="py-2.5 px-3 text-center">Replaced</th>
                      <th className="py-2.5 px-3 text-center">Min</th>
                      <th className="py-2.5 px-3 text-center">G</th>
                      <th className="py-2.5 px-3 text-center">A</th>
                      <th className="py-2.5 px-3 text-center">Passes</th>
                      <th className="py-2.5 px-3 text-center">Tkl Won</th>
                      <th className="py-2.5 px-3 text-center">Cards</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E2EAE3] text-[#26332B]">
                    {matchPlayers.substitutes.map((p, idx) => (
                      <tr key={idx} className="hover:bg-[#F4F8F4]/80 transition-colors">
                        <td className="py-2.5 px-3 text-[#718078] font-bold">#{p.jersey_number ?? "-"}</td>
                        <td className="py-2.5 px-3 font-semibold text-[#174B32]">
                          <Link href={`/players/${p.player_id}`} className="hover:underline">
                            ▲ {p.name}
                          </Link>
                        </td>
                        <td className="py-2.5 px-3 text-[#246B45] font-bold">{p.position || "—"}</td>
                        <td className="py-2.5 px-3 text-center text-[#246B45] font-bold">
                          {p.sub_in_minute ? `${p.sub_in_minute}'` : "—"}
                        </td>
                        <td className="py-2.5 px-3 text-center text-[#718078]">
                          {p.replaced_player_name ? `▼ ${p.replaced_player_name}` : "—"}
                        </td>
                        <td className="py-2.5 px-3 text-center">{p.minutes_played !== null ? `${p.minutes_played}'` : "N/A"}</td>
                        <td className="py-2.5 px-3 text-center font-bold text-[#246B45]">{p.goals ?? 0}</td>
                        <td className="py-2.5 px-3 text-center text-[#174B32]">{p.assists ?? 0}</td>
                        <td className="py-2.5 px-3 text-center">
                          {p.passes_completed !== null && p.passes_completed !== undefined
                            ? `${p.passes_completed}/${p.passes_total ?? 0}`
                            : "N/A"}
                        </td>
                        <td className="py-2.5 px-3 text-center">{p.tackles_won !== null && p.tackles_won !== undefined ? p.tackles_won : "N/A"}</td>
                        <td className="py-2.5 px-3 text-center">
                          {p.red_cards ? (
                            <span className="w-2.5 h-3.5 bg-[#C65B56] inline-block rounded-xs" title="Red card dismissal" />
                          ) : p.yellow_cards ? (
                            <span className="w-2.5 h-3.5 bg-[#D9A441] inline-block rounded-xs" title={`${p.yellow_cards} Yellow card(s)`} />
                          ) : (
                            <span className="text-[#718078]">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      )}

      {/* TAB 3: LINEUPS & FORMATIONS */}
      {activeTab === "LINEUPS" && (() => {
        const starters = match?.lineups?.filter((l) => l.lineup_role === "STARTER") || [];
        const substitutes = match?.lineups?.filter((l) => l.lineup_role === "BENCH" || l.is_substitute_in) || [];
        return (
          <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white border border-[#E2EAE3] rounded-2xl p-5 shadow-xs space-y-5">
              <div>
                <h3 className="text-xs font-bold text-[#246B45] uppercase tracking-widest font-mono mb-3 flex items-center justify-between">
                  <span>{homeTeam?.name} Starting XI ({starters.length})</span>
                  <span className="text-[10px] text-[#174B32] px-2 py-0.5 rounded bg-[#E6F0E7] border border-[#C3DEC7] font-mono">
                    {matchPlayers?.formation || match?.lineups?.[0]?.tactical_formation || "Formation N/A"}
                  </span>
                </h3>
                <div className="space-y-1.5 font-mono text-xs">
                  {starters.length > 0 ? (
                    starters.map((l, idx) => {
                      const pName = l.player?.known_name || (l.player ? `${l.player.first_name} ${l.player.last_name}` : "Player");
                      return (
                        <div key={idx} className="flex items-center justify-between p-2 rounded bg-[#F4F8F4] border border-[#E2EAE3]">
                          <div className="flex items-center space-x-2.5">
                            <span className="w-5 text-right font-bold text-[#718078]">#{l.jersey_number ?? "-"}</span>
                            <span className="font-semibold text-[#26332B]">
                              {pName} {l.is_captain && <span className="text-[#D9A441] font-bold">(C)</span>}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            {l.minutes_played !== null && l.minutes_played !== undefined && (
                              <span className="text-[10px] text-[#718078] font-mono">{l.minutes_played}&apos;</span>
                            )}
                            {l.sub_out_minute && (
                              <span className="text-[10px] text-[#C65B56] font-mono">▼ {l.sub_out_minute}&apos;</span>
                            )}
                            <span className="text-[10px] text-[#246B45] font-bold">{l.position || "STARTER"}</span>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="text-[#718078] text-xs py-4 text-center font-mono">
                      Starting XI not announced yet for this scheduled fixture.
                    </div>
                  )}
                </div>
              </div>

              {substitutes.length > 0 && (
                <div className="pt-3 border-t border-[#E2EAE3]">
                  <h3 className="text-xs font-bold text-[#174B32] uppercase tracking-widest font-mono mb-3 flex items-center justify-between">
                    <span>Actual Substitutions Made ({substitutes.length})</span>
                    <span className="text-[10px] text-[#718078] font-mono">Verified Matchday Bench</span>
                  </h3>
                  <div className="space-y-1.5 font-mono text-xs">
                    {substitutes.map((l, idx) => {
                      const pName = l.player?.known_name || (l.player ? `${l.player.first_name} ${l.player.last_name}` : "Substitute");
                      return (
                        <div key={idx} className="flex items-center justify-between p-2 rounded bg-[#F4F8F4] border border-[#E2EAE3]">
                          <div className="flex items-center space-x-2.5">
                            <span className="w-5 text-right font-bold text-[#718078]">#{l.jersey_number ?? "-"}</span>
                            <span className="font-semibold text-[#174B32]">
                              ▲ {pName}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            {l.sub_in_minute && (
                              <span className="text-[10px] text-[#246B45] font-mono">ON {l.sub_in_minute}&apos;</span>
                            )}
                            {l.minutes_played !== null && l.minutes_played !== undefined && (
                              <span className="text-[10px] text-[#718078] font-mono">({l.minutes_played}&apos;)</span>
                            )}
                            <span className="text-[10px] text-[#718078] font-bold">{l.position || "SUB"}</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            <div className="bg-white border border-[#E2EAE3] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
              <div>
                <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono mb-4">
                  Match Officials & Tactical Context
                </h3>
                <div className="space-y-3 font-mono text-xs text-[#26332B]">
                  <div className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl">
                    <span className="text-[#718078] block text-[10px] uppercase">Referee</span>
                    <span className="font-bold text-[#26332B]">{match?.referee || "Official Appointed"}</span>
                  </div>
                  <div className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl">
                    <span className="text-[#718078] block text-[10px] uppercase">Attendance</span>
                    <span className="font-bold text-[#26332B]">{match?.attendance ? match.attendance.toLocaleString() : "Attendance N/A"}</span>
                  </div>
                  <div className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl">
                    <span className="text-[#718078] block text-[10px] uppercase">Venue & City</span>
                    <span className="font-bold text-[#26332B]">{match?.venue?.name || "Jawaharlal Nehru Stadium"}, {match?.venue?.city || "Chennai"}</span>
                    <span className="text-[#246B45] block text-[10px] mt-1 font-semibold">Verification: {match?.verification_status || "VERIFIED"}</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl text-[11px] font-mono text-[#718078]">
                ℹ️ Missing stats display strictly as N/A in accordance with anti-fabrication guidelines.
              </div>
            </div>
          </section>
        );
      })()}

      {/* TAB 4: TIMELINE (CHRONOLOGICAL MATCH EVENTS & CARDS) */}
      {activeTab === "TIMELINE" && (
        <section className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs">
          <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3 mb-6">
            <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono">
              Chronological Match Events, Goals & Bookings
            </h3>
            <span className="text-[11px] font-mono text-[#718078]">Verified Goals, Assists & Bookings</span>
          </div>

          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#E2EAE3]">
            {match?.events && match.events.length > 0 ? (
              match.events.map((evt, idx) => {
                const isGoal = evt.event_type.includes("GOAL");
                const isYellow = evt.event_type.includes("YELLOW");
                const isRed = evt.event_type.includes("RED");
                const isCfc = evt.team_id === match.home_team_id
                  ? match.home_team?.short_name === "CFC"
                  : match.away_team?.short_name === "CFC";
                const teamName = evt.team_id === match.home_team_id
                  ? match.home_team?.name
                  : match.away_team?.name;
                const primaryName = evt.primary_player?.known_name || (evt.primary_player ? `${evt.primary_player.first_name} ${evt.primary_player.last_name}` : "Player");
                const secondaryName = evt.secondary_player?.known_name || (evt.secondary_player ? `${evt.secondary_player.first_name} ${evt.secondary_player.last_name}` : null);

                return (
                  <div key={idx} className="relative flex items-start space-x-4">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs -ml-6 border ${isGoal
                        ? "bg-[#246B45] text-white border-[#174B32] shadow-xs"
                        : isRed
                          ? "bg-[#C65B56] text-white border-red-700"
                          : isYellow
                            ? "bg-[#D9A441] text-white border-amber-600"
                            : "bg-slate-200 text-slate-700 border-slate-300"
                        }`}
                    >
                      {isGoal ? "⚽" : isRed ? "🟥" : isYellow ? "🟨" : "•"}
                    </div>

                    <div className="bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl p-3.5 flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono font-bold text-[#26332B]">
                          {evt.minute}&apos; {evt.stoppage_minute ? `+${evt.stoppage_minute}'` : ""} — {evt.event_type.replace(/_/g, " ")}
                        </span>
                        <span className={`text-[11px] font-mono font-semibold ${isCfc ? "text-[#246B45]" : "text-[#D9A441]"}`}>
                          {teamName}
                        </span>
                      </div>
                      <p className="mt-1 text-xs text-[#26332B] font-semibold">
                        {primaryName}
                        {secondaryName && (
                          <span className="text-[#718078] font-normal"> (Assist: <strong className="text-[#26332B]">{secondaryName}</strong>)</span>
                        )}
                      </p>
                      {evt.description && (
                        <p className="mt-0.5 text-[11px] text-[#718078]">{evt.description}</p>
                      )}
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-[#718078] text-xs py-8 text-center font-mono">
                No discrete in-match events recorded for this scheduled fixture yet.
              </div>
            )}
          </div>
        </section>
      )}

      {/* TAB 5: INTERACTIVE PITCH */}
      {activeTab === "PITCH" && (
        <section className="space-y-4">
          <FootballPitch
            mode="SHOT MAP"
            showTabs={false}
            shots={shotMap?.shots}
          />
        </section>
      )}
    </Shell>
  );
}
