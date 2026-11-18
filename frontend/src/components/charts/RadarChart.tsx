"use client";

import React from "react";
import * as echarts from "echarts";
import EChartsWrapper from "./EChartsWrapper";
import { RadarComparisonItem } from "@/lib/types";

interface RadarChartProps {
  dimensions: RadarComparisonItem[];
  playerAName?: string;
  playerBName?: string;
  height?: string;
}

export default function RadarChart({
  dimensions,
  playerAName = "Player A",
  playerBName,
  height = "320px",
}: RadarChartProps) {
  if (!dimensions || dimensions.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-xs text-slate-500 font-mono">
        No radar dimensions available
      </div>
    );
  }

  const indicator = dimensions.map((d) => ({
    name: d.dimension,
    max: 100,
  }));

  const dataA = dimensions.map((d) => d.player_a_score);
  const dataB = playerBName ? dimensions.map((d) => d.player_b_score) : null;

  const seriesData: any[] = [
    {
      value: dataA,
      name: playerAName,
      symbol: "circle",
      symbolSize: 6,
      lineStyle: {
        width: 2.5,
        color: "#3b82f6", // Marina Blue accent
      },
      areaStyle: {
        color: "rgba(59, 130, 246, 0.25)",
      },
      itemStyle: {
        color: "#60a5fa",
      },
    },
  ];

  if (playerBName && dataB) {
    seriesData.push({
      value: dataB,
      name: playerBName,
      symbol: "rect",
      symbolSize: 6,
      lineStyle: {
        width: 2,
        color: "#10b981", // Emerald Green
        type: "dashed",
      },
      areaStyle: {
        color: "rgba(16, 185, 129, 0.2)",
      },
      itemStyle: {
        color: "#34d399",
      },
    });
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: "item",
      backgroundColor: "#0f172a",
      borderColor: "#334155",
      textStyle: { color: "#f8fafc", fontSize: 12 },
    },
    legend: {
      show: true,
      bottom: 0,
      textStyle: { color: "#94a3b8", fontSize: 11 },
      icon: "circle",
    },
    radar: {
      indicator,
      shape: "polygon",
      splitNumber: 4,
      axisName: {
        color: "#94a3b8",
        fontSize: 10,
        fontWeight: "bold",
      },
      splitLine: {
        lineStyle: {
          color: "rgba(51, 65, 85, 0.6)",
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ["rgba(15, 23, 42, 0.4)", "rgba(30, 41, 59, 0.4)"],
        },
      },
      axisLine: {
        lineStyle: {
          color: "rgba(51, 65, 85, 0.8)",
        },
      },
    },
    series: [
      {
        type: "radar",
        data: seriesData,
      },
    ],
  };

  return <EChartsWrapper option={option} style={{ height }} />;
}
