"use client";

import React from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";

interface ShellProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export default function Shell({ children, title, subtitle }: ShellProps) {
  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-100 overflow-hidden font-sans">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-950/50">
          <div className="max-w-7xl mx-auto space-y-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
