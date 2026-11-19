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
    <div className="flex h-screen w-full bg-[#FFFFFF] text-[#26332B] overflow-hidden font-sans">
      {/* Fixed-Width Desktop Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden bg-[#F4F8F4]">
        <Header title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-y-auto p-5 md:p-7">
          <div className="max-w-7xl mx-auto space-y-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
