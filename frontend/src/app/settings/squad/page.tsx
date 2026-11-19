"use client";

import React, { useEffect, useState, useTransition } from "react";
import Link from "next/link";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import {
  fetchActiveSquad,
  fetchSquadImportHistory,
  previewSquadImportFile,
  previewSquadImportJson,
  syncSquad,
  updatePlayer,
} from "@/lib/api";
import {
  PlayerUpdatePayload,
  SquadImportHistoryItem,
  SquadImportPreview,
  SquadMember,
  SquadSyncResponse,
} from "@/lib/types";
import {
  Users,
  Upload,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  FileText,
  Search,
  Filter,
  ArrowRight,
  ShieldAlert,
  Calendar,
  DollarSign,
  UserCheck,
  UserX,
  History,
  FileCheck,
  Edit2,
  X,
  Clock,
  Sparkles,
} from "lucide-react";
import { clsx } from "clsx";

export default function SquadManagementPage() {
  const [activeTab, setActiveTab] = useState<"roster" | "sync" | "history">("roster");

  // Roster Tab States
  const [squad, setSquad] = useState<SquadMember[]>([]);
  const [loadingRoster, setLoadingRoster] = useState(true);
  const [search, setSearch] = useState("");
  const [posFilter, setPosFilter] = useState<string>("ALL");
  const [natFilter, setNatFilter] = useState<string>("ALL");
  const [includeInactive, setIncludeInactive] = useState(false);
  const [selectedPlayerForEdit, setSelectedPlayerForEdit] = useState<SquadMember | null>(null);
  const [editForm, setEditForm] = useState<PlayerUpdatePayload>({});
  const [savingEdit, setSavingEdit] = useState(false);

  // Sync Tab States
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<SquadImportPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [syncConfirmed, setSyncConfirmed] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SquadSyncResponse | null>(null);
  const [syncError, setSyncError] = useState<string | null>(null);

  // History Tab States
  const [historyLogs, setHistoryLogs] = useState<SquadImportHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Load active squad
  const loadSquad = async () => {
    setLoadingRoster(true);
    try {
      const data = await fetchActiveSquad({
        include_inactive: includeInactive,
        position: posFilter,
        nationality: natFilter,
      });
      setSquad(data);
    } catch (err) {
      console.error("Failed to load active squad:", err);
    } finally {
      setLoadingRoster(false);
    }
  };

  useEffect(() => {
    loadSquad();
  }, [includeInactive, posFilter, natFilter]);

  // Load history logs
  const loadHistory = async () => {
    setLoadingHistory(true);
    try {
      const logs = await fetchSquadImportHistory();
      setHistoryLogs(logs);
    } catch (err) {
      console.error("Failed to load history logs:", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (activeTab === "history") {
      loadHistory();
    }
  }, [activeTab]);

  // Handle File Upload & Preview
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setPreviewLoading(true);
    setSyncError(null);
    setSyncResult(null);

    try {
      const preview = await previewSquadImportFile(file);
      setPreviewData(preview);
    } catch (err: any) {
      setSyncError(err.message || "Failed to parse uploaded roster file.");
      setPreviewData(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  // 1-Click Load Bundled Official 2026-27 Roster Preview
  const handleLoadOfficialRoster = async () => {
    setPreviewLoading(true);
    setSelectedFile(null);
    setSyncError(null);
    setSyncResult(null);

    try {
      const preview = await previewSquadImportJson([]);
      setPreviewData(preview);
    } catch (err: any) {
      setSyncError(err.message || "Failed to load bundled official squad dataset.");
      setPreviewData(null);
    } finally {
      setPreviewLoading(false);
    }
  };

  // Commit Synchronization
  const handleCommitSync = async () => {
    if (!syncConfirmed) return;
    setSyncing(true);
    setSyncError(null);

    try {
      const result = await syncSquad({
        batch_id: previewData?.batch_id,
        confirmed: true,
        deactivate_absent: true,
      });
      setSyncResult(result);
      setPreviewData(null);
      setSyncConfirmed(false);
      loadSquad();
      if (activeTab === "history") loadHistory();
    } catch (err: any) {
      setSyncError(err.message || "Squad synchronization failed.");
    } finally {
      setSyncing(false);
    }
  };

  // Player Profile Edit Save
  const handleSavePlayerEdit = async () => {
    if (!selectedPlayerForEdit) return;
    setSavingEdit(true);
    try {
      await updatePlayer(selectedPlayerForEdit.player_id, editForm);
      setSelectedPlayerForEdit(null);
      loadSquad();
    } catch (err) {
      alert("Failed to update player details. Check network or console.");
    } finally {
      setSavingEdit(false);
    }
  };

  // Squad KPIs
  const activeMembers = squad.filter((m) => m.is_active);
  const totalCount = activeMembers.length;
  const domesticCount = activeMembers.filter((m) => m.is_domestic).length;
  const overseasCount = totalCount - domesticCount;

  const totalMarketValueInr = activeMembers.reduce(
    (acc, m) => acc + (m.market_value_inr || 0),
    0
  );
  const formattedSquadValue =
    totalMarketValueInr > 10000000
      ? `₹${(totalMarketValueInr / 10000000).toFixed(2)} Cr`
      : totalMarketValueInr > 100000
      ? `₹${(totalMarketValueInr / 100000).toFixed(2)} L`
      : "—";

  const validAges = activeMembers.map((m) => m.age).filter((a): a is number => a !== null && a !== undefined && a > 0);
  const avgAge = validAges.length > 0 ? (validAges.reduce((a, b) => a + b, 0) / validAges.length).toFixed(1) : "—";

  // Filtered Roster
  const filteredSquad = squad.filter((p) => {
    if (search) {
      const q = search.toLowerCase();
      const nameMatch = p.name.toLowerCase().includes(q) || (p.known_name && p.known_name.toLowerCase().includes(q));
      const numMatch = p.squad_number ? p.squad_number.toString() === q : false;
      if (!nameMatch && !numMatch) return false;
    }
    return true;
  });

  return (
    <Shell
      title="Squad Management & Synchronization"
      subtitle="Chennaiyin FC • ISL 2026–27 Roster Synchronization Engine"
    >
      <div className="space-y-6">
        {/* Navigation Tabs */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab("roster")}
              className={clsx(
                "px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2",
                activeTab === "roster"
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-900/40"
                  : "bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              )}
            >
              <Users className="w-4 h-4" />
              <span>Active Squad ({totalCount})</span>
            </button>

            <button
              onClick={() => setActiveTab("sync")}
              className={clsx(
                "px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2",
                activeTab === "sync"
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-900/40"
                  : "bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              )}
            >
              <RefreshCw className="w-4 h-4" />
              <span>Roster Import & Sync</span>
            </button>

            <button
              onClick={() => setActiveTab("history")}
              className={clsx(
                "px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-2",
                activeTab === "history"
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-900/40"
                  : "bg-slate-900 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
              )}
            >
              <History className="w-4 h-4" />
              <span>Audit History</span>
            </button>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <span className="text-slate-400">Anchor Club:</span>
            <Badge variant="blue" size="sm">Chennaiyin FC</Badge>
            <span className="text-slate-400">Season:</span>
            <span className="font-mono font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded text-[11px]">
              2026–27
            </span>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* TAB 1: ACTIVE SQUAD VIEW */}
        {/* ========================================================================= */}
        {activeTab === "roster" && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Total Active Squad</span>
                  <Users className="w-4 h-4 text-blue-400" />
                </div>
                <div className="text-2xl font-black text-white">{totalCount}</div>
                <div className="text-[10px] text-slate-500 mt-1">2026–27 Roster Registrations</div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Domestic Players</span>
                  <UserCheck className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-2xl font-black text-emerald-400">{domesticCount}</div>
                <div className="text-[10px] text-slate-500 mt-1">Eligible for Indian Quota</div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Overseas Signings</span>
                  <Sparkles className="w-4 h-4 text-purple-400" />
                </div>
                <div className="text-2xl font-black text-purple-400">{overseasCount}</div>
                <div className="text-[10px] text-slate-500 mt-1">International Players</div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Total Market Value</span>
                  <DollarSign className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-2xl font-black text-amber-400 font-mono">{formattedSquadValue}</div>
                <div className="text-[10px] text-slate-500 mt-1">Combined Squad Valuation</div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Average Squad Age</span>
                  <Calendar className="w-4 h-4 text-sky-400" />
                </div>
                <div className="text-2xl font-black text-sky-400">{avgAge} <span className="text-xs text-slate-400">yrs</span></div>
                <div className="text-[10px] text-slate-500 mt-1">Mean Age Across Roster</div>
              </div>
            </div>

            {/* Filter and Search Bar */}
            <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-lg flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="relative w-full md:w-80">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search by player name or squad #..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
                />
              </div>

              <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto">
                {/* Position Group Filter */}
                <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px] font-semibold">
                  {["ALL", "GK", "DEF", "MID", "FWD"].map((pos) => (
                    <button
                      key={pos}
                      onClick={() => setPosFilter(pos)}
                      className={clsx(
                        "px-2.5 py-1 rounded-lg transition-colors",
                        posFilter === pos ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
                      )}
                    >
                      {pos}
                    </button>
                  ))}
                </div>

                {/* Nationality Filter */}
                <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px] font-semibold">
                  {["ALL", "DOMESTIC", "OVERSEAS"].map((nat) => (
                    <button
                      key={nat}
                      onClick={() => setNatFilter(nat)}
                      className={clsx(
                        "px-2.5 py-1 rounded-lg transition-colors",
                        natFilter === nat ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
                      )}
                    >
                      {nat === "DOMESTIC" ? "Domestic" : nat === "OVERSEAS" ? "Overseas" : "All"}
                    </button>
                  ))}
                </div>

                {/* Inactive Toggle */}
                <label className="flex items-center space-x-2 text-xs text-slate-400 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 cursor-pointer hover:border-slate-700">
                  <input
                    type="checkbox"
                    checked={includeInactive}
                    onChange={(e) => setIncludeInactive(e.target.checked)}
                    className="rounded border-slate-800 text-blue-600 focus:ring-0"
                  />
                  <span>Show Departed / Inactive</span>
                </label>

                <button
                  onClick={loadSquad}
                  className="p-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700 transition-colors"
                  title="Refresh Roster"
                >
                  <RefreshCw className={clsx("w-4 h-4", loadingRoster && "animate-spin text-blue-400")} />
                </button>
              </div>
            </div>

            {/* Squad Table */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/70 border-b border-slate-800 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
                    <tr>
                      <th className="py-3 px-4 w-12 text-center">#</th>
                      <th className="py-3 px-4">Player</th>
                      <th className="py-3 px-3">Position</th>
                      <th className="py-3 px-3">Age / DOB</th>
                      <th className="py-3 px-3">Nationality</th>
                      <th className="py-3 px-3">Height / Foot</th>
                      <th className="py-3 px-3">Joined / Previous Club</th>
                      <th className="py-3 px-3">Contract Expiry</th>
                      <th className="py-3 px-3 text-right">Market Value</th>
                      <th className="py-3 px-3 text-center">Status</th>
                      <th className="py-3 px-3 text-center w-16">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-medium">
                    {loadingRoster ? (
                      <tr>
                        <td colSpan={11} className="py-12 text-center text-slate-500">
                          <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-400" />
                          <span>Loading active Chennaiyin FC squad...</span>
                        </td>
                      </tr>
                    ) : filteredSquad.length === 0 ? (
                      <tr>
                        <td colSpan={11} className="py-12 text-center text-slate-500">
                          No players found matching current filters.
                        </td>
                      </tr>
                    ) : (
                      filteredSquad.map((player) => {
                        const posBadgeVariant: "amber" | "green" | "blue" | "rose" =
                          player.pos_group === "GK"
                            ? "amber"
                            : player.pos_group === "DEF"
                            ? "green"
                            : player.pos_group === "MID"
                            ? "blue"
                            : "rose";

                        return (
                          <tr
                            key={player.id}
                            className={clsx(
                              "hover:bg-slate-800/40 transition-colors",
                              !player.is_active && "opacity-60 bg-red-950/10"
                            )}
                          >
                            <td className="py-3 px-4 text-center">
                              <span className="font-mono font-bold text-slate-300 bg-slate-950 px-2 py-0.5 rounded border border-slate-800 text-[11px]">
                                {player.squad_number !== null ? player.squad_number : "—"}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex flex-col">
                                <span className="font-bold text-slate-100 flex items-center space-x-1.5">
                                  <span>{player.name}</span>
                                  {!player.is_domestic && (
                                    <span className="text-[9px] font-bold px-1 rounded bg-purple-900/60 text-purple-300 border border-purple-700/50">
                                      INT
                                    </span>
                                  )}
                                </span>
                                {player.known_name && player.known_name !== player.name && (
                                  <span className="text-[11px] text-slate-400 font-normal">
                                    {player.known_name}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-3">
                              <Badge variant={posBadgeVariant} size="sm">
                                {player.position}
                              </Badge>
                            </td>
                            <td className="py-3 px-3 font-mono text-slate-300">
                              <div>{player.age ? `${player.age} yrs` : "—"}</div>
                              <div className="text-[10px] text-slate-500">
                                {player.date_of_birth || "—"}
                              </div>
                            </td>
                            <td className="py-3 px-3">
                              <div className="flex flex-col">
                                <span className="text-slate-200">{player.nationality}</span>
                                {player.secondary_nationality && (
                                  <span className="text-[10px] text-slate-400">
                                    / {player.secondary_nationality}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="py-3 px-3 font-mono text-slate-300">
                              <div>{player.height_m ? `${player.height_m.toFixed(2)}m` : "—"}</div>
                              <div className="text-[10px] text-slate-500">
                                {player.preferred_foot ? `${player.preferred_foot} foot` : "—"}
                              </div>
                            </td>
                            <td className="py-3 px-3">
                              <div className="text-slate-300">{player.previous_club || "—"}</div>
                              <div className="text-[10px] text-slate-500 font-mono">
                                {player.joined_date ? `Joined: ${player.joined_date}` : "—"}
                              </div>
                            </td>
                            <td className="py-3 px-3 font-mono text-slate-300">
                              {player.contract_expiry || "—"}
                            </td>
                            <td className="py-3 px-3 text-right font-mono font-bold text-amber-400">
                              <div>
                                {player.market_value_inr
                                  ? player.market_value_inr >= 10000000
                                    ? `₹${(player.market_value_inr / 10000000).toFixed(2)} Cr`
                                    : `₹${(player.market_value_inr / 100000).toFixed(2)} L`
                                  : player.market_value_original || "—"}
                              </div>
                              {player.market_value_original && (
                                <div className="text-[10px] text-slate-500 font-normal">
                                  {player.market_value_original}
                                </div>
                              )}
                            </td>
                            <td className="py-3 px-3 text-center">
                              {player.is_active ? (
                                <Badge variant="green" size="sm">Active</Badge>
                              ) : (
                                <Badge variant="rose" size="sm">Inactive</Badge>
                              )}
                            </td>
                            <td className="py-3 px-3 text-center">
                              <button
                                onClick={() => {
                                  setSelectedPlayerForEdit(player);
                                  setEditForm({
                                    squad_number: player.squad_number ?? undefined,
                                    primary_position: player.position,
                                    contract_expiry: player.contract_expiry ?? undefined,
                                    market_value_original: player.market_value_original ?? undefined,
                                    market_value_inr: player.market_value_inr ?? undefined,
                                    previous_club: player.previous_club ?? undefined,
                                    preferred_foot: player.preferred_foot ?? undefined,
                                    is_active: player.is_active,
                                  });
                                }}
                                className="p-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                                title="Edit Player Profile"
                              >
                                <Edit2 className="w-3.5 h-3.5" />
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 2: ROSTER IMPORT & SYNC CONSOLE */}
        {/* ========================================================================= */}
        {activeTab === "sync" && (
          <div className="space-y-6 max-w-4xl mx-auto">
            {/* Top Info Banner */}
            <div className="p-4 rounded-2xl bg-blue-950/30 border border-blue-800/50 flex items-start space-x-3.5">
              <ShieldAlert className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
              <div className="text-xs space-y-1">
                <span className="font-bold text-blue-300 block">
                  Strict Historical Data Preservation Guarantee
                </span>
                <p className="text-slate-300 leading-relaxed">
                  Synchronizing replacing the active squad roster will <strong>never delete</strong> departed players, past lineups, match minutes, goals, assists, or events. Departed squad members are safely deactivated for the 2026–27 season (`is_active = False`) while preserving all historical integrity. Missing fields like height or foot are safely retained as NULL and never coerced to zero.
                </p>
              </div>
            </div>

            {/* Sync Error Banner */}
            {syncError && (
              <div className="p-4 rounded-2xl bg-red-950/40 border border-red-800/60 flex items-start space-x-3 text-xs text-red-300">
                <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold block">Synchronization Error</span>
                  <p>{syncError}</p>
                </div>
              </div>
            )}

            {/* Sync Success Banner */}
            {syncResult && (
              <div className="p-5 rounded-2xl bg-emerald-950/40 border border-emerald-800/60 space-y-3">
                <div className="flex items-center space-x-3 text-emerald-300">
                  <CheckCircle className="w-5 h-5 text-emerald-400" />
                  <span className="font-bold text-sm">Squad Synchronization Successful!</span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="p-2.5 rounded-xl bg-slate-950/60 border border-emerald-900/40">
                    <span className="text-slate-400 block text-[10px]">Batch ID</span>
                    <span className="text-slate-200 font-bold">{syncResult.batch_id}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950/60 border border-emerald-900/40">
                    <span className="text-slate-400 block text-[10px]">New Signings</span>
                    <span className="text-emerald-400 font-bold">+{syncResult.new_created}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950/60 border border-emerald-900/40">
                    <span className="text-slate-400 block text-[10px]">Profiles Updated</span>
                    <span className="text-blue-400 font-bold">{syncResult.updated}</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-slate-950/60 border border-emerald-900/40">
                    <span className="text-slate-400 block text-[10px]">Active 2026–27 Squad</span>
                    <span className="text-white font-bold">{syncResult.active_squad_count} Players</span>
                  </div>
                </div>
                <div className="text-[11px] text-slate-400 pt-1">
                  {syncResult.message}
                </div>
              </div>
            )}

            {/* Import Methods */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Option 1: Load Official Supplied Roster */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-slate-100 font-bold text-sm">
                    <FileCheck className="w-4 h-4 text-blue-400" />
                    <span>Official 2026–27 Roster Dataset</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Instantly load and audit the official verified Chennaiyin FC 2026–27 dataset (27 players from Mohammad Nawaz to Vivek S) bundled in the repository.
                  </p>
                </div>

                <button
                  onClick={handleLoadOfficialRoster}
                  disabled={previewLoading || syncing}
                  className="w-full py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold text-xs flex items-center justify-center space-x-2 transition-all shadow-lg shadow-blue-900/40"
                >
                  <RefreshCw className={clsx("w-4 h-4", previewLoading && "animate-spin")} />
                  <span>Load Official 2026–27 Dataset</span>
                </button>
              </div>

              {/* Option 2: Drag & Drop CSV / JSON File */}
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-slate-100 font-bold text-sm">
                    <Upload className="w-4 h-4 text-emerald-400" />
                    <span>Upload Custom CSV / JSON</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Upload an updated roster file. Supports standard transfer market columns: Player, Position, Foot, Height, Market Value, Signed from, Contract until.
                  </p>
                </div>

                <label className="w-full py-2.5 px-4 rounded-xl border border-dashed border-slate-700 hover:border-blue-500 bg-slate-950/60 hover:bg-slate-950 text-slate-300 font-semibold text-xs flex items-center justify-center space-x-2 transition-all cursor-pointer">
                  <Upload className="w-4 h-4 text-slate-400" />
                  <span>{selectedFile ? selectedFile.name : "Choose CSV / JSON File"}</span>
                  <input
                    type="file"
                    accept=".csv, .json, text/csv, application/json"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Preview Section */}
            {previewData && (
              <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div>
                    <h3 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
                      <span>Import Audit & Discrepancy Preview</span>
                      <Badge variant="blue" size="sm">{previewData.total_incoming} Incoming</Badge>
                    </h3>
                    <p className="text-xs text-slate-400 font-mono mt-0.5">
                      Batch ID: {previewData.batch_id}
                    </p>
                  </div>

                  <div className="flex items-center space-x-2 text-xs">
                    <span className="text-emerald-400 font-bold">+{previewData.new_players.length} New</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-blue-400 font-bold">{previewData.updated_players.length} Updated</span>
                    <span className="text-slate-600">•</span>
                    <span className="text-amber-400 font-bold">{previewData.leaving_players.length} Departures</span>
                  </div>
                </div>

                {/* KPI Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Total Incoming</span>
                    <span className="text-lg font-bold text-white">{previewData.total_incoming}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">New Signings</span>
                    <span className="text-lg font-bold text-emerald-400">+{previewData.new_players.length}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Retained / Updated</span>
                    <span className="text-lg font-bold text-blue-400">{previewData.updated_players.length}</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">Departed (Deactivated)</span>
                    <span className="text-lg font-bold text-amber-400">{previewData.leaving_players.length}</span>
                  </div>
                </div>

                {/* Missing Fields Breakdown */}
                {Object.keys(previewData.missing_fields_summary).length > 0 && (
                  <div className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5">
                    <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                      <span>Missing Fields Summary (Safely Preserved as NULL, Not Zero):</span>
                    </div>
                    <div className="flex flex-wrap gap-2 text-[11px] font-mono">
                      {Object.entries(previewData.missing_fields_summary).map(([field, count]) => (
                        <span key={field} className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400">
                          {field}: <strong className="text-amber-400">{count}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Departures Warning List */}
                {previewData.leaving_players.length > 0 && (
                  <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-800/40 space-y-2">
                    <div className="flex items-center space-x-2 text-xs font-bold text-amber-300">
                      <UserX className="w-4 h-4 text-amber-400" />
                      <span>Departed Players (Deactivating active 2026–27 membership only):</span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {previewData.leaving_players.map((p) => (
                        <span
                          key={p.player_id}
                          className="px-2 py-1 rounded-lg bg-amber-950/60 border border-amber-700/50 text-[11px] text-amber-200"
                        >
                          #{p.squad_number || "—"} {p.name} ({p.position})
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Confirmation Checkbox & Submit */}
                <div className="pt-4 border-t border-slate-800 space-y-4">
                  <label className="flex items-start space-x-3 text-xs text-slate-300 cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={syncConfirmed}
                      onChange={(e) => setSyncConfirmed(e.target.checked)}
                      className="mt-0.5 rounded border-slate-700 text-blue-600 focus:ring-0"
                    />
                    <span>
                      I confirm and authorize synchronizing the Chennaiyin FC 2026–27 squad roster. I understand that departed players will have their active 2026–27 membership deactivated, while <strong>all historical match records, lineups, goals, and statistics will remain completely intact</strong>.
                    </span>
                  </label>

                  <div className="flex items-center justify-end space-x-3">
                    <button
                      onClick={() => setPreviewData(null)}
                      className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCommitSync}
                      disabled={!syncConfirmed || syncing}
                      className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-xs font-bold flex items-center space-x-2 transition-all shadow-lg shadow-emerald-950/50"
                    >
                      <CheckCircle className={clsx("w-4 h-4", syncing && "animate-spin")} />
                      <span>{syncing ? "Committing Synchronization..." : "Commit Squad Synchronization"}</span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================================= */}
        {/* TAB 3: AUDIT HISTORY LOGS */}
        {/* ========================================================================= */}
        {activeTab === "history" && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-200">
                Squad Synchronization Audit Trail
              </h3>
              <button
                onClick={loadHistory}
                className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-300 hover:text-white flex items-center space-x-1.5"
              >
                <RefreshCw className={clsx("w-3.5 h-3.5", loadingHistory && "animate-spin")} />
                <span>Refresh Logs</span>
              </button>
            </div>

            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/70 border-b border-slate-800 text-slate-400 font-semibold tracking-wider uppercase text-[10px]">
                    <tr>
                      <th className="py-3 px-4">Batch ID</th>
                      <th className="py-3 px-4">Timestamp</th>
                      <th className="py-3 px-4">Source Dataset</th>
                      <th className="py-3 px-3 text-center">Incoming</th>
                      <th className="py-3 px-3 text-center">New</th>
                      <th className="py-3 px-3 text-center">Updated</th>
                      <th className="py-3 px-3 text-center">Deactivated</th>
                      <th className="py-3 px-3 text-center">Status</th>
                      <th className="py-3 px-4">Operator</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-medium">
                    {loadingHistory ? (
                      <tr>
                        <td colSpan={9} className="py-8 text-center text-slate-500">
                          <RefreshCw className="w-4 h-4 animate-spin mx-auto mb-1 text-blue-400" />
                          <span>Loading audit logs...</span>
                        </td>
                      </tr>
                    ) : historyLogs.length === 0 ? (
                      <tr>
                        <td colSpan={9} className="py-8 text-center text-slate-500">
                          No squad synchronization logs recorded yet.
                        </td>
                      </tr>
                    ) : (
                      historyLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-800/40">
                          <td className="py-3 px-4 font-mono font-bold text-blue-400">
                            {log.batch_id}
                          </td>
                          <td className="py-3 px-4 font-mono text-slate-400">
                            {new Date(log.created_at).toLocaleString()}
                          </td>
                          <td className="py-3 px-4 text-slate-200">
                            {log.source_name}
                          </td>
                          <td className="py-3 px-3 text-center font-mono font-bold text-white">
                            {log.total_incoming}
                          </td>
                          <td className="py-3 px-3 text-center font-mono text-emerald-400 font-bold">
                            +{log.new_players}
                          </td>
                          <td className="py-3 px-3 text-center font-mono text-blue-400">
                            {log.updated_players}
                          </td>
                          <td className="py-3 px-3 text-center font-mono text-amber-400">
                            {log.deactivated_players}
                          </td>
                          <td className="py-3 px-3 text-center">
                            <Badge variant={log.status === "COMPLETED" ? "green" : "rose"} size="sm">
                              {log.status}
                            </Badge>
                          </td>
                          <td className="py-3 px-4 font-mono text-slate-400">
                            {log.imported_by || "system"}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* EDIT PLAYER PROFILE MODAL */}
        {/* ========================================================================= */}
        {selectedPlayerForEdit && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <Edit2 className="w-4 h-4 text-blue-400" />
                  <h3 className="font-bold text-sm text-slate-100">
                    Edit Player Profile: {selectedPlayerForEdit.name}
                  </h3>
                </div>
                <button
                  onClick={() => setSelectedPlayerForEdit(null)}
                  className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Squad Number</label>
                  <input
                    type="number"
                    value={editForm.squad_number ?? ""}
                    onChange={(e) =>
                      setEditForm({
                        ...editForm,
                        squad_number: e.target.value ? parseInt(e.target.value) : undefined,
                      })
                    }
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-slate-200"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Position</label>
                  <input
                    type="text"
                    value={editForm.primary_position ?? ""}
                    onChange={(e) =>
                      setEditForm({ ...editForm, primary_position: e.target.value })
                    }
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-slate-200"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Contract Expiry</label>
                  <input
                    type="text"
                    placeholder="YYYY-MM-DD"
                    value={editForm.contract_expiry ?? ""}
                    onChange={(e) =>
                      setEditForm({ ...editForm, contract_expiry: e.target.value })
                    }
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-slate-200"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Previous Club</label>
                  <input
                    type="text"
                    value={editForm.previous_club ?? ""}
                    onChange={(e) =>
                      setEditForm({ ...editForm, previous_club: e.target.value })
                    }
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-slate-200"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Preferred Foot</label>
                  <select
                    value={editForm.preferred_foot ?? ""}
                    onChange={(e) =>
                      setEditForm({ ...editForm, preferred_foot: e.target.value || undefined })
                    }
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-slate-200"
                  >
                    <option value="">Unspecified (—)</option>
                    <option value="Right">Right</option>
                    <option value="Left">Left</option>
                    <option value="Both">Both</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 mb-1">Original Market Value</label>
                  <input
                    type="text"
                    placeholder="e.g. ₹1.10 Cr or ₹55 L"
                    value={editForm.market_value_original ?? ""}
                    onChange={(e) =>
                      setEditForm({ ...editForm, market_value_original: e.target.value })
                    }
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-slate-200"
                  />
                </div>
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  onClick={() => setSelectedPlayerForEdit(null)}
                  className="px-3 py-1.5 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSavePlayerEdit}
                  disabled={savingEdit}
                  className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold flex items-center space-x-1.5"
                >
                  <CheckCircle className={clsx("w-3.5 h-3.5", savingEdit && "animate-spin")} />
                  <span>{savingEdit ? "Saving..." : "Save Changes"}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Shell>
  );
}
