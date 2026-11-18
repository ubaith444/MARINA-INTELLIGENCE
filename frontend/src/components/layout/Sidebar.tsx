"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CalendarDays,
  Crosshair,
  Users,
  Shield,
  Settings,
  Activity,
  ChevronRight,
  Radio,
} from "lucide-react";
import { clsx } from "clsx";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: string;
}

const NAV_ITEMS: NavItem[] = [
  { name: "Season Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Match Centre", href: "/matches", icon: CalendarDays },
  { name: "Tactical Analysis", href: "/tactical", icon: Crosshair },
  { name: "Player Directory", href: "/players", icon: Users },
  { name: "Team Analysis", href: "/teams", icon: Shield },
  { name: "Settings & System", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-950 border-r border-slate-800/80 flex flex-col shrink-0 select-none">
      {/* Platform Crest & Brand */}
      <div className="h-16 px-5 border-b border-slate-800/80 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="h-10 w-10 rounded-xl bg-blue-800 flex items-center justify-center font-black text-white text-base tracking-wider border border-blue-500/40 shadow-lg shadow-blue-950/60 group-hover:scale-105 transition-transform">
            CFC
          </div>
          <div>
            <div className="flex items-center space-x-1">
              <span className="font-extrabold text-sm tracking-tight text-white">MARINA</span>
              <span className="font-light text-sm tracking-widest text-blue-400">INTEL</span>
            </div>
            <p className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">
              Chennaiyin FC Analytics
            </p>
          </div>
        </Link>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-5 px-3 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
          Performance Suite
        </div>
        {NAV_ITEMS.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all duration-150 group",
                isActive
                  ? "bg-blue-600/15 text-blue-400 border border-blue-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent"
              )}
            >
              <div className="flex items-center space-x-3">
                <Icon
                  className={clsx(
                    "w-4 h-4 transition-colors",
                    isActive
                      ? "text-blue-400"
                      : "text-slate-400 group-hover:text-slate-300"
                  )}
                />
                <span>{item.name}</span>
              </div>
              {isActive && (
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              )}
            </Link>
          );
        })}
      </div>

      {/* Current Season & Status Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/40 space-y-2">
        <div className="flex items-center justify-between px-2 text-[11px] text-slate-400">
          <span className="font-medium">Active Season</span>
          <span className="font-mono font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
            2026–27
          </span>
        </div>
        <div className="flex items-center justify-between px-2 text-[11px] text-slate-400">
          <span className="font-medium">Anchor Club</span>
          <span className="font-semibold text-blue-400">Chennaiyin FC</span>
        </div>
        <div className="pt-1 px-2 flex items-center space-x-1.5 text-[10px] text-emerald-400 font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
          <span>ISL Verified Source Pipeline</span>
        </div>
      </div>
    </aside>
  );
}
