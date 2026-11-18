"use client";

import React, { useEffect, useRef } from "react";
import * as echarts from "echarts";

interface EChartsWrapperProps {
  option: echarts.EChartsOption;
  style?: React.CSSProperties;
  className?: string;
  loading?: boolean;
}

export default function EChartsWrapper({
  option,
  style,
  className,
  loading = false,
}: EChartsWrapperProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current, "dark", {
        renderer: "svg",
      });
    }

    if (loading) {
      chartInstance.current.showLoading({
        text: "Computing...",
        color: "#3b82f6",
        textColor: "#94a3b8",
        maskColor: "rgba(15, 23, 42, 0.6)",
      });
    } else {
      chartInstance.current.hideLoading();
      chartInstance.current.setOption(
        {
          backgroundColor: "transparent",
          ...option,
        },
        true
      );
    }

    const handleResize = () => {
      chartInstance.current?.resize();
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [option, loading]);

  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, []);

  return (
    <div
      ref={chartRef}
      style={{ width: "100%", height: "300px", ...style }}
      className={className}
    />
  );
}
