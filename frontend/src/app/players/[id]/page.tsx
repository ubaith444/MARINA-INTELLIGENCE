"use client";

import React, { useEffect, useState } from "react";
import { notFound, useParams } from "next/navigation";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import KpiCard from "@/components/ui/KpiCard";
import RadarChart from "@/components/charts/RadarChart";
import { fetchPlayerById, fetchPlayerPerformance, fetchPlayerMatches } from "@/lib/api";
import { Player, PlayerPerformance, PlayerMatchHistoryItem, RadarComparisonItem } from "@/lib/types";
import {
  ArrowLeft,
  Activity,
  Award,
  AlertCircle,
  FileCheck2,
  Info,
  Shield,
} from "lucide-react";
import Link from "next/link";

export default function PlayerProfilePage() {
  const params = useParams();
  const playerId = params?.id as string;

  if (playerId === "compare") {
    notFound();
  }

  const [player, setPlayer] = useState<Player | null>(null);
  const [performance, setPerformance] = useState<PlayerPerformance | null>(null);
  const [matches, setMatches] = useState<PlayerMatchHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    Promise.all([
      fetchPlayerById(playerId).catch(() => null),
      fetchPlayerPerformance(playerId).catch(() => null),
      fetchPlayerMatches(playerId).catch(() => []),
    ])
      .then(([pData, perfData, matchData]) => {
        if (!isMounted) return;
        if (pData) setPlayer(pData);
        if (perfData) setPerformance(perfData);
        if (matchData) setMatches(matchData);
        if (!pData && !perfData) {
          setError(`Player not found in active database.`);
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.error("[MARINA] Error loading player profile:", err);
          setError("Failed to load player profile.");
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [playerId]);

  const p = performance;
  const p90 = p?.per_90;
  const raw = p?.raw_totals;

  const displayName = player?.known_name || (player ? `${player.first_name} ${player.last_name}` : p?.name || "Player Profile");
  const positionStr = (player?.primary_position || p?.primary_position || "").toUpperCase();
  const isGk = positionStr.includes("GK") || positionStr.includes("GOALKEEPER");
  const appearances = p?.appearances ?? 0;
  const minutes = p?.minutes_played ?? 0;
  const hasPlayed = appearances > 0 || minutes > 0;
  const hasSufficientMin = p90?.has_sufficient_minutes ?? false;

  const LEADERSHIP_PLAYER_IDS = new Set([
    "a378e4c6-f1f1-4304-9a7f-6ac754f2e014", // Nuno Reis
    "77bee327-2929-4d41-9329-e2f2bd18c88e", // P. C. Laldinpuia
    "3a79ed6c-7620-44aa-8568-b1f2b3650062", // Nikola Stojanović
    "ee362980-f66b-417d-8abb-c4004b703320", // Samik Mitra
    "f1f1efd2-6b7f-4f22-aba3-2bf79404a683", // Mohammad Nawaz
  ]);
  const isLeadership = Boolean(
    player?.is_leadership_group || p?.is_leadership_group || LEADERSHIP_PLAYER_IDS.has(playerId)
  );

  // Radar chart calculation: position adaptive
  let radarItems: RadarComparisonItem[] = [];
  if (isGk) {
    const savePctVal = raw?.save_percentage ?? 0;
    const savesP90 = hasSufficientMin && minutes > 0 ? ((raw?.saves ?? 0) / minutes) * 90 : 0;
    const gcP90 = hasSufficientMin && minutes > 0 ? ((raw?.goals_conceded ?? 0) / minutes) * 90 : 0;
    const passAcc = raw?.pass_accuracy_pct ?? 0;
    const csRatio = appearances > 0 ? ((raw?.clean_sheets ?? 0) / appearances) * 100 : 0;

    radarItems = [
      { dimension: "Shot Stopping", player_a_score: Math.min(100, Math.round((savePctVal / 80.0) * 100)), player_b_score: 65 },
      { dimension: "Save Volume", player_a_score: Math.min(100, Math.round((savesP90 / 4.5) * 100)), player_b_score: 60 },
      { dimension: "Goal Prevention", player_a_score: Math.max(0, Math.min(100, Math.round(((2.5 - gcP90) / 2.5) * 100))), player_b_score: 55 },
      { dimension: "Distribution", player_a_score: Math.min(100, Math.round((passAcc / 85.0) * 100)), player_b_score: 50 },
      { dimension: "Clean Sheets", player_a_score: Math.min(100, Math.round((csRatio / 40.0) * 100)), player_b_score: 40 },
    ];
  } else {
    radarItems = [
      { dimension: "Scoring Threat", player_a_score: hasSufficientMin ? Math.min(100, Math.round(((p90?.goals_per_90 || 0) / 0.8) * 100)) : 0, player_b_score: 45 },
      { dimension: "Shot Volume", player_a_score: hasSufficientMin ? Math.min(100, Math.round(((p90?.shots_per_90 || 0) / 3.5) * 100)) : 0, player_b_score: 40 },
      { dimension: "Playmaking", player_a_score: hasSufficientMin ? Math.min(100, Math.round(((p90?.assists_per_90 || 0) / 0.5) * 100)) : 0, player_b_score: 35 },
      { dimension: "Passing Output", player_a_score: hasSufficientMin ? Math.min(100, Math.round(((p90?.passes_completed_per_90 || 0) / 55.0) * 100)) : 0, player_b_score: 50 },
      { dimension: "Ball Winning", player_a_score: hasSufficientMin ? Math.min(100, Math.round((((p90?.tackles_per_90 || 0) + (p90?.interceptions_per_90 || 0)) / 4.5) * 100)) : 0, player_b_score: 30 },
    ];
  }

  if (loading) {
    return (
      <Shell title="Player Profile" subtitle="Loading individual player intelligence...">
        <div className="py-24 text-center font-mono text-xs text-[#718078]">
          <div className="animate-spin w-8 h-8 border-2 border-[#246B45] border-t-transparent rounded-full mx-auto mb-3" />
          Loading verified player performance profile...
        </div>
      </Shell>
    );
  }

  if (error || !player) {
    return (
      <Shell title="Player Profile" subtitle="Profile not found">
        <div className="bg-white border border-[#E2EAE3] rounded-2xl p-8 text-center space-y-4 max-w-lg mx-auto shadow-xs">
          <AlertCircle className="w-10 h-10 text-[#C65B56] mx-auto" />
          <h2 className="text-lg font-bold text-[#26332B]">Player Not Found</h2>
          <p className="text-xs text-[#718078] font-mono">{error || "The requested player record was not found in the 2026–27 squad database."}</p>
          <Link
            href="/players"
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-[#246B45] hover:bg-[#174B32] text-white text-xs font-semibold shadow-xs"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Return to Player Directory</span>
          </Link>
        </div>
      </Shell>
    );
  }

  return (
    <Shell
      title={`Player Profile • ${displayName}`}
      subtitle="Chennaiyin FC First Team Squad • Individual Analytics Engine"
    >
      {/* Navigation & Action Bar */}
      <div className="flex items-center justify-between">
        <Link
          href="/players"
          className="text-xs font-semibold text-[#718078] hover:text-[#26332B] flex items-center space-x-1.5 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Player Directory</span>
        </Link>
      </div>

      {/* Profile Header Banner */}
      <section className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="flex items-center space-x-5">
          <div className="w-16 h-16 rounded-2xl bg-[#246B45] border border-[#174B32] flex items-center justify-center font-black font-mono text-2xl text-white shadow-xs">
            {player.jersey_number ? `#${player.jersey_number}` : displayName.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="flex items-center space-x-2 text-xs font-mono font-bold text-[#246B45] mb-1">
              <span>{positionStr.replace("_", " ")}</span>
              <span>•</span>
              {player.nationality === "India" || player.nationality?.toLowerCase().includes("india") ? (
                <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7]">
                  <span>🇮🇳</span>
                  <span>Domestic Player (India)</span>
                </span>
              ) : (
                <span>✈️ {player.nationality}</span>
              )}
              {player.jersey_number && (
                <>
                  <span>•</span>
                  <span>Squad #{player.jersey_number}</span>
                </>
              )}
              {isLeadership && (
                <>
                  <span>•</span>
                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7] font-bold text-[10px]">
                    <Shield className="w-3 h-3 text-[#246B45]" />
                    <span>Leadership Group</span>
                  </span>
                </>
              )}
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-[#26332B] tracking-tight">
              {displayName}
            </h2>
            <p className="text-[#718078] text-xs mt-0.5 font-mono">
              Chennaiyin FC • Indian Super League 2026–27 Official Roster
            </p>
          </div>
        </div>

        {/* Sample Size / Appearance Validation Badge */}
        <div className="bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl p-3.5 flex flex-col items-start md:items-end text-xs font-mono">
          <span className="text-[10px] text-[#718078] uppercase tracking-widest mb-1 font-semibold">
            Competitive Sample Standard
          </span>
          {hasSufficientMin ? (
            <span className="inline-flex items-center space-x-1.5 text-[#246B45] font-bold">
              <span className="w-2 h-2 rounded-full bg-[#246B45]" />
              <span>Normalized Per-90 Valid (≥45m)</span>
            </span>
          ) : hasPlayed ? (
            <span className="inline-flex items-center space-x-1.5 text-[#D9A441] font-bold">
              <span className="w-2 h-2 rounded-full bg-[#D9A441]" />
              <span>Limited Minutes (&lt;45m Sample)</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 text-[#718078] font-bold">
              <span className="w-2 h-2 rounded-full bg-[#718078]" />
              <span>Unplayed Squad Member (0 Min)</span>
            </span>
          )}
          <span className="text-[10px] text-[#718078] mt-0.5">
            Total Minutes: {p?.minutes_played ?? 0}&apos; across {p?.appearances ?? 0} appearances
          </span>
        </div>
      </section>

      {/* Leadership Group Verification Card */}
      {isLeadership && (
        <div className="bg-[#FFFFFF] border border-[#C3DEC7] rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs font-mono shadow-xs">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7] flex items-center justify-center shrink-0">
              <Shield className="w-4 h-4 text-[#246B45]" />
            </div>
            <div>
              <span className="font-bold text-[#174B32] block">
                Chennaiyin FC Leadership Group • ISL 2026–27
              </span>
              <p className="text-[11px] text-[#718078] font-sans">
                {displayName} is one of five verified senior players comprising Chennaiyin FC&apos;s 2026–27 squad leadership group.
              </p>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7] shrink-0 self-start sm:self-auto">
            Senior Leadership Council
          </span>
        </div>
      )}

      {/* Unplayed Squad Member Notice if 0 Minutes */}
      {!hasPlayed && (
        <div className="bg-[#E6F0E7]/70 border border-[#C3DEC7] rounded-xl p-4 flex items-start space-x-3 text-xs text-[#174B32] font-mono">
          <Info className="w-5 h-5 text-[#246B45] shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-bold text-[#174B32]">Registered Squad Member — Unplayed in Matches 1–5</p>
            <p className="text-[#26332B] text-[11px]">
              {displayName} is an official member of Chennaiyin FC&apos;s 2026–27 squad but has not made an appearance in the first 5 completed ISL fixtures. To uphold zero-fabrication data integrity, playing statistics are recorded as 0 and rate metrics are marked N/A.
            </p>
          </div>
        </div>
      )}

      {/* Squad Rankings Ribbon (When Player Has Played) */}
      {hasPlayed && p?.rankings && (
        <section className="bg-white border border-[#E2EAE3] rounded-2xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-3 border-b border-[#E2EAE3] pb-2">
            <span className="text-xs font-mono font-bold text-[#26332B] uppercase tracking-wider flex items-center gap-1.5">
              <Award className="w-4 h-4 text-[#D9A441]" />
              Squad Rankings (ISL 2026–27)
            </span>
            <span className="text-[10px] font-mono text-[#718078]">45 Registered Squad Members (32 Domestic, 13 Overseas)</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center font-mono">
            <div className="bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl p-3">
              <span className="text-[10px] text-[#718078] block">Goals Rank</span>
              <span className="text-lg font-bold text-[#246B45]">
                #{p.rankings.goals?.rank ?? "—"}{" "}
                <span className="text-[10px] text-[#718078] font-normal">/ {p.rankings.goals?.total ?? 45}</span>
              </span>
            </div>
            <div className="bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl p-3">
              <span className="text-[10px] text-[#718078] block">Minutes Rank</span>
              <span className="text-lg font-bold text-[#174B32]">
                #{p.rankings.minutes?.rank ?? "—"}{" "}
                <span className="text-[10px] text-[#718078] font-normal">/ {p.rankings.minutes?.total ?? 45}</span>
              </span>
            </div>
            <div className="bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl p-3">
              <span className="text-[10px] text-[#718078] block">Assists Rank</span>
              <span className="text-lg font-bold text-[#246B45]">
                #{p.rankings.assists?.rank ?? "—"}{" "}
                <span className="text-[10px] text-[#718078] font-normal">/ {p.rankings.assists?.total ?? 45}</span>
              </span>
            </div>
            <div className="bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl p-3">
              <span className="text-[10px] text-[#718078] block">Shots Rank</span>
              <span className="text-lg font-bold text-[#D9A441]">
                #{p.rankings.shots?.rank ?? "—"}{" "}
                <span className="text-[10px] text-[#718078] font-normal">/ {p.rankings.shots?.total ?? 45}</span>
              </span>
            </div>
          </div>
        </section>
      )}

      {/* Recent Form Strip (Last 5 Competitive Matches) */}
      {hasPlayed && p?.last_five_matches && p.last_five_matches.length > 0 && (
        <section className="bg-white border border-[#E2EAE3] rounded-2xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-3 border-b border-[#E2EAE3] pb-2">
            <span className="text-xs font-mono font-bold text-[#26332B] uppercase tracking-wider flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-[#246B45]" />
              Recent Form Strip (Last {p.last_five_matches.length} Matches)
            </span>
            <span className="text-[10px] font-mono text-[#718078]">Official Matchdays</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-2.5 font-mono text-xs">
            {p.last_five_matches.map((m, idx) => (
              <div
                key={idx}
                className="bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl p-2.5 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-[#718078] font-bold">M#{m.match_number} vs {m.opponent_short}</span>
                  <span
                    className={`text-[9px] px-1 py-0.2 rounded font-bold ${
                      m.is_home ? "bg-[#E6F0E7] text-[#174B32]" : "bg-sky-50 text-sky-800"
                    }`}
                  >
                    {m.is_home ? "H" : "A"}
                  </span>
                </div>
                <div className="flex items-center justify-between my-1">
                  <span className="text-[#26332B] font-bold">{m.score}</span>
                  <span className="text-[#718078] text-[11px]">{m.minutes_played}&apos;</span>
                </div>
                <div className="flex items-center justify-between text-[10px] text-[#718078] pt-1 border-t border-[#E2EAE3]">
                  <span className="text-[#246B45] font-semibold">{m.goals > 0 ? `${m.goals}G` : ""} {m.assists > 0 ? `${m.assists}A` : ""}</span>
                  <span>{m.started ? "Starter" : "Sub"}</span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Position-Specific Key Performance Indicators */}
      {isGk ? (
        <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
          <KpiCard label="Appearances" value={p?.appearances ?? 0} subtext={`Starts: ${p?.starts ?? 0}`} accent="slate" />
          <KpiCard label="Minutes Played" value={`${p?.minutes_played ?? 0}'`} subtext="Official game duration" accent="blue" />
          <KpiCard label="Saves" value={raw?.saves !== null && raw?.saves !== undefined ? raw.saves : (hasPlayed ? 0 : "N/A")} subtext="Shots stopped" accent="green" />
          <KpiCard label="Clean Sheets" value={raw?.clean_sheets !== null && raw?.clean_sheets !== undefined ? raw.clean_sheets : (hasPlayed ? 0 : "N/A")} subtext="Shutouts recorded" accent="blue" />
          <KpiCard label="Goals Conceded" value={raw?.goals_conceded !== null && raw?.goals_conceded !== undefined ? raw.goals_conceded : (hasPlayed ? 0 : "N/A")} subtext="Total conceded" accent="amber" />
          <KpiCard
            label="Save Percentage"
            value={raw?.save_percentage !== null && raw?.save_percentage !== undefined ? `${raw.save_percentage}%` : "N/A"}
            subtext={hasSufficientMin ? "Based on shots on target faced" : "Requires ≥45m"}
            accent="slate"
          />
        </section>
      ) : (
        <section className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
          <KpiCard label="Appearances" value={p?.appearances ?? 0} subtext={`Starts: ${p?.starts ?? 0} • Sub: ${p?.substitute_appearances ?? 0}`} accent="slate" />
          <KpiCard label="Minutes Played" value={`${p?.minutes_played ?? 0}'`} subtext="Official game duration" accent="blue" />
          <KpiCard label="Goals Scored" value={raw?.goals ?? 0} subtext="Total ISL goals" accent="green" />
          <KpiCard label="Assists" value={raw?.assists ?? 0} subtext="Goal assists" accent="blue" />
          <KpiCard label="Shots (Target)" value={raw?.shots_total !== null && raw?.shots_total !== undefined ? `${raw.shots_on_target ?? 0} / ${raw.shots_total}` : "N/A"} subtext="Target / Total" accent="blue" />
          <KpiCard label="Tackles Won" value={raw?.tackles_won !== null && raw?.tackles_won !== undefined ? raw.tackles_won : "N/A"} subtext={raw?.interceptions ? `${raw.interceptions} Interceptions` : "Defensive duel"} accent="slate" />
        </section>
      )}

      {/* Detailed Per-90 Metrics & Tactical Radar */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Standardized Per-90 Rates Card */}
        <div className="lg:col-span-2 bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
            <div>
              <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono">
                {isGk ? "Standardized Goalkeeper Analytics" : "Standardized Per-90 Statistics"}
              </h3>
              <p className="text-[11px] text-[#718078]">
                Rate metrics normalized per 90 minutes played to eliminate playing-time distortion.
              </p>
            </div>
            {hasSufficientMin ? (
              <Badge variant="green">Per-90 Normalized</Badge>
            ) : (
              <Badge variant="slate">N/A (&lt;45m Sample)</Badge>
            )}
          </div>

          {!hasSufficientMin && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 font-mono flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-amber-600" />
              <span>
                {hasPlayed
                  ? "Player has fewer than 45 total competitive minutes. Per-90 rate metrics are marked N/A to prevent misleading statistical projection."
                  : "Player has not logged any match minutes. Rate metrics are unavailable (N/A)."}
              </span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
            {isGk
              ? [
                  { label: "Save Percentage", val: raw?.save_percentage !== null && raw?.save_percentage !== undefined ? `${raw.save_percentage}%` : "N/A", benchmark: "75.0% Elite Benchmark" },
                  {
                    label: "Saves Per 90",
                    val: hasSufficientMin && minutes > 0 && raw?.saves !== null && raw?.saves !== undefined
                      ? (((raw.saves) / minutes) * 90).toFixed(2)
                      : "N/A",
                    benchmark: "4.00 High Workload",
                  },
                  {
                    label: "Goals Conceded Per 90",
                    val: hasSufficientMin && minutes > 0 && raw?.goals_conceded !== null && raw?.goals_conceded !== undefined
                      ? (((raw.goals_conceded) / minutes) * 90).toFixed(2)
                      : "N/A",
                    benchmark: "1.00 Elite Defense",
                  },
                  {
                    label: "Clean Sheet Rate",
                    val: appearances > 0 && raw?.clean_sheets !== null && raw?.clean_sheets !== undefined
                      ? `${(((raw.clean_sheets) / appearances) * 100).toFixed(1)}%`
                      : "N/A",
                    benchmark: "35.0% Starting CS",
                  },
                  { label: "Pass Accuracy", val: raw?.pass_accuracy_pct !== null && raw?.pass_accuracy_pct !== undefined ? `${raw.pass_accuracy_pct}%` : "N/A", benchmark: "75.0% Build-up Base" },
                  {
                    label: "Passes Completed Per 90",
                    val: hasSufficientMin && minutes > 0 && raw?.passes_completed !== null && raw?.passes_completed !== undefined
                      ? (((raw.passes_completed) / minutes) * 90).toFixed(2)
                      : "N/A",
                    benchmark: "25.0 Distribution",
                  },
                ].map((metric, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl flex items-center justify-between font-mono"
                  >
                    <div>
                      <span className="text-[11px] font-sans font-semibold text-[#26332B] block">
                        {metric.label}
                      </span>
                      <span className="text-[10px] text-[#718078]">Benchmark: {metric.benchmark}</span>
                    </div>
                    <span className="text-sm font-bold text-[#174B32]">{metric.val}</span>
                  </div>
                ))
              : [
                  { label: "Goals Per 90", val: hasSufficientMin && p90?.goals_per_90 !== null && p90?.goals_per_90 !== undefined ? p90.goals_per_90.toFixed(2) : "N/A", benchmark: "0.80 Elite Striker" },
                  { label: "Assists Per 90", val: hasSufficientMin && p90?.assists_per_90 !== null && p90?.assists_per_90 !== undefined ? p90.assists_per_90.toFixed(2) : "N/A", benchmark: "0.50 Elite Playmaker" },
                  { label: "Goal Contributions Per 90", val: hasSufficientMin && p90?.goal_contributions_per_90 !== null && p90?.goal_contributions_per_90 !== undefined ? p90.goal_contributions_per_90.toFixed(2) : "N/A", benchmark: "1.20 Elite Forward" },
                  { label: "Shots Per 90", val: hasSufficientMin && p90?.shots_per_90 !== null && p90?.shots_per_90 !== undefined ? p90.shots_per_90.toFixed(2) : "N/A", benchmark: "3.50 High Volume" },
                  { label: "Passes Completed Per 90", val: hasSufficientMin && p90?.passes_completed_per_90 !== null && p90?.passes_completed_per_90 !== undefined ? p90.passes_completed_per_90.toFixed(2) : "N/A", benchmark: "55.0 Central Midfield" },
                  { label: "Tackles Won Per 90", val: hasSufficientMin && p90?.tackles_per_90 !== null && p90?.tackles_per_90 !== undefined ? p90.tackles_per_90.toFixed(2) : "N/A", benchmark: "3.20 Ball Winner" },
                  { label: "Interceptions Per 90", val: hasSufficientMin && p90?.interceptions_per_90 !== null && p90?.interceptions_per_90 !== undefined ? p90.interceptions_per_90.toFixed(2) : "N/A", benchmark: "2.00 Elite Read" },
                  { label: "Expected Goals Per 90", val: hasSufficientMin && p90?.expected_goals_per_90 !== null && p90?.expected_goals_per_90 !== undefined ? p90.expected_goals_per_90.toFixed(2) : "N/A", benchmark: "0.65 Primary Threat" },
                ].map((metric, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl flex items-center justify-between font-mono"
                  >
                    <div>
                      <span className="text-[11px] font-sans font-semibold text-[#26332B] block">
                        {metric.label}
                      </span>
                      <span className="text-[10px] text-[#718078]">Benchmark: {metric.benchmark}</span>
                    </div>
                    <span className="text-sm font-bold text-[#246B45]">{metric.val}</span>
                  </div>
                ))}
          </div>
        </div>

        {/* 5-Dimension Tactical Radar */}
        <div className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono mb-1">
              {isGk ? "Goalkeeper Tactical Radar" : "5-Dimension Tactical Radar"}
            </h3>
            <p className="text-[11px] text-[#718078] mb-4">
              Normalized tactical dimensional profile (0–100 scale vs ISL benchmarks)
            </p>
            <RadarChart dimensions={radarItems} playerAName={displayName} />
          </div>

          <div className="mt-4 pt-3 border-t border-[#E2EAE3] text-[10px] text-[#718078] font-mono text-center">
            {hasSufficientMin
              ? "Calculated against ISL 2026–27 competitive match benchmarks."
              : "Radar dimensions require ≥45 minutes of match data."}
          </div>
        </div>
      </section>

      {/* Verified Match-by-Match Performance History */}
      <section className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
          <div>
            <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono">
              Verified 2026–27 Match Performance Log
            </h3>
            <p className="text-[11px] text-[#718078]">
              Per-match appearances and statistics ingested from official ISL matchday logs.
            </p>
          </div>
          <Badge variant="green">{matches.length} Matches Logged</Badge>
        </div>

        {matches.length === 0 ? (
          <div className="py-12 text-center text-xs text-[#718078] font-mono space-y-2">
            <p>No match appearances recorded yet across the 5 completed fixtures.</p>
            <p className="text-[11px] text-[#718078]">
              Appearances are logged dynamically upon official match completion and verified team sheet ingestion.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="bg-[#F4F8F4] border-b border-[#E2EAE3] text-[10px] text-[#718078] uppercase tracking-wider">
                  <th className="py-3 px-3">MW</th>
                  <th className="py-3 px-3">Date</th>
                  <th className="py-3 px-3">Opponent</th>
                  <th className="py-3 px-3">Venue</th>
                  <th className="py-3 px-3">Result</th>
                  <th className="py-3 px-3">Role</th>
                  <th className="py-3 px-3 text-right">Min</th>
                  {isGk ? (
                    <>
                      <th className="py-3 px-3 text-center">Saves</th>
                      <th className="py-3 px-3 text-center">Conceded</th>
                      <th className="py-3 px-3 text-center">Clean Sheet</th>
                    </>
                  ) : (
                    <>
                      <th className="py-3 px-3 text-right">G</th>
                      <th className="py-3 px-3 text-right">A</th>
                      <th className="py-3 px-3 text-right">Shots (OT/Tot)</th>
                    </>
                  )}
                  <th className="py-3 px-3 text-right">Passes (Acc/Tot)</th>
                  <th className="py-3 px-3 text-center">Cards</th>
                  <th className="py-3 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2EAE3]">
                {matches.map((m) => (
                  <tr key={m.match_id} className="hover:bg-[#F4F8F4]/80 transition-colors">
                    <td className="py-3 px-3 font-bold text-[#174B32]">#{m.match_number ?? "—"}</td>
                    <td className="py-3 px-3 text-[#718078]">
                      {m.match_date ? new Date(m.match_date).toLocaleDateString("en-GB", { day: "2-digit", month: "short" }) : "—"}
                    </td>
                    <td className="py-3 px-3 font-semibold text-[#26332B]">
                      {m.opponent_name}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${m.is_home ? "bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7]" : "bg-sky-50 text-sky-800 border border-sky-200"}`}>
                        {m.is_home ? "HOME" : "AWAY"}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center space-x-1 px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        m.result === "W" ? "bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7]" :
                        m.result === "D" ? "bg-amber-50 text-amber-800 border border-amber-200" :
                        m.result === "L" ? "bg-rose-50 text-rose-800 border border-rose-200" : "bg-slate-100 text-slate-700"
                      }`}>
                        <span>{m.result || "—"}</span>
                        <span>({m.cfc_score}–{m.opponent_score})</span>
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[#26332B]">
                      {m.lineup_role === "SUBSTITUTE" ? (
                        <span className="text-[#D9A441] font-semibold">SUBSTITUTE</span>
                      ) : (
                        <span>{m.lineup_role}</span>
                      )}
                      {m.is_captain && <span className="text-[#D9A441] font-bold ml-1">(C)</span>}
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-[#26332B]">{m.minutes_played}&apos;</td>
                    {isGk ? (
                      <>
                        <td className="py-3 px-3 text-center font-bold text-[#D9A441]">{m.saves ?? 0}</td>
                        <td className="py-3 px-3 text-center font-bold text-[#C65B56]">{m.goals_conceded ?? m.opponent_score ?? 0}</td>
                        <td className="py-3 px-3 text-center">
                          {m.clean_sheet ? (
                            <span className="px-1.5 py-0.5 rounded bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7] text-[10px] font-bold">YES</span>
                          ) : (
                            <span className="text-[#718078]">NO</span>
                          )}
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="py-3 px-3 text-right font-bold text-[#246B45]">{m.goals}</td>
                        <td className="py-3 px-3 text-right font-bold text-[#174B32]">{m.assists}</td>
                        <td className="py-3 px-3 text-right text-[#26332B]">
                          {m.shots_total !== null && m.shots_total !== undefined ? `${m.shots_on_target ?? 0}/${m.shots_total}` : "N/A"}
                        </td>
                      </>
                    )}
                    <td className="py-3 px-3 text-right text-[#26332B]">
                      {m.passes_total !== null && m.passes_total !== undefined ? `${m.passes_completed ?? 0}/${m.passes_total}` : "N/A"}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {m.red_cards > 0 ? (
                        <span className="w-2.5 h-3.5 bg-[#C65B56] inline-block rounded-xs" title="Red card dismissal" />
                      ) : m.yellow_cards > 0 ? (
                        <span className="w-2.5 h-3.5 bg-[#D9A441] inline-block rounded-xs" title={`${m.yellow_cards} Yellow card(s)`} />
                      ) : (
                        <span className="text-[#718078]">—</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <Link
                        href={`/matches/${m.match_id}`}
                        className="text-xs text-[#246B45] hover:text-[#174B32] hover:underline font-semibold"
                      >
                        Match Center →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Data Completeness & Source Information Card */}
      <section className="bg-white border border-[#E2EAE3] rounded-2xl p-5 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4 font-mono text-xs">
        <div className="flex items-start space-x-3">
          <FileCheck2 className="w-5 h-5 text-[#246B45] shrink-0 mt-0.5" />
          <div>
            <div className="font-bold text-[#26332B]">Data Integrity & Verification Provenance</div>
            <p className="text-[11px] text-[#718078] mt-0.5">
              Source: Official Indian Super League 2026–27 Match Feeds • Dual-entry verified against official referee reports.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-[11px]">
          <div className="px-2.5 py-1 rounded bg-[#F4F8F4] border border-[#E2EAE3] text-[#26332B]">
            <span className="text-[#718078]">Optical Tracking:</span> <span className="text-[#D9A441] font-bold">N/A</span>
          </div>
          <div className="px-2.5 py-1 rounded bg-[#F4F8F4] border border-[#E2EAE3] text-[#26332B]">
            <span className="text-[#718078]">GPS Sprints:</span> <span className="text-[#D9A441] font-bold">N/A</span>
          </div>
          <div className="px-2.5 py-1 rounded bg-[#E6F0E7] border border-[#C3DEC7] text-[#174B32]">
            <span className="text-[#718078]">Status:</span> <span className="text-[#246B45] font-bold">VERIFIED</span>
          </div>
        </div>
      </section>
    </Shell>
  );
}
