"use client";

import React, { useState, Suspense } from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  CalendarDays,
  Shield,
  Users,
  Network,
  Crosshair,
  Compass,
  Bot,
  ShieldCheck,
  SlidersHorizontal,
  Menu,
  X,
} from "lucide-react";
import { clsx } from "clsx";

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  exact?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard, exact: true },
  { name: "Team Analytics", href: "/teams", icon: Shield },
  { name: "Match Centre", href: "/matches", icon: CalendarDays },
  { name: "Player Profiles", href: "/players", icon: Users },
  { name: "Tactical Intelligence", href: "/tactical", icon: Compass },
  { name: "Advanced Analytics", href: "/intelligence", icon: Crosshair },
  { name: "AI Football Analyst", href: "/analyst", icon: Bot },
  { name: "Data Sources & Quality", href: "/data-quality", icon: ShieldCheck },
  { name: "Administration & Audit", href: "/settings", icon: SlidersHorizontal },
];

function SidebarInner() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isItemActive = (item: NavItem) => {
    if (item.exact) {
      return pathname === item.href;
    }
    return pathname.startsWith(item.href);
  };

  const navContent = (
    <div className="flex flex-col h-full bg-[#FFFFFF] border-r border-[#E2EAE3]">
      {/* Platform Crest & Club Brand */}
      <div className="h-16 px-5 border-b border-[#E2EAE3] flex items-center justify-between bg-[#FFFFFF]">
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="h-9 w-9 rounded-lg bg-[#246B45] flex items-center justify-center font-bold text-white text-xs tracking-wider shadow-sm group-hover:bg-[#174B32] transition-colors">
            CFC
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-extrabold text-sm tracking-tight text-[#174B32]">MARINA</span>
              <span className="font-medium text-sm tracking-wide text-[#246B45]">INTEL</span>
            </div>
            <p className="text-[10px] text-[#718078] font-semibold tracking-wider uppercase">
              Performance Department
            </p>
          </div>
        </Link>
        {/* Mobile close button */}
        <button
          onClick={() => setMobileOpen(false)}
          className="md:hidden text-[#718078] hover:text-[#26332B] p-1"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation Items (12 Items) */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold text-[#718078] uppercase tracking-wider">
          Performance Suite
        </div>
        {NAV_ITEMS.map((item, idx) => {
          const active = isItemActive(item);
          const Icon = item.icon;

          return (
            <Link
              key={idx}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={clsx(
                "flex items-center space-x-3 px-3 py-2 rounded-lg text-xs font-medium transition-all",
                active
                  ? "bg-[#E6F0E7] text-[#174B32] font-semibold border-l-3 border-[#246B45] shadow-[0_1px_2px_rgba(36,107,69,0.08)]"
                  : "text-[#718078] hover:bg-[#F4F8F4] hover:text-[#26332B]"
              )}
            >
              <Icon
                className={clsx(
                  "w-4 h-4 shrink-0 transition-colors",
                  active ? "text-[#246B45]" : "text-[#718078]"
                )}
              />
              <span className="truncate">{item.name}</span>
            </Link>
          );
        })}
      </div>

      {/* Sidebar Footer: Club Identity */}
      <div className="p-4 border-t border-[#E2EAE3] bg-[#F4F8F4]">
        <div className="flex items-center space-x-2.5">
          <div className="w-2 h-2 rounded-full bg-[#246B45]" />
          <div className="truncate">
            <span className="block text-xs font-bold text-[#26332B] truncate">
              Chennaiyin FC
            </span>
            <span className="block text-[10px] font-mono text-[#718078]">
              Indian Super League 2026–27
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed-Width Sidebar (w-64) */}
      <aside className="hidden md:flex w-64 flex-col shrink-0 select-none h-screen z-20">
        {navContent}
      </aside>

      {/* Mobile Menu Trigger Header */}
      <div className="md:hidden fixed top-3 left-3 z-50">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-lg bg-[#FFFFFF] border border-[#E2EAE3] text-[#26332B] shadow-md"
          aria-label="Open Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>

      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0 bg-black/30 backdrop-blur-xs"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative w-64 max-w-full h-full z-10">
            {navContent}
          </div>
        </div>
      )}
    </>
  );
}

export default function Sidebar() {
  return (
    <Suspense fallback={<aside className="hidden md:flex w-64 flex-col shrink-0 bg-[#FFFFFF] border-r border-[#E2EAE3] h-screen" />}>
      <SidebarInner />
    </Suspense>
  );
}
