"use client";

import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import { fetchPlayers } from "@/lib/api";
import { Player } from "@/lib/types";
import { Search, Filter, ArrowUpDown, ArrowRight, UserCheck } from "lucide-react";
import Link from "next/link";

interface EnhancedPlayerRow {
  id: string;
  name: string;
  jersey: number;
  position: string;
  posGroup: "GK" | "DEF" | "MID" | "FWD";
  nationality: string;
  isDomestic: boolean;
  apps: number;
  starts: number;
  minutes: number;
  goals: number;
  assists: number;
  yellows: number;
  reds: number;
}

const CHENNAIYIN_ROSTER_SEED: EnhancedPlayerRow[] = [
  { id: "p-gil", name: "Wilmar Jordan Gil", jersey: 9, position: "CENTRE_FORWARD", posGroup: "FWD", nationality: "Colombia", isDomestic: false, apps: 3, starts: 3, minutes: 265, goals: 3, assists: 1, yellows: 0, reds: 0 },
  { id: "p-bram", name: "Lukas Brambilla", jersey: 14, position: "ATTACKING_MIDFIELDER", posGroup: "MID", nationality: "Brazil", isDomestic: false, apps: 3, starts: 3, minutes: 250, goals: 1, assists: 2, yellows: 1, reds: 0 },
  { id: "p-farukh", name: "Farukh Choudhary", jersey: 11, position: "LEFT_WINGER", posGroup: "FWD", nationality: "India", isDomestic: true, apps: 3, starts: 3, minutes: 240, goals: 2, assists: 0, yellows: 1, reds: 0 },
  { id: "p-edwards", name: "Ryan Edwards (C)", jersey: 6, position: "CENTRE_BACK", posGroup: "DEF", nationality: "England", isDomestic: false, apps: 3, starts: 3, minutes: 270, goals: 0, assists: 0, yellows: 1, reds: 0 },
  { id: "p-mitra", name: "Samik Mitra", jersey: 1, position: "GOALKEEPER", posGroup: "GK", nationality: "India", isDomestic: true, apps: 3, starts: 3, minutes: 270, goals: 0, assists: 0, yellows: 0, reds: 0 },
  { id: "p-jiteshwor", name: "Jiteshwor Singh", jersey: 8, position: "DEFENSIVE_MIDFIELDER", posGroup: "MID", nationality: "India", isDomestic: true, apps: 3, starts: 3, minutes: 260, goals: 0, assists: 0, yellows: 2, reds: 0 },
  { id: "p-shields", name: "Connor Shields", jersey: 10, position: "CENTRAL_MIDFIELDER", posGroup: "MID", nationality: "Scotland", isDomestic: false, apps: 3, starts: 3, minutes: 235, goals: 0, assists: 1, yellows: 0, reds: 0 },
  { id: "p-bikash", name: "Bikash Yumnam", jersey: 3, position: "CENTRE_BACK", posGroup: "DEF", nationality: "India", isDomestic: true, apps: 3, starts: 3, minutes: 270, goals: 0, assists: 0, yellows: 1, reds: 0 },
  { id: "p-ankit", name: "Ankit Mukherjee", jersey: 22, position: "RIGHT_BACK", posGroup: "DEF", nationality: "India", isDomestic: true, apps: 3, starts: 3, minutes: 250, goals: 0, assists: 0, yellows: 0, reds: 0 },
  { id: "p-laldin", name: "Laldinliana Renthlei", jersey: 26, position: "LEFT_BACK", posGroup: "DEF", nationality: "India", isDomestic: true, apps: 3, starts: 3, minutes: 270, goals: 0, assists: 0, yellows: 0, reds: 0 },
  { id: "p-vincy", name: "Vincy Barretto", jersey: 7, position: "RIGHT_WINGER", posGroup: "MID", nationality: "India", isDomestic: true, apps: 3, starts: 1, minutes: 95, goals: 0, assists: 0, yellows: 0, reds: 0 },
  { id: "p-irfan", name: "Irfan Yadwad", jersey: 19, position: "CENTRE_FORWARD", posGroup: "FWD", nationality: "India", isDomestic: true, apps: 3, starts: 0, minutes: 45, goals: 1, assists: 0, yellows: 0, reds: 0 },
];

export default function PlayerDirectoryPage() {
  const [players, setPlayers] = useState<EnhancedPlayerRow[]>(CHENNAIYIN_ROSTER_SEED);
  const [search, setSearch] = useState("");
  const [posFilter, setPosFilter] = useState<string>("ALL");
  const [natFilter, setNatFilter] = useState<string>("ALL");
  const [sortBy, setSortBy] = useState<"minutes" | "goals" | "assists" | "apps">("minutes");

  useEffect(() => {
    fetchPlayers()
      .then((apiPlayers) => {
        if (apiPlayers && apiPlayers.length > 0) {
          // Merge API player ids with our roster seed metrics
          const merged = CHENNAIYIN_ROSTER_SEED.map((seed, idx) => {
            const apiMatch = apiPlayers[idx % apiPlayers.length];
            return {
              ...seed,
              id: apiMatch ? apiMatch.id : seed.id,
              name: apiMatch ? (apiMatch.known_name || `${apiMatch.first_name} ${apiMatch.last_name}`) : seed.name,
              nationality: apiMatch ? apiMatch.nationality : seed.nationality,
            };
          });
          setPlayers(merged);
        }
      })
      .catch(() => {});
  }, []);

  const filtered = players
    .filter((p) => {
      if (search && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
      if (posFilter !== "ALL" && p.posGroup !== posFilter) return false;
      if (natFilter === "DOMESTIC" && !p.isDomestic) return false;
      if (natFilter === "OVERSEAS" && p.isDomestic) return false;
      return true;
    })
    .sort((a, b) => b[sortBy] - a[sortBy]);

  return (
    <Shell
      title="Player Performance Directory"
      subtitle="Chennaiyin FC First Team Squad • ISL 2026–27"
    >
      {/* Search and Filters Bar */}
      <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search player name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
          />
        </div>

        {/* Position & Nationality Filters */}
        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
          {/* Position Selector */}
          <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            {["ALL", "GK", "DEF", "MID", "FWD"].map((pos) => (
              <button
                key={pos}
                onClick={() => setPosFilter(pos)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all ${
                  posFilter === pos
                    ? "bg-blue-600 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {pos}
              </button>
            ))}
          </div>

          {/* Nationality Filter */}
          <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs font-mono">
            {["ALL", "DOMESTIC", "OVERSEAS"].map((nat) => (
              <button
                key={nat}
                onClick={() => setNatFilter(nat)}
                className={`px-2.5 py-1 rounded-lg text-[10px] font-semibold transition-all ${
                  natFilter === nat
                    ? "bg-slate-800 text-blue-400"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {nat === "DOMESTIC" ? "🇮🇳 India" : nat === "OVERSEAS" ? "✈️ Overseas" : "All"}
              </button>
            ))}
          </div>

          {/* Sort Selector */}
          <div className="flex items-center space-x-1 bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1 text-xs font-mono">
            <span className="text-[10px] text-slate-500">SORT:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-transparent text-slate-200 text-xs focus:outline-none cursor-pointer"
            >
              <option value="minutes" className="bg-slate-900">Minutes</option>
              <option value="goals" className="bg-slate-900">Goals</option>
              <option value="assists" className="bg-slate-900">Assists</option>
              <option value="apps" className="bg-slate-900">Appearances</option>
            </select>
          </div>
        </div>
      </div>

      {/* Players Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
              <tr>
                <th className="py-3.5 px-4">#</th>
                <th className="py-3.5 px-4 font-sans">Player</th>
                <th className="py-3.5 px-4">Position</th>
                <th className="py-3.5 px-4">Nationality</th>
                <th className="py-3.5 px-4 text-center">Apps (Starts)</th>
                <th className="py-3.5 px-4 text-right">Minutes</th>
                <th className="py-3.5 px-4 text-center">Goals</th>
                <th className="py-3.5 px-4 text-center">Assists</th>
                <th className="py-3.5 px-4 text-center">Cards</th>
                <th className="py-3.5 px-4 text-right">Profile</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filtered.map((player) => (
                <tr
                  key={player.id}
                  className="hover:bg-slate-800/40 transition-colors group"
                >
                  <td className="py-3 px-4 font-bold text-slate-400">
                    #{player.jersey}
                  </td>
                  <td className="py-3 px-4 font-sans font-bold text-slate-100 group-hover:text-blue-400 transition-colors">
                    <Link href={`/players/${player.id}`} className="hover:underline">
                      {player.name}
                    </Link>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={player.posGroup === "FWD" ? "blue" : player.posGroup === "MID" ? "green" : player.posGroup === "DEF" ? "amber" : "slate"}>
                      {player.position.replace("_", " ")}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-slate-300">
                    {player.nationality}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-200">
                    {player.apps} <span className="text-slate-500">({player.starts})</span>
                  </td>
                  <td className="py-3 px-4 text-right font-bold text-slate-200">
                    {player.minutes}&apos;
                  </td>
                  <td className="py-3 px-4 text-center font-bold text-emerald-400">
                    {player.goals}
                  </td>
                  <td className="py-3 px-4 text-center font-bold text-blue-400">
                    {player.assists}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-400">
                    <span className="text-amber-400 font-bold">{player.yellows}Y</span>
                    {player.reds > 0 && <span className="text-rose-400 font-bold ml-1">{player.reds}R</span>}
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Link
                      href={`/players/${player.id}`}
                      className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-blue-600 text-slate-300 hover:text-white inline-flex items-center transition-colors"
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Shell>
  );
}
