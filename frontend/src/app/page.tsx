import React from "react";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-lg bg-blue-700 flex items-center justify-center font-black text-white text-lg tracking-wider border border-blue-500/30 shadow-lg shadow-blue-900/30">
              MI
            </div>
            <div>
              <span className="font-bold text-lg tracking-tight text-white">MARINA</span>
              <span className="font-light text-lg tracking-widest text-blue-400 ml-1">INTELLIGENCE</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700 text-xs">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300 font-medium">FastAPI v0.1.0 Ready</span>
            </div>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs bg-blue-600 hover:bg-blue-500 text-white font-medium px-3.5 py-1.5 rounded-lg transition-colors"
            >
              OpenAPI Docs
            </a>
          </div>
        </div>
      </header>

      {/* Main Content Hero */}
      <div className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
        {/* Context Focus Bar */}
        <section className="bg-gradient-to-r from-blue-950/80 via-slate-900 to-slate-900 border border-blue-900/40 rounded-2xl p-6 shadow-xl relative overflow-hidden">
          <div className="absolute right-0 top-0 bottom-0 w-96 bg-gradient-to-l from-blue-600/10 to-transparent pointer-events-none" />
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div>
              <div className="flex items-center space-x-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
                <span>Phase 1 Architecture Foundation</span>
                <span>•</span>
                <span>ISL 2026–27</span>
              </div>
              <h1 className="text-3xl font-extrabold text-white tracking-tight">
                Chennaiyin FC Performance Analytics
              </h1>
              <p className="text-slate-400 text-sm mt-1 max-w-2xl">
                Normalized relational data modeling, strictly non-fabricated football statistics,
                and provenance-verified ingestion pipeline for the Marina Machans.
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3">
                <span className="text-xs text-slate-500 uppercase font-mono">Anchor Club</span>
                <p className="font-semibold text-sm text-slate-200">Chennaiyin FC</p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3">
                <span className="text-xs text-slate-500 uppercase font-mono">Season Target</span>
                <p className="font-semibold text-sm text-blue-300">2026–27 (ISL)</p>
              </div>
              <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3">
                <span className="text-xs text-slate-500 uppercase font-mono">Home Venue</span>
                <p className="font-semibold text-sm text-slate-200">Marina Arena</p>
              </div>
            </div>
          </div>
        </section>

        {/* Architectural Highlights Grid */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-3">
            <div className="h-10 w-10 rounded-lg bg-blue-900/40 border border-blue-700/50 flex items-center justify-center text-blue-400 font-bold">
              01
            </div>
            <h3 className="text-lg font-bold text-white">Strict Data Integrity</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              No fabrication of 2026–27 match scores or player metrics. Missing metrics strictly remain
              <code className="bg-slate-800 px-1.5 py-0.5 rounded text-amber-300 font-mono text-xs ml-1">null</code>
              rather than misleading zero placeholders.
            </p>
          </div>

          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-3">
            <div className="h-10 w-10 rounded-lg bg-indigo-900/40 border border-indigo-700/50 flex items-center justify-center text-indigo-400 font-bold">
              02
            </div>
            <h3 className="text-lg font-bold text-white">Decoupled Player Identity</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Intrinsic human player identities are decoupled from seasonal club squad registrations, ensuring full
              fidelity across transfer windows and career progression.
            </p>
          </div>

          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 space-y-3">
            <div className="h-10 w-10 rounded-lg bg-emerald-900/40 border border-emerald-700/50 flex items-center justify-center text-emerald-400 font-bold">
              03
            </div>
            <h3 className="text-lg font-bold text-white">Provenance & Verification</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Every data point tracks its authoritative source provenance, import batch audit logs, and
              verification status (<span className="text-emerald-400 text-xs font-semibold">OFFICIAL</span>, <span className="text-blue-400 text-xs font-semibold">VERIFIED</span>, <span className="text-amber-400 text-xs font-semibold">PROVISIONAL</span>).
            </p>
          </div>
        </section>

        {/* Domain Models & Verification Checklist */}
        <section className="bg-slate-900/40 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-base font-semibold text-slate-200 uppercase tracking-wider font-mono">
            Step 1 Verified Core Domains
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs">
            {[
              "Competitions",
              "Seasons",
              "Venues",
              "Teams",
              "Players",
              "Squad Registrations",
              "Matches",
              "Lineups",
              "Match Events",
              "Team Statistics",
              "Player Statistics",
              "Data Sources",
              "Import History",
            ].map((domain) => (
              <div
                key={domain}
                className="bg-slate-950 border border-slate-800/80 rounded-lg px-3 py-2 text-slate-300 flex items-center space-x-2"
              >
                <span className="text-emerald-400">✓</span>
                <span className="font-medium">{domain}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500">
        MARINA INTELLIGENCE © 2026. Built with FastAPI, PostgreSQL, SQLAlchemy 2, Alembic, Next.js, and Tailwind CSS.
      </footer>
    </main>
  );
}
