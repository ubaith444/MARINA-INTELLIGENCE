"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import { fetchMatches, fetchMatchCompare } from "@/lib/api";
import { Match, MatchCompareResponse, MatchCompareMetricItem } from "@/lib/types";
import {
  ArrowLeft,
  ArrowRightLeft,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";

function MatchComparisonContent() {
  const searchParams = useSearchParams();
  const initialMatchA = searchParams.get("match_a") || "";
  const initialMatchB = searchParams.get("match_b") || "";

  const [finishedMatches, setFinishedMatches] = useState<Match[]>([]);
  const [matchAId, setMatchAId] = useState<string>(initialMatchA);
  const [matchBId, setMatchBId] = useState<string>(initialMatchB);

  const [comparison, setComparison] = useState<MatchCompareResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [fetchingMatches, setFetchingMatches] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Load Completed Matches for dropdowns
  useEffect(() => {
    fetchMatches({ status: "FINISHED" })
      .then((data) => {
        setFinishedMatches(data);
        if (data.length >= 2) {
          if (!matchAId) setMatchAId(data[0].id);
          if (!matchBId) setMatchBId(data[1].id);
        }
      })
      .catch((err) => {
        console.error("[MARINA] Failed to fetch finished matches:", err);
      })
      .finally(() => {
        setFetchingMatches(false);
      });
  }, []);

  // 2. Fetch Comparison when Match A and Match B are selected
  useEffect(() => {
    if (!matchAId || !matchBId) return;
    if (matchAId === matchBId) {
      setComparison(null);
      setError("Please select two different matches to compare.");
      return;
    }

    setLoading(true);
    setError(null);

    fetchMatchCompare(matchAId, matchBId)
      .then((res) => {
        setComparison(res);
        setError(null);
      })
      .catch((err) => {
        console.error("[MARINA] Failed to compare matches:", err);
        setError("Unable to generate comparative analysis for selected matches.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [matchAId, matchBId]);

  const swapMatches = () => {
    const temp = matchAId;
    setMatchAId(matchBId);
    setMatchBId(temp);
  };

  const mA = comparison?.match_a;
  const mB = comparison?.match_b;

  return (
    <Shell
      title="Match-to-Match Comparative Intelligence"
      subtitle="Chennaiyin FC ISL 2026–27 • Comparative Tactical Performance Workspace"
    >
      {/* Navigation Link */}
      <div className="flex items-center justify-between">
        <Link
          href="/matches"
          className="text-xs font-semibold text-[#718078] hover:text-[#26332B] flex items-center space-x-1.5 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Match Centre</span>
        </Link>
      </div>

      {/* Match Selector Card */}
      <section className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs">
        <div className="grid grid-cols-1 md:grid-cols-11 gap-4 items-center">
          {/* Match A Selector */}
          <div className="md:col-span-5 space-y-2">
            <label className="text-[11px] font-mono uppercase font-bold text-[#246B45] flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-[#246B45]" />
              <span>Match A (Primary Baseline • Dark Green)</span>
            </label>
            <select
              value={matchAId}
              onChange={(e) => setMatchAId(e.target.value)}
              className="w-full bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl px-3.5 py-2.5 text-xs text-[#26332B] focus:outline-none focus:border-[#246B45] font-mono cursor-pointer"
            >
              {finishedMatches.map((m) => (
                <option key={m.id} value={m.id} className="bg-white text-[#26332B]">
                  Match #{m.match_number}: {m.home_team?.short_name || "CFC"} {m.home_score}–{m.away_score}{" "}
                  {m.away_team?.short_name || "OPP"} ({m.home_team?.slug?.includes("chennai") ? "Home" : "Away"})
                </option>
              ))}
            </select>
          </div>

          {/* Swap Button */}
          <div className="md:col-span-1 flex justify-center py-2 md:py-0">
            <button
              onClick={swapMatches}
              className="p-2.5 rounded-xl bg-[#F4F8F4] border border-[#E2EAE3] hover:border-[#246B45] text-[#26332B] hover:text-[#246B45] transition-colors shadow-xs"
              title="Swap Selected Matches"
            >
              <ArrowRightLeft className="w-4 h-4" />
            </button>
          </div>

          {/* Match B Selector */}
          <div className="md:col-span-5 space-y-2">
            <label className="text-[11px] font-mono uppercase font-bold text-[#D9A441] flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-[#D9A441]" />
              <span>Match B (Comparison Target • Gold/Amber)</span>
            </label>
            <select
              value={matchBId}
              onChange={(e) => setMatchBId(e.target.value)}
              className="w-full bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl px-3.5 py-2.5 text-xs text-[#26332B] focus:outline-none focus:border-[#D9A441] font-mono cursor-pointer"
            >
              {finishedMatches.map((m) => (
                <option key={m.id} value={m.id} className="bg-white text-[#26332B]">
                  Match #{m.match_number}: {m.home_team?.short_name || "CFC"} {m.home_score}–{m.away_score}{" "}
                  {m.away_team?.short_name || "OPP"} ({m.home_team?.slug?.includes("chennai") ? "Home" : "Away"})
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      {/* Error Notice */}
      {error && (
        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 font-mono flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-amber-600" />
          <span>{error}</span>
        </div>
      )}

      {/* Loading Indicator */}
      {loading && (
        <div className="py-20 text-center font-mono text-xs text-[#718078]">
          <div className="animate-spin w-8 h-8 border-2 border-[#246B45] border-t-transparent rounded-full mx-auto mb-3" />
          Computing side-by-side tactical performance deltas...
        </div>
      )}

      {/* Comparison Results */}
      {!loading && comparison && mA && mB && (
        <div className="space-y-6">
          {/* Side-by-Side Match Header Cards */}
          <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Match A Card */}
            <div className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#246B45]">
                  MATCH #{mA.match_number ?? "—"} • {mA.is_home ? "HOME" : "AWAY"}
                </span>
                <span className="px-2 py-0.5 rounded bg-[#E6F0E7] border border-[#C3DEC7] text-[#174B32] text-[10px] font-mono font-bold">
                  {mA.formation || "4-2-3-1"}
                </span>
              </div>
              <div className="flex items-baseline space-x-3">
                <span className="text-2xl font-black text-[#26332B]">vs {mA.opponent_name}</span>
                <span className="text-xl font-bold font-mono text-[#246B45]">
                  {mA.score}
                </span>
              </div>
              <div className="text-[11px] font-mono text-[#718078] flex items-center space-x-3">
                <span>{mA.venue || "Jawaharlal Nehru Stadium (Marina Arena)"}</span>
              </div>
            </div>

            {/* Match B Card */}
            <div className="bg-white border border-[#E2EAE3] rounded-2xl p-6 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-[#D9A441]">
                  MATCH #{mB.match_number ?? "—"} • {mB.is_home ? "HOME" : "AWAY"}
                </span>
                <span className="px-2 py-0.5 rounded bg-amber-50 border border-amber-200 text-amber-800 text-[10px] font-mono font-bold">
                  {mB.formation || "4-2-3-1"}
                </span>
              </div>
              <div className="flex items-baseline space-x-3">
                <span className="text-2xl font-black text-[#26332B]">vs {mB.opponent_name}</span>
                <span className="text-xl font-bold font-mono text-[#D9A441]">
                  {mB.score}
                </span>
              </div>
              <div className="text-[11px] font-mono text-[#718078] flex items-center space-x-3">
                <span>{mB.venue || "Jawaharlal Nehru Stadium (Marina Arena)"}</span>
              </div>
            </div>
          </section>

          {/* Comparative Metrics Table */}
          <section className="bg-white border border-[#E2EAE3] rounded-2xl overflow-hidden shadow-xs">
            <div className="p-4 border-b border-[#E2EAE3] flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-[#26332B] uppercase tracking-widest font-mono">
                  Side-by-Side Tactical Metrics &amp; Deltas
                </h3>
                <p className="text-[11px] text-[#718078]">
                  Direct match-to-match performance variances (Delta = Match A − Match B).
                </p>
              </div>
              <Badge variant="green">ISL 2026–27 Verified</Badge>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#F4F8F4] border-b border-[#E2EAE3] text-[10px] uppercase text-[#718078] tracking-wider">
                  <tr>
                    <th className="py-3 px-4 w-1/4 text-[#246B45] font-bold">
                      Match #{mA.match_number} (vs {mA.opponent_name?.split(" ")[0]})
                    </th>
                    <th className="py-3 px-4 w-1/3 text-center text-[#718078] font-bold">Metric Category</th>
                    <th className="py-3 px-4 w-1/4 text-right text-[#D9A441] font-bold">
                      Match #{mB.match_number} (vs {mB.opponent_name?.split(" ")[0]})
                    </th>
                    <th className="py-3 px-4 w-1/6 text-right text-[#174B32] font-bold">Δ (A − B)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2EAE3]">
                  {comparison.comparisons.map((row: MatchCompareMetricItem, idx: number) => {
                    const deltaVal = row.delta;
                    const isNum = typeof deltaVal === "number";
                    const deltaStr = isNum
                      ? deltaVal > 0
                        ? `+${deltaVal}`
                        : `${deltaVal}`
                      : deltaVal !== null && deltaVal !== undefined
                      ? String(deltaVal)
                      : "—";

                    const deltaColor =
                      isNum && deltaVal > 0
                        ? "text-[#246B45] font-bold"
                        : isNum && deltaVal < 0
                        ? "text-[#D9A441] font-bold"
                        : "text-[#718078]";

                    return (
                      <tr key={idx} className="hover:bg-[#F4F8F4]/80 transition-colors">
                        <td className="py-3 px-4 font-bold text-[#26332B]">
                          {row.match_a_value !== null && row.match_a_value !== undefined
                            ? `${row.match_a_value}${row.unit ? ` ${row.unit}` : ""}`
                            : "N/A"}
                        </td>
                        <td className="py-3 px-4 text-center text-[#718078] font-semibold">{row.label}</td>
                        <td className="py-3 px-4 text-right font-bold text-[#26332B]">
                          {row.match_b_value !== null && row.match_b_value !== undefined
                            ? `${row.match_b_value}${row.unit ? ` ${row.unit}` : ""}`
                            : "N/A"}
                        </td>
                        <td className={`py-3 px-4 text-right ${deltaColor}`}>{deltaStr}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>
        </div>
      )}
    </Shell>
  );
}

export default function MatchComparisonPage() {
  return (
    <Suspense
      fallback={
        <Shell
          title="Match-to-Match Comparative Intelligence"
          subtitle="Loading match comparison engine..."
        >
          <div className="py-24 text-center text-xs font-mono text-[#718078]">
            <div className="animate-spin w-8 h-8 border-2 border-[#246B45] border-t-transparent rounded-full mx-auto mb-3" />
            Loading Match Comparison Workspace...
          </div>
        </Shell>
      }
    >
      <MatchComparisonContent />
    </Suspense>
  );
}
