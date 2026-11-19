"use client";

import React from "react";
import * as echarts from "echarts";
import EChartsWrapper from "./EChartsWrapper";

interface XgMatchComparisonChartProps {
  matches?: {
    match_number: number;
    opponent_name: string;
    goals: number;
    expected_goals: number;
  }[];
  height?: string;
}

export default function XgMatchComparisonChart({
  matches = [
    { match_number: 1, opponent_name: "FC Goa", goals: 1, expected_goals: 0.61 },
    { match_number: 2, opponent_name: "Bengaluru FC", goals: 0, expected_goals: 0.21 },
    { match_number: 3, opponent_name: "Mohun Bagan SG", goals: 0, expected_goals: 0.20 },
    { match_number: 4, opponent_name: "Kerala Blasters", goals: 0, expected_goals: 0.20 },
    { match_number: 5, opponent_name: "East Bengal", goals: 5, expected_goals: 2.19 },
  ],
  height = "260px",
}: XgMatchComparisonChartProps) {
  const categories = matches.map((m) => `M#${m.match_number} vs ${m.opponent_name.split(" ")[0]}`);
  const actualGoals = matches.map((m) => m.goals);
  const expectedGoals = matches.map((m) => m.expected_goals);

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: "axis",
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
      data: categories,
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
        name: "Actual Goals",
        type: "bar",
        data: actualGoals,
        itemStyle: {
          color: "#246B45",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: 16,
      },
      {
        name: "Expected Goals (xG)",
        type: "bar",
        data: expectedGoals,
        itemStyle: {
          color: "#D9A441",
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: 16,
      },
    ],
  };

  return <EChartsWrapper option={option} height={height} />;
}
