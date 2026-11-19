"use client";

import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import { fetchMatches, fetchSeasonOverview } from "@/lib/api";
import { Match, SeasonOverviewResponse } from "@/lib/types";
import {
  MapPin,
  ArrowRight,
  Filter,
  Search,
  RotateCcw,
  Scale,
} from "lucide-react";
import Link from "next/link";

export default function MatchCentrePage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [overview, setOverview] = useState<SeasonOverviewResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [venueFilter, setVenueFilter] = useState<string>("ALL");
  const [matchweekFilter, setMatchweekFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    Promise.all([
      fetchMatches().catch(() => []),
      fetchSeasonOverview().catch(() => null),
    ]).then(([matchesData, overviewData]) => {
      if (!isMounted) return;
      setMatches(matchesData || []);
      setOverview(overviewData);
      setLoading(false);
    });

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredMatches = matches.filter((m) => {
    // Status filter
    if (statusFilter !== "ALL") {
      if (statusFilter === "PLAYED" && m.match_status !== "FINISHED") return false;
      if (statusFilter === "UPCOMING" && m.match_status !== "SCHEDULED" && m.match_status !== "TIMED") return false;
      if (statusFilter === "POSTPONED" && m.match_status !== "POSTPONED") return false;
    }

    // Home / Away filter
    const isHome = m.home_team?.slug === "chennaiyin-fc" || m.home_team?.short_name === "CFC";
    if (venueFilter === "HOME" && !isHome) return false;
    if (venueFilter === "AWAY" && isHome) return false;

    // Matchweek filter
    const mw = m.matchweek || m.match_number;
    if (matchweekFilter !== "ALL" && mw !== Number(matchweekFilter)) return false;

    // Search query by opponent
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const oppName = isHome ? m.away_team?.name?.toLowerCase() || "" : m.home_team?.name?.toLowerCase() || "";
      const oppShort = isHome ? m.away_team?.short_name?.toLowerCase() || "" : m.home_team?.short_name?.toLowerCase() || "";
      if (!oppName.includes(q) && !oppShort.includes(q)) return false;
    }

    return true;
  });

  const resetFilters = () => {
    setStatusFilter("ALL");
    setVenueFilter("ALL");
    setMatchweekFilter("ALL");
    setSearchQuery("");
  };

  return (
    <Shell
      title="Interactive Match Centre"
      subtitle="Indian Super League 2026–27 • Complete 24 Fixtures, Results & Tactical Reports"
    >
      {/* Season Progress Ribbon */}
      {overview && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="bg-white border border-[#E2EAE3] rounded-2xl p-4 shadow-xs flex flex-col justify-between">
            <span className="text-[10px] text-[#718078] font-mono uppercase font-bold tracking-wider">
              Fixtures Played
            </span>
            <div className="flex items-baseline space-x-1.5 mt-1 font-mono">
              <span className="text-2xl font-black text-[#26332B]">{overview.matches_played}</span>
              <span className="text-xs text-[#718078]">/ {overview.total_fixtures}</span>
            </div>
          </div>

          <div className="bg-white border border-[#E2EAE3] rounded-2xl p-4 shadow-xs flex flex-col justify-between">
            <span className="text-[10px] text-[#718078] font-mono uppercase font-bold tracking-wider">
              Record (W-D-L)
            </span>
            <div className="mt-1 font-mono text-xl font-black text-[#246B45]">
              {overview.wins}–{overview.draws}–{overview.losses}
            </div>
          </div>

          <div className="bg-white border border-[#E2EAE3] rounded-2xl p-4 shadow-xs flex flex-col justify-between">
            <span className="text-[10px] text-[#718078] font-mono uppercase font-bold tracking-wider">
              Season Points
            </span>
            <div className="flex items-baseline space-x-1.5 mt-1 font-mono">
              <span className="text-2xl font-black text-[#174B32]">{overview.points}</span>
              <span className="text-xs text-[#718078]">({overview.points_per_match} PPM)</span>
            </div>
          </div>

          <div className="bg-white border border-[#E2EAE3] rounded-2xl p-4 shadow-xs flex flex-col justify-between">
            <span className="text-[10px] text-[#718078] font-mono uppercase font-bold tracking-wider">
              Goals (GF / GA)
            </span>
            <div className="mt-1 font-mono text-xl font-black text-[#26332B]">
              {overview.goals_scored} : {overview.goals_conceded}
              <span className="text-xs text-[#718078] font-normal ml-1.5">({overview.goal_difference > 0 ? `+${overview.goal_difference}` : overview.goal_difference})</span>
            </div>
          </div>

          <div className="bg-white border border-[#E2EAE3] rounded-2xl p-4 shadow-xs flex flex-col justify-between">
            <span className="text-[10px] text-[#718078] font-mono uppercase font-bold tracking-wider">
              Clean Sheets
            </span>
            <div className="mt-1 font-mono text-xl font-black text-[#246B45]">
              {overview.clean_sheets}
            </div>
          </div>

          <div className="bg-white border border-[#E2EAE3] rounded-2xl p-4 shadow-xs flex flex-col justify-between">
            <span className="text-[10px] text-[#718078] font-mono uppercase font-bold tracking-wider">
              Recent Form
            </span>
            <div className="flex items-center space-x-1 mt-1 font-mono">
              {overview.recent_form.map((res, i) => (
                <span
                  key={i}
                  className={`w-6 h-6 rounded flex items-center justify-center font-bold text-xs ${res === "W"
                    ? "bg-[#246B45] text-white"
                    : res === "D"
                      ? "bg-[#D9A441] text-white"
                      : "bg-[#C65B56] text-white"
                    }`}
                >
                  {res}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Action Strip: Match Comparison Workspace */}
      <div className="flex items-center justify-between">
        <div className="text-xs font-mono text-[#718078]">
          Official ISL 2026–27 Matchday Central
        </div>
        <Link
          href="/matches/compare"
          className="px-3.5 py-1.5 rounded-xl bg-[#E6F0E7] hover:bg-[#d8e8da] text-[#174B32] border border-[#C3DEC7] text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-xs font-mono"
        >
          <Scale className="w-3.5 h-3.5 text-[#246B45]" />
          <span>Compare Matches H2H →</span>
        </Link>
      </div>

      {/* Control Bar: Filters & Search */}
      <div className="bg-white border border-[#E2EAE3] p-4 rounded-2xl shadow-xs space-y-3.5">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
          {/* Status Tabs */}
          <div className="flex items-center space-x-1 bg-[#F4F8F4] p-1 rounded-xl border border-[#E2EAE3] text-xs overflow-x-auto">
            {[
              { id: "ALL", label: "All Fixtures (24)" },
              { id: "PLAYED", label: "Played (5)" },
              { id: "UPCOMING", label: "Upcoming (19)" },
              { id: "POSTPONED", label: "Postponed (0)" },
            ].map((s) => (
              <button
                key={s.id}
                onClick={() => setStatusFilter(s.id)}
                className={`px-3 py-1.5 rounded-lg font-semibold tracking-wider text-[11px] whitespace-nowrap transition-all ${statusFilter === s.id
                  ? "bg-[#246B45] text-white shadow-xs"
                  : "text-[#718078] hover:text-[#26332B]"
                  }`}
              >
                {s.label}
              </button>
            ))}
          </div>

          {/* Search Box */}
          <div className="relative flex-1 lg:max-w-xs">
            <Search className="w-4 h-4 text-[#718078] absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search opponent (e.g. East Bengal, Goa)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl pl-9 pr-3 py-1.5 text-xs text-[#26332B] placeholder-[#718078] focus:outline-none focus:border-[#246B45]"
            />
          </div>
        </div>

        {/* Secondary Filters: Home/Away & Matchweek */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#E2EAE3] text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-[#718078] text-[11px] font-mono uppercase font-bold flex items-center space-x-1">
              <Filter className="w-3 h-3 text-[#718078]" />
              <span>Filters:</span>
            </span>

            {/* Home/Away Selector */}
            <div className="flex items-center space-x-1 bg-[#F4F8F4] px-1 py-0.5 rounded-lg border border-[#E2EAE3]">
              {["ALL", "HOME", "AWAY"].map((v) => (
                <button
                  key={v}
                  onClick={() => setVenueFilter(v)}
                  className={`px-2 py-1 rounded text-[11px] font-mono font-semibold transition-all ${venueFilter === v
                    ? "bg-[#E6F0E7] text-[#174B32]"
                    : "text-[#718078] hover:text-[#26332B]"
                    }`}
                >
                  {v === "ALL" ? "All Venues" : v}
                </button>
              ))}
            </div>

            {/* Matchweek Dropdown */}
            <select
              value={matchweekFilter}
              onChange={(e) => setMatchweekFilter(e.target.value)}
              className="bg-[#F4F8F4] border border-[#E2EAE3] text-[#26332B] text-xs rounded-lg px-2.5 py-1 focus:outline-none font-mono"
            >
              <option value="ALL">All Matchweeks (1–24)</option>
              {Array.from({ length: 24 }, (_, i) => i + 1).map((mw) => (
                <option key={mw} value={mw}>
                  Matchweek {mw}
                </option>
              ))}
            </select>

            {(statusFilter !== "ALL" || venueFilter !== "ALL" || matchweekFilter !== "ALL" || searchQuery) && (
              <button
                onClick={resetFilters}
                className="text-[11px] font-mono text-[#718078] hover:text-[#D9A441] flex items-center space-x-1 ml-2 transition-colors"
              >
                <RotateCcw className="w-3 h-3" />
                <span>Reset Filters</span>
              </button>
            )}
          </div>

          <div className="text-xs font-mono text-[#718078]">
            Showing <strong className="text-[#26332B]">{filteredMatches.length}</strong> of {matches.length} fixtures
          </div>
        </div>
      </div>

      {/* Match Cards Listing */}
      <div className="space-y-3.5">
        {loading ? (
          <div className="p-12 text-center text-[#718078] font-mono text-xs">
            Loading verified fixtures from database...
          </div>
        ) : filteredMatches.length > 0 ? (
          filteredMatches.map((match) => {
            const isFinished = match.match_status === "FINISHED";
            const isHome = match.home_team?.slug === "chennaiyin-fc" || match.home_team?.short_name === "CFC";
            const kickoff = match.scheduled_kickoff ? new Date(match.scheduled_kickoff) : null;
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
              : match.kickoff_time_ist || "Kickoff TBC";

            const matchOutcome = isFinished && typeof match.home_score === "number" && typeof match.away_score === "number"
              ? isHome
                ? match.home_score > match.away_score ? "W" : match.home_score === match.away_score ? "D" : "L"
                : match.away_score > match.home_score ? "W" : match.away_score === match.home_score ? "D" : "L"
              : null;

            return (
              <div
                key={match.id}
                className="bg-white hover:bg-[#F4F8F4]/50 border border-[#E2EAE3] hover:border-[#C3DEC7] rounded-2xl p-4 md:p-5 transition-all shadow-xs group relative overflow-hidden"
              >
                {/* Result Indicator Accent */}
                {matchOutcome && (
                  <div
                    className={`absolute left-0 top-0 bottom-0 w-1 ${matchOutcome === "W"
                      ? "bg-[#246B45]"
                      : matchOutcome === "D"
                        ? "bg-[#D9A441]"
                        : "bg-[#C65B56]"
                      }`}
                  />
                )}

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  {/* Meta Header: Matchweek & Kickoff */}
                  <div className="flex flex-wrap items-center space-x-2.5 text-xs text-[#718078] font-mono">
                    <Badge variant={isFinished ? "green" : "blue"}>
                      {isFinished ? "Full Time" : "Scheduled"}
                    </Badge>
                    <span className="text-[#E2EAE3]">•</span>
                    <span>Matchweek {match.matchweek || match.match_number || "—"}</span>
                    <span className="text-[#E2EAE3]">•</span>
                    <span className="text-[#26332B] font-semibold">{dateStr}</span>
                    <span className="text-[#E2EAE3]">•</span>
                    <span className="text-[#718078]">{timeStr}</span>
                  </div>

                  {/* Venue & Location */}
                  <div className="flex items-center space-x-1.5 text-xs text-[#718078] font-medium">
                    <MapPin className="w-3.5 h-3.5 text-[#246B45]" />
                    <span>
                      {match.venue?.name || "Jawaharlal Nehru Stadium"}, {match.venue?.city || "Chennai"}
                    </span>
                    <span className="text-[#E2EAE3]">|</span>
                    <span className={isHome ? "text-[#246B45] font-semibold" : "text-[#D9A441] font-semibold"}>
                      {isHome ? "HOME" : "AWAY"}
                    </span>
                  </div>
                </div>

                {/* Main Matchup Scoreboard */}
                <div className="mt-4 pt-4 border-t border-[#E2EAE3] grid grid-cols-1 md:grid-cols-7 items-center gap-4">
                  {/* Home Team */}
                  <div className="md:col-span-3 flex items-center md:justify-end space-x-3">
                    <div className="text-left md:text-right">
                      <h3 className={`font-bold text-base md:text-lg ${isHome ? "text-[#246B45]" : "text-[#26332B]"}`}>
                        {match.home_team?.name}
                      </h3>
                      <span className="text-[11px] text-[#718078] uppercase font-mono tracking-wider">
                        {isHome ? "Anchor Club" : "Host Club"}
                      </span>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-[#F4F8F4] border border-[#E2EAE3] flex items-center justify-center font-bold font-mono text-sm text-[#26332B]">
                      {match.home_team?.short_name || "H"}
                    </div>
                  </div>

                  {/* Score / VS Center Display */}
                  <div className="md:col-span-1 flex flex-col items-center justify-center py-2 md:py-0">
                    {isFinished ? (
                      <div className="flex items-center space-x-2 bg-[#F4F8F4] px-4 py-1.5 rounded-xl border border-[#E2EAE3] font-mono font-black text-2xl text-[#26332B] shadow-inner">
                        <span className={match.home_score! > match.away_score! ? "text-[#246B45]" : ""}>
                          {match.home_score}
                        </span>
                        <span className="text-[#718078]">:</span>
                        <span className={match.away_score! > match.home_score! ? "text-[#246B45]" : ""}>
                          {match.away_score}
                        </span>
                      </div>
                    ) : (
                      <div className="bg-[#F4F8F4] px-3.5 py-1 rounded-xl border border-[#E2EAE3] font-mono text-xs font-bold text-[#246B45]">
                        VS
                      </div>
                    )}
                  </div>

                  {/* Away Team */}
                  <div className="md:col-span-3 flex items-center justify-between md:justify-start space-x-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 rounded-xl bg-[#F4F8F4] border border-[#E2EAE3] flex items-center justify-center font-bold font-mono text-sm text-[#26332B]">
                        {match.away_team?.short_name || "A"}
                      </div>
                      <div>
                        <h3 className={`font-bold text-base md:text-lg ${!isHome ? "text-[#246B45]" : "text-[#26332B]"}`}>
                          {match.away_team?.name}
                        </h3>
                        <span className="text-[11px] text-[#718078] uppercase font-mono tracking-wider">
                          {!isHome ? "Anchor Club" : "Visiting Club"}
                        </span>
                      </div>
                    </div>

                    {/* Link to Details Button */}
                    <Link
                      href={`/matches/${match.id}`}
                      className="ml-auto px-3.5 py-2 rounded-xl bg-[#E6F0E7] hover:bg-[#d8e8da] text-[#174B32] border border-[#C3DEC7] transition-all flex items-center space-x-1.5 text-xs font-mono font-semibold shadow-xs"
                    >
                      <span>{isFinished ? "Report" : "Preview"}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-[#246B45]" />
                    </Link>
                  </div>
                </div>

                {/* Match Report Footer for Completed Fixtures */}
                {isFinished && (
                  <div className="mt-3 pt-2.5 border-t border-[#E2EAE3] flex flex-wrap items-center justify-between text-[11px] font-mono text-[#718078] gap-2">
                    <div className="flex items-center space-x-3">
                      <span>Ref: <strong className="text-[#26332B]">{match.referee || "Official"}</strong></span>
                      {match.attendance && (
                        <span>Att: <strong className="text-[#26332B]">{match.attendance.toLocaleString()}</strong></span>
                      )}
                    </div>
                    <span className="text-[#246B45] font-semibold">✓ Verified ISL Match Record</span>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="p-12 text-center bg-white border border-[#E2EAE3] rounded-2xl space-y-2 shadow-xs">
            <p className="text-[#26332B] font-bold text-sm">No fixtures found matching your filter criteria.</p>
            <p className="text-[#718078] text-xs">Try selecting a different match status, venue, or clearing the search box.</p>
            <button
              onClick={resetFilters}
              className="mt-3 px-3.5 py-1.5 bg-[#246B45] hover:bg-[#174B32] text-white rounded-lg text-xs font-semibold"
            >
              Reset Filters
            </button>
          </div>
        )}
      </div>
    </Shell>
  );
}
