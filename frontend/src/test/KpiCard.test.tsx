import React from "react";
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import KpiCard from "@/components/ui/KpiCard";

describe("KpiCard Component", () => {
  it("renders label and formatted value", () => {
    render(<KpiCard label="Points" value={7} subtext="PPM: 2.33" />);
    expect(screen.getByText("Points")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("PPM: 2.33")).toBeInTheDocument();
  });

  it("handles null and undefined values by rendering em-dash without crash", () => {
    render(<KpiCard label="Expected Goals" value={null} subtext="Missing" />);
    expect(screen.getByText("Expected Goals")).toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("renders trend indicators properly", () => {
    render(
      <KpiCard
        label="Goals"
        value={8}
        trend="up"
        trendValue="+2.1"
      />
    );
    expect(screen.getByText("+2.1")).toBeInTheDocument();
  });
});
