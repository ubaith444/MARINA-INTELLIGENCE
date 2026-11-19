"use client";

import React from "react";
import * as echarts from "echarts";
import EChartsWrapper from "./EChartsWrapper";

interface XgDistributionChartProps {
  tiers?: {
    bin: string;
    shots: number;
    goals: number;
  }[];
  height?: string;
}

export default function XgDistributionChart({
  tiers = [
    { bin: "0.00–0.10 (Low)", shots: 9, goals: 0 },
    { bin: "0.10–0.25 (Fair)", shots: 3, goals: 0 },
    { bin: "0.25–0.50 (High)", shots: 4, goals: 4 },
    { bin: ">0.50 (Big Chance)", shots: 2, goals: 2 },
  ],
  height = "260px",
}: XgDistributionChartProps) {
  const bins = tiers.map((t) => t.bin);
  const nonGoals = tiers.map((t) => t.shots - t.goals);
  const goals = tiers.map((t) => t.goals);

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "shadow" },
      backgroundColor: "#FFFFFF",
      borderColor: "#E2EAE3",
      textStyle: { color: "#26332B", fontSize: 12, fontFamily: "monospace" },
      extraCssText: "box-shadow: 0 4px 12px rgba(38, 51, 43, 0.08); border-radius: 8px;",
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
      right: "4%",
      bottom: "5%",
      top: "16%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: bins,
      axisLine: { lineStyle: { color: "#CBDAD0" } },
      axisLabel: { color: "#718078", fontSize: 10, fontFamily: "monospace" },
    },
    yAxis: {
      type: "value",
      axisLine: { lineStyle: { color: "#CBDAD0" } },
      splitLine: { lineStyle: { color: "#F0F5F1", type: "dashed" } },
      axisLabel: { color: "#718078", fontSize: 10, fontFamily: "monospace" },
    },
    series: [
      {
        name: "Goals Converted",
        type: "bar",
        stack: "total",
        data: goals,
        itemStyle: {
          color: "#246B45",
        },
        barWidth: 22,
      },
      {
        name: "Saved / Blocked / Missed",
        type: "bar",
        stack: "total",
        data: nonGoals,
        itemStyle: {
          color: "#CBDAD0",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: 22,
      },
    ],
  };

  return <EChartsWrapper option={option} height={height} />;
}
