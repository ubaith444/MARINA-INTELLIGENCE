"use client";

import React from "react";
import * as echarts from "echarts";
import EChartsWrapper from "./EChartsWrapper";

interface GoalTrendChartProps {
  categories?: string[];
  goalsScored?: number[];
  goalsConceded?: number[];
  height?: string;
}

export default function GoalTrendChart({
  categories = ["Match 1 (EBFC)", "Match 2 (KBFC)", "Match 3 (MCFC)"],
  goalsScored = [5, 1, 2],
  goalsConceded = [3, 1, 0],
  height = "280px",
}: GoalTrendChartProps) {
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: "axis",
      backgroundColor: "#0f172a",
      borderColor: "#334155",
      textStyle: { color: "#f8fafc", fontSize: 12 },
    },
    legend: {
      show: true,
      top: 0,
      right: 0,
      textStyle: { color: "#94a3b8", fontSize: 11 },
      icon: "roundRect",
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      top: "15%",
      containLabel: true,
    },
    xAxis: {
      type: "category",
      data: categories,
      axisLine: { lineStyle: { color: "#334155" } },
      axisLabel: { color: "#94a3b8", fontSize: 11 },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      splitLine: { lineStyle: { color: "rgba(51, 65, 85, 0.4)" } },
      axisLabel: { color: "#94a3b8", fontSize: 11 },
    },
    series: [
      {
        name: "Goals Scored",
        type: "bar",
        data: goalsScored,
        itemStyle: {
          color: "#3b82f6",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: "25%",
      },
      {
        name: "Goals Conceded",
        type: "bar",
        data: goalsConceded,
        itemStyle: {
          color: "#f43f5e",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: "25%",
      },
    ],
  };

  return <EChartsWrapper option={option} style={{ height }} />;
}
