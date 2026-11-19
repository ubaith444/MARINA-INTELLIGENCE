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
  Users,
  ArrowRight,
  Shield,
  Lock,
  UserCheck,
  SlidersHorizontal,
  FileSpreadsheet,
} from "lucide-react";
import Link from "next/link";

interface RolePermission {
  role: "OWNER" | "ADMINISTRATOR" | "ANALYST" | "VIEWER";
  title: string;
  description: string;
  permissions: {
    manageUsers: boolean;
    manageSquad: boolean;
    importDatasets: boolean;
    executeAiQueries: boolean;
    exportData: boolean;
    viewDashboards: boolean;
  };
}

const ROLES_MATRIX: RolePermission[] = [
  {
    role: "OWNER",
    title: "Club Executive / Technical Director",
    description: "Unrestricted administrative privileges, user role assignment, database configuration, and system migrations.",
    permissions: {
      manageUsers: true,
      manageSquad: true,
      importDatasets: true,
      executeAiQueries: true,
      exportData: true,
      viewDashboards: true,
    },
  },
  {
    role: "ADMINISTRATOR",
    title: "Performance Data Director",
    description: "Squad registration management, match log synchronization, CSV/Excel dataset ingestion, and data provenance auditing.",
    permissions: {
      manageUsers: false,
      manageSquad: true,
      importDatasets: true,
      executeAiQueries: true,
      exportData: true,
      viewDashboards: true,
    },
  },
  {
    role: "ANALYST",
    title: "Senior Tactical & Opposition Analyst",
    description: "Tactical breakdown authoring, AI analyst interrogation, and player performance evaluation.",
    permissions: {
      manageUsers: false,
      manageSquad: false,
      importDatasets: false,
      executeAiQueries: true,
      exportData: true,
      viewDashboards: true,
    },
  },
  {
    role: "VIEWER",
    title: "Staff & Management Stakeholder",
    description: "Read-only access to published performance dashboards, match centre logs, and player statistics.",
    permissions: {
      manageUsers: false,
      manageSquad: false,
      importDatasets: false,
      executeAiQueries: false,
      exportData: true,
      viewDashboards: true,
    },
  },
];

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
      title="Administration & System Diagnostics"
      subtitle="Role-based permissions, database health monitoring, dataset ingestion pipelines, and provenance governance."
    >
      <div className="space-y-6 max-w-5xl">
        {/* Backend API & Database Diagnostics */}
        <section className="bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
            <div className="flex items-center space-x-3">
              <Server className="w-5 h-5 text-[#246B45]" />
              <div>
                <h3 className="text-sm font-bold text-[#174B32]">REST Backend & Database Diagnostics</h3>
                <p className="text-xs text-[#718078]">FastAPI application layer communicating with persistent database</p>
              </div>
            </div>
            <button
              onClick={runDiagnostics}
              disabled={testing}
              className="px-3 py-1.5 rounded-lg bg-[#246B45] hover:bg-[#174B32] text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${testing ? "animate-spin" : ""}`} />
              <span>Test Connection</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
            <div className="p-3 bg-[#F4F8F4] rounded-lg border border-[#E2EAE3]">
              <span className="text-[#718078] font-sans block text-[11px]">Configured API Endpoint</span>
              <span className="text-[#174B32] font-bold text-xs truncate block mt-0.5">{API_BASE_URL}</span>
            </div>

            <div className="p-3 bg-[#F4F8F4] rounded-lg border border-[#E2EAE3]">
              <span className="text-[#718078] font-sans block text-[11px]">Database Schema Status</span>
              <span className="text-[#174B32] font-bold text-xs block mt-0.5">23 Tables Synced</span>
            </div>

            <div className="p-3 bg-[#F4F8F4] rounded-lg border border-[#E2EAE3]">
              <span className="text-[#718078] font-sans block text-[11px]">System Health & Latency</span>
              <span className="flex items-center space-x-2 mt-0.5">
                <span
                  className={`w-2 h-2 rounded-full ${
                    health?.status === "healthy" ? "bg-[#246B45]" : "bg-amber-500"
                  }`}
                />
                <span className="font-bold text-[#26332B] font-sans">
                  {health?.status === "healthy" ? "HEALTHY (HTTP 200)" : "OFFLINE / LOCAL"}
                </span>
                {latency !== null && <span className="text-[#718078]">({latency}ms)</span>}
              </span>
            </div>
          </div>
        </section>

        {/* Role-Based Access Control (RBAC) Permissions Matrix */}
        <section className="bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
            <div className="flex items-center space-x-3">
              <Lock className="w-5 h-5 text-[#246B45]" />
              <div>
                <h3 className="text-sm font-bold text-[#174B32]">Role-Based Access Control (RBAC) Matrix</h3>
                <p className="text-xs text-[#718078]">Permissions enforced across Owner, Administrator, Analyst, and Viewer tiers</p>
              </div>
            </div>
            <Badge variant="verified">STRICT ROLE GOVERNANCE</Badge>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F4F8F4] text-[#718078] border-b border-[#E2EAE3] font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Role & Title</th>
                  <th className="py-2.5 px-3 text-center">User Admin</th>
                  <th className="py-2.5 px-3 text-center">Squad Sync</th>
                  <th className="py-2.5 px-3 text-center">Dataset Ingestion</th>
                  <th className="py-2.5 px-3 text-center">AI Interrogation</th>
                  <th className="py-2.5 px-3 text-center">Export Data</th>
                  <th className="py-2.5 px-3 text-center">View Dashboard</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2EAE3] text-[#26332B]">
                {ROLES_MATRIX.map((r) => (
                  <tr key={r.role} className="hover:bg-[#F4F8F4]/60">
                    <td className="py-3 px-3">
                      <div className="font-bold text-[#174B32]">{r.role}</div>
                      <div className="text-[11px] text-[#718078]">{r.title}</div>
                    </td>
                    <td className="py-3 px-3 text-center">
                      {r.permissions.manageUsers ? (
                        <CheckCircle className="w-4 h-4 text-[#246B45] mx-auto" />
                      ) : (
                        <span className="text-[#718078]">—</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {r.permissions.manageSquad ? (
                        <CheckCircle className="w-4 h-4 text-[#246B45] mx-auto" />
                      ) : (
                        <span className="text-[#718078]">—</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {r.permissions.importDatasets ? (
                        <CheckCircle className="w-4 h-4 text-[#246B45] mx-auto" />
                      ) : (
                        <span className="text-[#718078]">—</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {r.permissions.executeAiQueries ? (
                        <CheckCircle className="w-4 h-4 text-[#246B45] mx-auto" />
                      ) : (
                        <span className="text-[#718078]">—</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {r.permissions.exportData ? (
                        <CheckCircle className="w-4 h-4 text-[#246B45] mx-auto" />
                      ) : (
                        <span className="text-[#718078]">—</span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-center">
                      {r.permissions.viewDashboards ? (
                        <CheckCircle className="w-4 h-4 text-[#246B45] mx-auto" />
                      ) : (
                        <span className="text-[#718078]">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Squad Management & Sync Console Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <section className="bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
              <div className="flex items-center space-x-2.5">
                <Users className="w-5 h-5 text-[#246B45]" />
                <h3 className="text-sm font-bold text-[#174B32]">Squad Roster & Registration</h3>
              </div>
              <Link
                href="/settings/squad"
                className="px-2.5 py-1 rounded-md bg-[#F4F8F4] hover:bg-[#E6F0E7] text-[#174B32] text-xs font-semibold flex items-center space-x-1 transition-colors border border-[#E2EAE3]"
              >
                <span>Console</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            <p className="text-xs text-[#718078]">
              Manage 28 registered Chennaiyin FC squad players, contracts, historical memberships, and squad numbers.
            </p>
          </section>

          <section className="bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-5 shadow-xs space-y-3">
            <div className="flex items-center justify-between border-b border-[#E2EAE3] pb-3">
              <div className="flex items-center space-x-2.5">
                <Radio className="w-5 h-5 text-[#246B45]" />
                <h3 className="text-sm font-bold text-[#174B32]">Match Synchronization & Logs</h3>
              </div>
              <Link
                href="/settings/sync-logs"
                className="px-2.5 py-1 rounded-md bg-[#F4F8F4] hover:bg-[#E6F0E7] text-[#174B32] text-xs font-semibold flex items-center space-x-1 transition-colors border border-[#E2EAE3]"
              >
                <span>Logs</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            <p className="text-xs text-[#718078]">
              Inspect data pipeline executions, sync logs, duplicate resolutions, and provider feed discrepancies.
            </p>
          </section>
        </div>

        {/* Data Provenance & Authoritative Sources */}
        <section className="bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-5 shadow-xs space-y-4">
          <div className="flex items-center space-x-3 border-b border-[#E2EAE3] pb-3">
            <Database className="w-5 h-5 text-[#246B45]" />
            <div>
              <h3 className="text-sm font-bold text-[#174B32]">Authoritative Data Sources</h3>
              <p className="text-xs text-[#718078]">Verified competition feeds and curation engines powering MARINA INTELLIGENCE</p>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            {[
              { code: "ISL_OFFICIAL", name: "Indian Super League Official Match Centre", type: "OFFICIAL_LEAGUE", trust: "100/100" },
              { code: "CFC_OFFICIAL", name: "Chennaiyin FC Official Communications & Roster", type: "CLUB_COMMUNICATIONS", trust: "100/100" },
              { code: "AIFF_OFFICIAL", name: "All India Football Federation Competitions Registry", type: "FEDERATION", trust: "95/100" },
              { code: "MANUAL_CURATION", name: "Tactical Video Analyst CSV / JSON Ingestion", type: "MANUAL_CURATION", trust: "90/100" },
            ].map((src) => (
              <div
                key={src.code}
                className="p-3 bg-[#F4F8F4] rounded-lg border border-[#E2EAE3] flex items-center justify-between"
              >
                <div>
                  <span className="text-[#174B32] font-bold block">{src.name}</span>
                  <span className="text-[11px] text-[#718078]">Source Type: {src.type}</span>
                </div>
                <Badge variant="verified">Trust: {src.trust}</Badge>
              </div>
            ))}
          </div>
        </section>

        {/* Data Integrity Guarantees */}
        <section className="bg-[#FFFFFF] border border-[#E2EAE3] rounded-xl p-5 shadow-xs space-y-3 text-xs">
          <div className="flex items-center space-x-3 border-b border-[#E2EAE3] pb-3">
            <ShieldCheck className="w-5 h-5 text-[#246B45]" />
            <h3 className="text-sm font-bold text-[#174B32]">Non-Negotiable Data Integrity Standards</h3>
          </div>

          <ul className="space-y-2 text-[#26332B] leading-relaxed">
            <li className="flex items-start space-x-2">
              <span className="text-[#246B45] font-bold">✓</span>
              <span><strong>Strict Non-Fabrication:</strong> Unplayed fixtures (Matches 6 to 24) are flagged SCHEDULED with zero fabricated scores or player statistics.</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-[#246B45] font-bold">✓</span>
              <span><strong>Null Preservation:</strong> Missing tracking metrics (e.g. optical distance, acceleration) remain NULL and are never silently replaced with zero.</span>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-[#246B45] font-bold">✓</span>
              <span><strong>Isolated Benchmarks:</strong> Open-source data benchmarks are strictly used for formula testing and never contaminate club production tables.</span>
            </li>
          </ul>
        </section>
      </div>
    </Shell>
  );
}
