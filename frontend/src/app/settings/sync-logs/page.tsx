"use client";

import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import { fetchDiscrepancies, fetchSyncLogs, triggerMatchSync } from "@/lib/api";
import { DataSyncLogItem, DataVerificationItem } from "@/lib/types";
import {
  Activity,
  AlertTriangle,
  RefreshCw,
  CheckCircle,
  Clock,
  Database,
  FileText,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";

export default function SyncLogsPage() {
  const [logs, setLogs] = useState<DataSyncLogItem[]>([]);
  const [discrepancies, setDiscrepancies] = useState<DataVerificationItem[]>([]);
  const [activeTab, setActiveTab] = useState<"LOGS" | "DISCREPANCIES">("LOGS");
  const [loading, setLoading] = useState<boolean>(true);
  const [syncing, setSyncing] = useState<boolean>(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    Promise.all([
      fetchSyncLogs(20).catch(() => []),
      fetchDiscrepancies(false, 50).catch(() => []),
    ]).then(([logsData, discData]) => {
      setLogs(logsData);
      setDiscrepancies(discData);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTriggerSync = async () => {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const res = await triggerMatchSync();
      setSyncMessage(res.message);
      loadData();
    } catch (err: any) {
      setSyncMessage(err.message || "Failed to trigger sync.");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <Shell
      title="Data Synchronization & Provenance Audit"
      subtitle="Audit match data ingestion, pipeline health, and multi-provider conflicting metrics"
    >
      {/* Top Action Ribbon */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-slate-900/90 border border-slate-800 rounded-2xl shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-blue-900/50 border border-blue-700/50 flex items-center justify-center text-blue-400">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white font-mono">Automated Ingestion Pipeline</h3>
            <p className="text-xs text-slate-400">
              Authoritative providers: ISL Official, FBref Ground Truth, Sportmonks, API-Football
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleTriggerSync}
            disabled={syncing}
            className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors disabled:opacity-50 shadow-md shadow-blue-900/30"
          >
            <Activity className={`w-3.5 h-3.5 mr-1.5 ${syncing ? "animate-spin" : ""}`} />
            <span>{syncing ? "Syncing Matches..." : "Run Match Sync"}</span>
          </button>
          <Link
            href="/settings"
            className="text-xs font-semibold px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition-colors"
          >
            Settings
          </Link>
        </div>
      </div>

      {syncMessage && (
        <div className="p-3.5 bg-blue-950/60 border border-blue-800/80 rounded-xl text-xs font-mono text-blue-200 flex items-center justify-between">
          <span>✓ {syncMessage}</span>
          <button onClick={() => setSyncMessage(null)} className="text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center space-x-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 w-fit text-xs font-semibold">
        <button
          onClick={() => setActiveTab("LOGS")}
          className={`px-4 py-2 rounded-lg transition-all ${
            activeTab === "LOGS"
              ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Synchronization Runs ({logs.length})
        </button>
        <button
          onClick={() => setActiveTab("DISCREPANCIES")}
          className={`px-4 py-2 rounded-lg transition-all ${
            activeTab === "DISCREPANCIES"
              ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
              : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Verification & Disputed Metrics ({discrepancies.length})
        </button>
      </div>

      {/* TAB 1: SYNC LOGS */}
      {activeTab === "LOGS" && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-widest font-mono">
              Pipeline Execution History
            </h4>
            <span className="text-[11px] font-mono text-slate-500">Updated in real time</span>
          </div>

          <div className="divide-y divide-slate-800/80">
            {logs.length > 0 ? (
              logs.map((log) => (
                <div key={log.id} className="p-4 hover:bg-slate-850/40 transition-colors space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={log.status === "SUCCESS" ? "green" : "amber"}>
                        {log.status}
                      </Badge>
                      <span className="text-xs font-mono font-bold text-white">{log.sync_type}</span>
                      <span className="text-xs text-slate-500 font-mono">• {log.provider_name}</span>
                    </div>
                    <span className="text-[11px] font-mono text-slate-400">
                      {new Date(log.created_at).toLocaleString()} ({log.duration_ms} ms)
                    </span>
                  </div>

                  {log.details && (
                    <p className="text-xs font-mono text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800">
                      {log.details}
                    </p>
                  )}

                  <div className="flex items-center space-x-4 text-[11px] font-mono text-slate-400">
                    <span>Matches: <strong className="text-slate-200">{log.matches_synced}</strong></span>
                    <span>Records: <strong className="text-slate-200">{log.records_updated}</strong></span>
                    <span>Discrepancies: <strong className="text-amber-400">{log.discrepancy_count}</strong></span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-slate-500 text-xs py-10 text-center font-mono">
                No synchronization logs recorded yet.
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: DISCREPANCIES */}
      {activeTab === "DISCREPANCIES" && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-200 uppercase tracking-widest font-mono">
              Data Verification Registry & Conflict Log
            </h4>
            <span className="text-[11px] font-mono text-slate-500">Strict Non-Fabrication Audit</span>
          </div>

          <div className="divide-y divide-slate-800/80">
            {discrepancies.length > 0 ? (
              discrepancies.map((d) => (
                <div key={d.id} className="p-4 hover:bg-slate-850/40 transition-colors space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <Badge variant={d.is_disputed ? "amber" : "blue"}>
                        {d.verification_status}
                      </Badge>
                      <span className="text-xs font-mono font-bold text-white">{d.metric_name}</span>
                      <span className="text-[11px] font-mono text-slate-500">({d.entity_type})</span>
                    </div>
                    {d.is_disputed && (
                      <span className="text-[10px] uppercase font-bold text-amber-400 bg-amber-950/60 border border-amber-800/60 px-2 py-0.5 rounded">
                        Conflicting Provider Feed
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
                    <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
                      <span className="text-slate-500 block text-[10px] uppercase font-bold">
                        Authoritative Source ({d.primary_source})
                      </span>
                      <span className="text-emerald-400 font-bold text-sm">{d.primary_value ?? "N/A"}</span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-950/70 border border-slate-800">
                      <span className="text-slate-500 block text-[10px] uppercase font-bold">
                        Secondary Feed ({d.secondary_source || "N/A"})
                      </span>
                      <span className="text-amber-300 font-bold text-sm">{d.secondary_value ?? "N/A"}</span>
                    </div>
                  </div>

                  {d.notes && (
                    <p className="text-xs text-slate-400 font-sans italic">
                      Note: {d.notes}
                    </p>
                  )}
                </div>
              ))
            ) : (
              <div className="text-slate-500 text-xs py-10 text-center font-mono">
                No discrepancies flagged.
              </div>
            )}
          </div>
        </div>
      )}
    </Shell>
  );
}
