"use client";

import React, { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import Badge from "@/components/ui/Badge";
import { API_BASE_URL, fetchHealth } from "@/lib/api";
import {
  Settings,
  Server,
  Database,
  ShieldCheck,
  CheckCircle,
  RefreshCw,
  Globe,
  Radio,
} from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<any>(null);
  const [testing, setTesting] = useState(false);
  const [latency, setLatency] = useState<number | null>(null);

  const runDiagnostics = () => {
    setTesting(true);
    const start = performance.now();
    fetchHealth()
      .then((data) => {
        const end = performance.now();
        setLatency(Math.round(end - start));
        setHealth(data);
        setTesting(false);
      })
      .catch((err) => {
        setHealth({ status: "offline", error: err.message });
        setTesting(false);
      });
  };

  useEffect(() => {
    runDiagnostics();
  }, []);

  return (
    <Shell
      title="Settings & System Diagnostics"
      subtitle="API Configuration • Data Provenance • Platform Integrity"
    >
      <div className="space-y-6 max-w-4xl">
        {/* Backend API Configuration */}
        <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-3">
              <Server className="w-5 h-5 text-blue-400" />
              <div>
                <h3 className="text-sm font-bold text-slate-100">FastAPI REST Backend Connection</h3>
                <p className="text-xs text-slate-400">Target server communicating with PostgreSQL 16</p>
              </div>
            </div>
            <button
              onClick={runDiagnostics}
              disabled={testing}
              className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${testing ? "animate-spin" : ""}`} />
              <span>Test Connection</span>
            </button>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
              <span className="text-slate-400 font-sans">Configured Endpoint:</span>
              <span className="text-blue-400 font-bold">{API_BASE_URL}</span>
            </div>

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
              <span className="text-slate-400 font-sans">Environment Variable:</span>
              <span className="text-slate-300">NEXT_PUBLIC_API_BASE_URL</span>
            </div>

            <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
              <span className="text-slate-400 font-sans">Connection Status:</span>
              <span className="flex items-center space-x-2">
                <span
                  className={`w-2 h-2 rounded-full ${
                    health?.status === "healthy" ? "bg-emerald-400" : "bg-amber-400"
                  }`}
                />
                <span className="font-bold text-slate-200">
                  {health?.status === "healthy" ? "HEALTHY (HTTP 200)" : "OFFLINE / DEMO MODE"}
                </span>
                {latency !== null && (
                  <span className="text-slate-500">({latency}ms)</span>
                )}
              </span>
            </div>
          </div>
        </section>

        {/* Data Provenance & Source Catalog */}
        <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
          <div className="flex items-center space-x-3 border-b border-slate-800 pb-3">
            <Database className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="text-sm font-bold text-slate-100">Authoritative Data Provenance</h3>
              <p className="text-xs text-slate-400">Primary evidence sources verified for Chennaiyin FC 2026–27</p>
            </div>
          </div>

          <div className="space-y-2.5 font-mono text-xs">
            {[
              { code: "ISL_OFFICIAL", name: "Indian Super League Official Match Centre", type: "OFFICIAL_LEAGUE", trust: "100/100" },
              { code: "CFC_OFFICIAL", name: "Chennaiyin FC Official Communications & Roster", type: "CLUB_COMMUNICATIONS", trust: "100/100" },
              { code: "AIFF_OFFICIAL", name: "All India Football Federation Competitions Registry", type: "FEDERATION", trust: "95/100" },
              { code: "MANUAL_CURATION", name: "Tactical Video Analyst CSV / JSON Ingestion", type: "MANUAL_CURATION", trust: "90/100" },
            ].map((src) => (
              <div
                key={src.code}
                className="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between"
              >
                <div>
                  <span className="text-slate-200 font-sans font-bold block">{src.name}</span>
                  <span className="text-[10px] text-slate-500">Provider: {src.type}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="green">Trust: {src.trust}</Badge>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Data Integrity Guarantees */}
        <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-3 text-xs">
          <div className="flex items-center space-x-3 border-b border-slate-800 pb-3">
            <ShieldCheck className="w-5 h-5 text-blue-400" />
            <h3 className="text-sm font-bold text-slate-100">Data Integrity & Anti-Fabrication Principles</h3>
          </div>

          <ul className="space-y-2 text-slate-400 font-sans leading-relaxed">
            <li className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span><strong>Strict Non-Fabrication:</strong> Upcoming fixtures and unfinished matches never have fabricated scores or artificial player statistics.</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span><strong>Null Preservation:</strong> Missing tracking metrics (e.g. Expected Goals, Distance Covered) remain NULL / None and are never converted to 0.</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-emerald-400 font-bold">✓</span>
              <span><strong>StatsBomb Isolation:</strong> Open data benchmarks are restricted to event processing algorithms and are never mixed with Chennaiyin FC production data.</span>
            </li>
          </ul>
        </section>
      </div>
    </Shell>
  );
}
