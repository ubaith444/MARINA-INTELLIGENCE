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
      <div className="h-64 flex items-center justify-center text-xs text-[#718078] font-mono">
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
        color: "#246B45", // Football Green
      },
      areaStyle: {
        color: "rgba(36, 107, 69, 0.20)",
      },
      itemStyle: {
        color: "#246B45",
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
        color: "#D9A441", // Match Amber
        type: "dashed",
      },
      areaStyle: {
        color: "rgba(217, 164, 65, 0.20)",
      },
      itemStyle: {
        color: "#D9A441",
      },
    });
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: "item",
      backgroundColor: "#FFFFFF",
      borderColor: "#E2EAE3",
      textStyle: { color: "#26332B", fontSize: 12 },
      extraCssText: "box-shadow: 0 2px 8px rgba(38, 51, 43, 0.08); border-radius: 8px;",
    },
    legend: {
      show: true,
      bottom: 0,
      textStyle: { color: "#718078", fontSize: 11, fontWeight: "bold" },
      icon: "circle",
    },
    radar: {
      indicator,
      shape: "polygon",
      splitNumber: 4,
      axisName: {
        color: "#26332B",
        fontSize: 10,
        fontWeight: "bold",
      },
      splitLine: {
        lineStyle: {
          color: "#E2EAE3",
        },
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ["#FFFFFF", "#F4F8F4"],
        },
      },
      axisLine: {
        lineStyle: {
          color: "#E2EAE3",
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
