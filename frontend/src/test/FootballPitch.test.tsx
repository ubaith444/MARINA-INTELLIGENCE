import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import FootballPitch from "@/components/pitch/FootballPitch";

describe("FootballPitch Component", () => {
  it("renders with default formation mode and pitch markings", () => {
    const { container } = render(<FootballPitch />);
    // Check mode buttons
    expect(screen.getByText("FORMATION")).toBeInTheDocument();
    expect(screen.getByText("PASSING NETWORK")).toBeInTheDocument();
    expect(screen.getByText("SHOT MAP")).toBeInTheDocument();
    expect(screen.getByText("DEFENSIVE ACTIONS")).toBeInTheDocument();
    expect(screen.getByText("HEATMAP")).toBeInTheDocument();

    // Check SVG pitch exists
    const svg = container.querySelector("svg");
    expect(svg).toBeInTheDocument();
    expect(svg?.getAttribute("viewBox")).toBe("0 0 1050 680");
  });

  it("toggles between Full Pitch and Attacking Half view", () => {
    const { container } = render(<FootballPitch />);
    const halfButton = screen.getByText("Attacking Half");
    fireEvent.click(halfButton);

    const svg = container.querySelector("svg");
    expect(svg?.getAttribute("viewBox")).toBe("525 0 525 680");

    const fullButton = screen.getByText("Full Pitch");
    fireEvent.click(fullButton);
    expect(svg?.getAttribute("viewBox")).toBe("0 0 1050 680");
  });

  it("switches to Shot Map mode", () => {
    render(<FootballPitch />);
    const shotMapBtn = screen.getByText("SHOT MAP");
    fireEvent.click(shotMapBtn);

    // Verify Shot Map legend appears
    expect(screen.getByText("Goal")).toBeInTheDocument();
    expect(screen.getByText("Saved / Missed")).toBeInTheDocument();
  });

  it("triggers onPlayerClick when a player marker is clicked", () => {
    const onPlayerClick = vi.fn();
    const customPlayers = [
      { id: "p1", name: "Wilmar Jordan Gil", jersey_number: 9, position: "STRIKER", x: 88, y: 50, role: "STARTER" as const },
    ];
    render(<FootballPitch players={customPlayers} onPlayerClick={onPlayerClick} />);

    // Click on the player name text
    const playerText = screen.getByText("Gil");
    fireEvent.click(playerText);

    expect(onPlayerClick).toHaveBeenCalledWith(
      expect.objectContaining({ name: "Wilmar Jordan Gil", jersey_number: 9 })
    );

    // Selected player flyout card appears
    expect(screen.getByText("Wilmar Jordan Gil")).toBeInTheDocument();
  });
});
