"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import { fetchFixtures, importFixtures } from "@/lib/api";
import { FixtureImportResponse, Match } from "@/lib/types";
import {
  Calendar,
  MapPin,
  Clock,
  ArrowRight,
  Search,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  ShieldCheck,
  Upload,
  CalendarDays,
  ExternalLink,
} from "lucide-react";
import { clsx } from "clsx";

export default function FixtureManagementPage() {
  const [fixtures, setFixtures] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [opponentFilter, setOpponentFilter] = useState("ALL");
  const [homeAwayFilter, setHomeAwayFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [legFilter, setLegFilter] = useState("ALL");
  const [search, setSearch] = useState("");
  const [importing, setImporting] = useState(false);
  const [importResult, setImportResult] = useState<FixtureImportResponse | null>(null);
  const [showImportModal, setShowImportModal] = useState(false);

  // Load fixtures
  const loadFixtures = async () => {
    setLoading(true);
    try {
      const data = await fetchFixtures({
        opponent: opponentFilter !== "ALL" ? opponentFilter : undefined,
        home_away: homeAwayFilter !== "ALL" ? homeAwayFilter : undefined,
        verification_status: statusFilter !== "ALL" ? statusFilter : undefined,
      });
      setFixtures(data);
    } catch (err) {
      console.error("Failed to load fixtures:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFixtures();
  }, [opponentFilter, homeAwayFilter, statusFilter]);

  // Handle 1-Click Import
  const handleImport = async (file?: File) => {
    setImporting(true);
    try {
      const res = await importFixtures(file);
      setImportResult(res);
      await loadFixtures();
    } catch (err: any) {
      alert("Failed to import fixtures: " + (err.message || err));
    } finally {
      setImporting(false);
    }
  };

  // KPIs
  const totalCount = fixtures.length;
  const publishedCount = fixtures.filter((f) => f.publication_status === "PUBLISHED").length;
  const provisionalCount = fixtures.filter((f) => f.publication_status === "PROVISIONAL").length;
  const discrepancyCount = fixtures.filter((f) => f.has_discrepancy).length;
  const completedCount = fixtures.filter((f) => f.match_status === "FINISHED").length;

  // Filtered List
  const filtered = fixtures.filter((f) => {
    if (legFilter !== "ALL") {
      if (legFilter === "FIRST_LEG" && f.fixture_leg !== "FIRST_LEG") return false;
      if (legFilter === "SECOND_LEG" && f.fixture_leg !== "SECOND_LEG") return false;
    }
    if (search) {
      const q = search.toLowerCase();
      const hMatch = f.home_team?.name?.toLowerCase().includes(q);
      const aMatch = f.away_team?.name?.toLowerCase().includes(q);
      const numMatch = f.match_number ? f.match_number.toString() === q : false;
      const vMatch = f.venue?.name?.toLowerCase().includes(q) || f.venue?.city?.toLowerCase().includes(q);
      if (!hMatch && !aMatch && !numMatch && !vMatch) return false;
    }
    return true;
  });

  return (
    <Shell
      title="ISL 2026–27 Fixture Management"
      subtitle="Chennaiyin FC • 24-Match Full-Season Schedule & Verification Engine"
    >
      <div className="space-y-6">
        {/* Navigation & Action Ribbon */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#E2EAE3] pb-4">
          <div className="flex items-center space-x-2">
            <Link
              href="/matches"
              className="px-3.5 py-1.5 rounded-xl bg-white border border-[#E2EAE3] text-xs text-[#718078] hover:text-[#26332B] hover:border-[#246B45] transition-colors shadow-xs"
            >
              ← Back to Match Centre
            </Link>
            <span className="text-[#E2EAE3]">/</span>
            <span className="text-xs font-semibold text-[#26332B]">Full Season Fixtures</span>
          </div>

          <div className="flex items-center space-x-2.5">
            <button
              onClick={() => handleImport()}
              disabled={importing}
              className="px-4 py-2 rounded-xl bg-[#246B45] hover:bg-[#174B32] disabled:opacity-50 text-white text-xs font-bold flex items-center space-x-2 transition-all shadow-xs"
            >
              <RefreshCw className={clsx("w-3.5 h-3.5", importing && "animate-spin")} />
              <span>{importing ? "Importing 24 Fixtures..." : "Re-Sync Official 24 Fixtures"}</span>
            </button>

            <button
              onClick={() => setShowImportModal(!showImportModal)}
              className="px-3 py-2 rounded-xl bg-white border border-[#E2EAE3] text-[#26332B] hover:border-[#246B45] text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-xs"
            >
              <Upload className="w-3.5 h-3.5 text-[#718078]" />
              <span>Upload CSV/JSON</span>
            </button>
          </div>
        </div>

        {/* Custom Upload Modal */}
        {showImportModal && (
          <div className="p-4 bg-white border border-[#E2EAE3] rounded-2xl shadow-md space-y-3 max-w-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-[#26332B] flex items-center space-x-2">
                <Upload className="w-4 h-4 text-[#246B45]" />
                <span>Upload Custom Fixture Schedule (CSV or JSON)</span>
              </span>
              <button
                onClick={() => setShowImportModal(false)}
                className="text-[#718078] hover:text-[#26332B] text-xs"
              >
                ✕ Close
              </button>
            </div>
            <p className="text-[11px] text-[#718078] leading-relaxed">
              Upload an official or staging fixture file. Required columns: match_number, home_team, away_team, date, kickoff_ist, venue, fixture_leg. Scores remain null.
            </p>
            <input
              type="file"
              accept=".csv, .json, text/csv, application/json"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  handleImport(file);
                  setShowImportModal(false);
                }
              }}
              className="text-xs text-[#26332B] file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-[#246B45] file:text-white hover:file:bg-[#174B32] cursor-pointer"
            />
          </div>
        )}

        {/* Import Result Notification */}
        {importResult && (
          <div className="p-4 rounded-2xl bg-[#E6F0E7] border border-[#C3DEC7] flex items-center justify-between text-xs font-mono">
            <div className="flex items-center space-x-2 text-[#174B32]">
              <CheckCircle className="w-4 h-4 text-[#246B45] shrink-0" />
              <span>{importResult.message}</span>
            </div>
            <div className="flex items-center space-x-3 text-[11px] text-[#26332B]">
              <span>Published: <strong className="text-[#246B45]">{importResult.published_count}</strong></span>
              <span>Provisional: <strong className="text-[#D9A441]">{importResult.provisional_count}</strong></span>
              <span>Discrepancies: <strong className="text-[#C65B56]">{importResult.discrepancies_flagged}</strong></span>
            </div>
          </div>
        )}

        {/* Schedule Discrepancy Highlight Banner */}
        <div className="p-4 rounded-2xl bg-amber-50 border border-amber-200 flex items-start space-x-3.5 shadow-xs">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="text-xs space-y-1">
            <div className="flex items-center space-x-2">
              <span className="font-bold text-amber-900">Active Schedule Discrepancy Notice: Fixture #7</span>
              <Badge variant="rose" size="sm">FLAGGED FOR VERIFICATION</Badge>
            </div>
            <p className="text-amber-800 leading-relaxed">
              Chennaiyin FC&apos;s club announcement originally listed <strong>Mumbai City away on 30 November</strong>, while the official Indian Super League published schedule lists <strong>Chennaiyin FC at home on 28 November (7:30 PM IST)</strong>. MARINA INTELLIGENCE uses the official ISL listing as the primary working record while flagging the discrepancy for administrative confirmation.
            </p>
          </div>
        </div>

        {/* Summary KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
          <div className="bg-white border border-[#E2EAE3] p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-[#718078] text-xs mb-1">
              <span>Total Fixtures</span>
              <CalendarDays className="w-4 h-4 text-[#246B45]" />
            </div>
            <div className="text-2xl font-black text-[#26332B]">{totalCount}</div>
            <div className="text-[10px] text-[#718078] mt-1">12 Home • 12 Away</div>
          </div>

          <div className="bg-white border border-[#E2EAE3] p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-[#718078] text-xs mb-1">
              <span>Published (Phase 1)</span>
              <CheckCircle className="w-4 h-4 text-[#246B45]" />
            </div>
            <div className="text-2xl font-black text-[#246B45]">{publishedCount}</div>
            <div className="text-[10px] text-[#718078] mt-1">Official ISL Fixtures Confirmed</div>
          </div>

          <div className="bg-white border border-[#E2EAE3] p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-[#718078] text-xs mb-1">
              <span>Provisional (Phase 2)</span>
              <Clock className="w-4 h-4 text-[#D9A441]" />
            </div>
            <div className="text-2xl font-black text-[#D9A441]">{provisionalCount}</div>
            <div className="text-[10px] text-[#718078] mt-1">Inferred Venues / Return Leg</div>
          </div>

          <div className="bg-white border border-[#E2EAE3] p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-[#718078] text-xs mb-1">
              <span>Discrepancies</span>
              <AlertTriangle className="w-4 h-4 text-[#C65B56]" />
            </div>
            <div className="text-2xl font-black text-[#C65B56]">{discrepancyCount}</div>
            <div className="text-[10px] text-[#718078] mt-1">Fixture #7 Flagged</div>
          </div>

          <div className="bg-white border border-[#E2EAE3] p-4 rounded-2xl shadow-xs">
            <div className="flex items-center justify-between text-[#718078] text-xs mb-1">
              <span>Completed Matches</span>
              <ShieldCheck className="w-4 h-4 text-[#174B32]" />
            </div>
            <div className="text-2xl font-black text-[#174B32]">{completedCount}</div>
            <div className="text-[10px] text-[#718078] mt-1">Verified Final Results</div>
          </div>
        </div>

        {/* Filter and Search Bar */}
        <div className="bg-white border border-[#E2EAE3] p-4 rounded-2xl shadow-xs flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 text-[#718078] absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search opponent, venue or #..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-[#F4F8F4] border border-[#E2EAE3] rounded-xl pl-9 pr-3 py-1.5 text-xs text-[#26332B] placeholder-[#718078] focus:outline-none focus:border-[#246B45]"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto text-xs">
            {/* Home / Away */}
            <div className="flex bg-[#F4F8F4] p-1 rounded-xl border border-[#E2EAE3] font-semibold text-[11px]">
              {["ALL", "HOME", "AWAY"].map((ha) => (
                <button
                  key={ha}
                  onClick={() => setHomeAwayFilter(ha)}
                  className={clsx(
                    "px-2.5 py-1 rounded-lg transition-colors",
                    homeAwayFilter === ha ? "bg-[#246B45] text-white" : "text-[#718078] hover:text-[#26332B]"
                  )}
                >
                  {ha === "ALL" ? "All Venues" : ha === "HOME" ? "Home" : "Away"}
                </button>
              ))}
            </div>

            {/* Leg / Phase */}
            <div className="flex bg-[#F4F8F4] p-1 rounded-xl border border-[#E2EAE3] font-semibold text-[11px]">
              {["ALL", "FIRST_LEG", "SECOND_LEG"].map((l) => (
                <button
                  key={l}
                  onClick={() => setLegFilter(l)}
                  className={clsx(
                    "px-2.5 py-1 rounded-lg transition-colors",
                    legFilter === l ? "bg-[#246B45] text-white" : "text-[#718078] hover:text-[#26332B]"
                  )}
                >
                  {l === "ALL" ? "All Legs" : l === "FIRST_LEG" ? "1st Leg (Pub)" : "2nd Leg (Prov)"}
                </button>
              ))}
            </div>

            {/* Verification Status */}
            <div className="flex bg-[#F4F8F4] p-1 rounded-xl border border-[#E2EAE3] font-semibold text-[11px]">
              {[
                { key: "ALL", label: "All Status" },
                { key: "PUBLISHED", label: "Published" },
                { key: "PROVISIONAL", label: "Provisional" },
                { key: "DISCREPANCY_FLAGGED", label: "Flagged" },
              ].map((s) => (
                <button
                  key={s.key}
                  onClick={() => setStatusFilter(s.key)}
                  className={clsx(
                    "px-2.5 py-1 rounded-lg transition-colors",
                    statusFilter === s.key ? "bg-[#246B45] text-white" : "text-[#718078] hover:text-[#26332B]"
                  )}
                >
                  {s.label}
                </button>
              ))}
            </div>

            <button
              onClick={loadFixtures}
              className="p-1.5 rounded-xl bg-[#F4F8F4] border border-[#E2EAE3] text-[#718078] hover:text-[#26332B] transition-colors"
              title="Refresh Fixtures"
            >
              <RefreshCw className={clsx("w-4 h-4", loading && "animate-spin text-[#246B45]")} />
            </button>
          </div>
        </div>

        {/* Fixtures Table View */}
        <div className="bg-white border border-[#E2EAE3] rounded-2xl shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F4F8F4] border-b border-[#E2EAE3] text-[#718078] font-semibold tracking-wider uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4 w-12 text-center">#</th>
                  <th className="py-3 px-3">Date & Time (IST)</th>
                  <th className="py-3 px-4">Fixture (Home vs Away)</th>
                  <th className="py-3 px-3">Venue / Ground</th>
                  <th className="py-3 px-3 text-center">Leg / Phase</th>
                  <th className="py-3 px-3 text-center">Verification Status</th>
                  <th className="py-3 px-3 text-center">Score</th>
                  <th className="py-3 px-3 text-center w-20">Source</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2EAE3] font-medium text-[#26332B]">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-[#718078]">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-[#246B45]" />
                      <span>Loading Chennaiyin FC fixtures...</span>
                    </td>
                  </tr>
                ) : filtered.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-12 text-center text-[#718078]">
                      No fixtures matching the selected filters.
                    </td>
                  </tr>
                ) : (
                  filtered.map((f) => {
                    const isCfcHome = f.home_team?.slug === "chennaiyin-fc";
                    const isCompleted = f.match_status === "FINISHED";

                    return (
                      <tr
                        key={f.id}
                        className={clsx(
                          "hover:bg-[#F4F8F4]/80 transition-colors",
                          f.has_discrepancy && "bg-amber-50/60 border-l-2 border-l-[#D9A441]"
                        )}
                      >
                        {/* Match Number */}
                        <td className="py-3.5 px-4 text-center">
                          <span className="font-mono font-bold text-[#174B32] bg-[#E6F0E7] px-2 py-0.5 rounded border border-[#C3DEC7] text-[11px]">
                            #{f.match_number ?? "—"}
                          </span>
                        </td>

                        {/* Date & Time */}
                        <td className="py-3.5 px-3">
                          <div className="flex flex-col font-mono">
                            <span className="text-[#26332B] font-semibold flex items-center space-x-1.5">
                              <Calendar className="w-3.5 h-3.5 text-[#246B45]" />
                              <span>
                                {f.scheduled_kickoff
                                  ? new Date(f.scheduled_kickoff).toLocaleDateString("en-IN", {
                                    day: "numeric",
                                    month: "short",
                                    year: "numeric",
                                  })
                                  : "TBC"}
                              </span>
                            </span>
                            <span className="text-[10px] text-[#718078] flex items-center space-x-1 mt-0.5">
                              <Clock className="w-3 h-3 text-[#718078]" />
                              <span>{f.kickoff_time_ist || "TBC"}</span>
                            </span>
                          </div>
                        </td>

                        {/* Match Teams */}
                        <td className="py-3.5 px-4">
                          <div className="flex items-center space-x-2 text-xs">
                            {/* Home Team */}
                            <span
                              className={clsx(
                                "font-bold",
                                isCfcHome ? "text-[#246B45] font-extrabold" : "text-[#26332B]"
                              )}
                            >
                              {f.home_team?.name || "TBC"}
                            </span>
                            <span className="text-[#718078] font-normal">vs</span>
                            {/* Away Team */}
                            <span
                              className={clsx(
                                "font-bold",
                                !isCfcHome ? "text-[#246B45] font-extrabold" : "text-[#26332B]"
                              )}
                            >
                              {f.away_team?.name || "TBC"}
                            </span>

                            {/* Home/Away Tag for Chennaiyin */}
                            <span
                              className={clsx(
                                "text-[9px] font-bold px-1.5 py-0.2 rounded ml-1",
                                isCfcHome
                                  ? "bg-[#E6F0E7] text-[#174B32] border border-[#C3DEC7]"
                                  : "bg-sky-50 text-sky-800 border border-sky-200"
                              )}
                            >
                              {isCfcHome ? "HOME" : "AWAY"}
                            </span>
                          </div>
                        </td>

                        {/* Venue */}
                        <td className="py-3.5 px-3">
                          <div className="flex flex-col text-[#26332B]">
                            <span className="flex items-center space-x-1.5">
                              <MapPin className="w-3.5 h-3.5 text-[#246B45] shrink-0" />
                              <span className="truncate max-w-[200px]">
                                {f.venue ? f.venue.name : "TBC (Pending Announcement)"}
                              </span>
                            </span>
                            {f.venue_verification_status && (
                              <span className="text-[10px] text-[#718078] pl-5">
                                Ground: {f.venue_verification_status}
                              </span>
                            )}
                          </div>
                        </td>

                        {/* Leg / Phase */}
                        <td className="py-3.5 px-3 text-center">
                          <Badge
                            variant={f.fixture_leg === "FIRST_LEG" ? "blue" : "slate"}
                            size="sm"
                          >
                            {f.fixture_leg === "FIRST_LEG" ? "Phase 1" : "Return Leg"}
                          </Badge>
                        </td>

                        {/* Verification Status */}
                        <td className="py-3.5 px-3 text-center">
                          {isCompleted ? (
                            <Badge variant="green" size="sm">COMPLETED</Badge>
                          ) : f.has_discrepancy ? (
                            <Badge variant="rose" size="sm">FLAGGED</Badge>
                          ) : f.verification_status === "PUBLISHED" ? (
                            <Badge variant="green" size="sm">PUBLISHED</Badge>
                          ) : f.verification_status === "PENDING" ? (
                            <Badge variant="slate" size="sm">PENDING</Badge>
                          ) : (
                            <Badge variant="amber" size="sm">PROVISIONAL</Badge>
                          )}
                        </td>

                        {/* Score (Strictly Null if Upcoming) */}
                        <td className="py-3.5 px-3 text-center font-mono font-bold text-xs">
                          {isCompleted ? (
                            <span className="text-[#174B32] px-2 py-0.5 rounded bg-[#E6F0E7] border border-[#C3DEC7]">
                              {f.home_score} – {f.away_score}
                            </span>
                          ) : (
                            <span className="text-[#718078]">—</span>
                          )}
                        </td>

                        {/* Source / Details Action */}
                        <td className="py-3.5 px-3 text-center">
                          <div className="flex items-center justify-center space-x-1.5">
                            {f.source_url && (
                              <a
                                href={f.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="p-1 rounded bg-[#F4F8F4] hover:bg-[#E6F0E7] text-[#718078] hover:text-[#174B32] transition-colors border border-[#E2EAE3]"
                                title="Open Official ISL Fixture Source"
                              >
                                <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                            )}
                            <Link
                              href={`/matches/${f.id}`}
                              className="p-1 rounded bg-[#E6F0E7] hover:bg-[#246B45] text-[#174B32] hover:text-white transition-colors border border-[#C3DEC7]"
                              title="View Match Detail"
                            >
                              <ArrowRight className="w-3.5 h-3.5" />
                            </Link>
                          </div>
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
    </Shell>
  );
}
