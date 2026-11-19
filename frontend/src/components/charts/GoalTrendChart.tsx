"use client";

import React from "react";
import * as echarts from "echarts";
import { useRouter } from "next/navigation";
import EChartsWrapper from "./EChartsWrapper";
import { ArrowUpRight, MapPin, Calendar, CheckCircle2 } from "lucide-react";

export interface GoalTrendMatchItem {
  match_id: string;
  match_number: number;
  opponent_name: string;
  opponent_short?: string;
  is_home: boolean;
  goals_scored: number;
  goals_conceded: number;
  result: "WIN" | "DRAW" | "LOSS" | "W" | "D" | "L";
  date?: string;
}

interface GoalTrendChartProps {
  matches?: GoalTrendMatchItem[];
  categories?: string[];
  goalsScored?: number[];
  goalsConceded?: number[];
  height?: string;
  onMatchClick?: (matchId: string) => void;
}

export default function GoalTrendChart({
  matches = [],
  categories,
  goalsScored,
  goalsConceded,
  height = "260px",
  onMatchClick,
}: GoalTrendChartProps) {
  const router = useRouter();

  const handleMatchClick = (matchId: string) => {
    if (onMatchClick) {
      onMatchClick(matchId);
    } else {
      router.push(`/matches/${matchId}`);
    }
  };

  // Derive categories and scores from matches if provided, otherwise fallback to props
  const chartMatches: GoalTrendMatchItem[] = React.useMemo(() => {
    if (matches && matches.length > 0) {
      return [...matches].sort((a, b) => a.match_number - b.match_number);
    }
    // Fallback if legacy categories/scores passed
    if (categories && categories.length > 0) {
      return categories.map((cat, idx) => ({
        match_id: `m-${idx + 1}`,
        match_number: idx + 1,
        opponent_name: cat,
        opponent_short: cat.slice(0, 4),
        is_home: true,
        goals_scored: goalsScored?.[idx] ?? 0,
        goals_conceded: goalsConceded?.[idx] ?? 0,
        result: (goalsScored?.[idx] ?? 0) > (goalsConceded?.[idx] ?? 0) ? "WIN" : (goalsScored?.[idx] ?? 0) === (goalsConceded?.[idx] ?? 0) ? "DRAW" : "LOSS",
      }));
    }
    return [];
  }, [matches, categories, goalsScored, goalsConceded]);

  const xLabels = chartMatches.map((m) => {
    const opp = m.opponent_short || m.opponent_name.replace(" FC", "").replace(" SG", "");
    return `M#${m.match_number}\n${opp} (${m.is_home ? "H" : "A"})`;
  });

  const scoredData = chartMatches.map((m) => m.goals_scored);
  const concededData = chartMatches.map((m) => m.goals_conceded);

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: "axis",
      backgroundColor: "#FFFFFF",
      borderColor: "#E2EAE3",
      padding: [10, 14],
      textStyle: { color: "#26332B", fontSize: 12 },
      extraCssText: "box-shadow: 0 4px 16px rgba(38, 51, 43, 0.12); border-radius: 10px;",
      formatter: (params: any) => {
        if (!Array.isArray(params) || params.length === 0) return "";
        const idx = params[0].dataIndex;
        const item = chartMatches[idx];
        if (!item) return "";

        const venueBadge = item.is_home ? "Home (JLN Marina Arena)" : "Away Match";
        const resColor =
          item.result === "WIN" || item.result === "W"
            ? "#246B45"
            : item.result === "DRAW" || item.result === "D"
            ? "#D9A441"
            : "#C65B56";

        return `
          <div style="font-family: inherit; font-size: 11px;">
            <div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 6px; border-bottom: 1px solid #E2EAE3; padding-bottom: 4px;">
              <strong style="color: #174B32; font-size: 12px;">Match #${item.match_number}</strong>
              <span style="color: #718078;">${item.date || ""}</span>
            </div>
            <div style="margin-bottom: 4px;">
              <span style="color: #718078;">Opponent:</span>
              <strong style="color: #26332B; margin-left: 4px;">${item.opponent_name}</strong>
              <span style="display: inline-block; background: #F4F8F4; border: 1px solid #E2EAE3; padding: 1px 5px; border-radius: 4px; font-size: 10px; margin-left: 4px;">${item.is_home ? "Home" : "Away"}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
              <span style="color: #246B45; font-weight: bold;">Goals Scored (CFC):</span>
              <strong style="color: #246B45;">${item.goals_scored}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
              <span style="color: #C65B56; font-weight: bold;">Goals Conceded:</span>
              <strong style="color: #C65B56;">${item.goals_conceded}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px dashed #E2EAE3; padding-top: 4px; margin-top: 4px;">
              <span style="color: #718078;">Result:</span>
              <span style="font-weight: bold; color: ${resColor};">${item.result} (${item.goals_scored}-${item.goals_conceded})</span>
            </div>
            <div style="color: #246B45; font-size: 10px; margin-top: 6px; font-weight: bold; text-align: right;">
              Click to view Match Centre →
            </div>
          </div>
        `;
      },
    },
    legend: {
      show: true,
      top: 0,
      right: 0,
      textStyle: { color: "#718078", fontSize: 11, fontWeight: "bold" },
      icon: "roundRect",
    },
    grid: {
      left: "3%",
      right: "3%",
      bottom: "8%",
      top: "16%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: xLabels,
      axisLine: { lineStyle: { color: "#CBDAD0" } },
      axisLabel: {
        color: "#26332B",
        fontSize: 10,
        fontWeight: "bold",
        lineHeight: 14,
        interval: 0,
      },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      splitLine: { lineStyle: { color: "#E2EAE3" } },
      axisLabel: { color: "#718078", fontSize: 11 },
    },
    series: [
      {
        name: "Goals Scored",
        type: "bar",
        data: scoredData,
        itemStyle: {
          color: "#246B45",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: "26%",
      },
      {
        name: "Goals Conceded",
        type: "bar",
        data: concededData,
        itemStyle: {
          color: "#C65B56",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: "26%",
      },
    ],
  };

  const onEvents = {
    click: (params: any) => {
      const idx = params.dataIndex;
      const match = chartMatches[idx];
      if (match && match.match_id) {
        handleMatchClick(match.match_id);
      }
    },
  };

  return (
    <div className="space-y-3">
      <EChartsWrapper option={option} style={{ height }} onEvents={onEvents} />

      {/* Match-by-Match Cards Strip with Direct Navigation */}
      {chartMatches.length > 0 && (
        <div className="pt-2 border-t border-[#E2EAE3]">
          <div className="text-[10px] font-mono uppercase tracking-wider text-[#718078] mb-2 flex items-center justify-between">
            <span>Verified Fixture Logs (Click card to open Match Centre)</span>
            <span className="text-[#246B45] font-bold">{chartMatches.length} Matches</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
            {chartMatches.map((m) => {
              const isWin = m.result === "WIN" || m.result === "W";
              const isDraw = m.result === "DRAW" || m.result === "D";
              return (
                <div
                  key={m.match_id}
                  onClick={() => handleMatchClick(m.match_id)}
                  className="group p-2.5 bg-[#F4F8F4] hover:bg-[#E6F0E7] border border-[#E2EAE3] hover:border-[#246B45] rounded-lg cursor-pointer transition-all flex flex-col justify-between"
                  title={`Open Match #${m.match_number} Centre: vs ${m.opponent_name}`}
                >
                  <div className="flex items-center justify-between text-[11px] font-mono mb-1">
                    <span className="font-bold text-[#26332B]">M#{m.match_number}</span>
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        isWin
                          ? "bg-[#E6F0E7] text-[#246B45] border border-[#C3DEC7]"
                          : isDraw
                          ? "bg-[#FEF3C7] text-[#92400E] border border-[#FDE68A]"
                          : "bg-[#FEE2E2] text-[#991B1B] border border-[#FECACA]"
                      }`}
                    >
                      {isWin ? "W" : isDraw ? "D" : "L"} ({m.goals_scored}–{m.goals_conceded})
                    </span>
                  </div>

                  <div className="truncate text-xs font-bold text-[#174B32] group-hover:text-[#246B45] flex items-center justify-between">
                    <span className="truncate">{m.opponent_name}</span>
                    <ArrowUpRight className="w-3 h-3 text-[#718078] group-hover:text-[#246B45] shrink-0 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-[#718078] mt-1 font-mono">
                    <span>{m.is_home ? "Home (JLN)" : "Away"}</span>
                    <span>{m.date || ""}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
