import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import LeadershipGroupSection from "../components/team/LeadershipGroupSection";

vi.mock("@/lib/api", () => ({
  fetchLeadershipGroup: vi.fn().mockResolvedValue({
    team_id: "f26268f6-f74f-4bee-a6cf-5f816765c031",
    team_name: "Chennaiyin FC",
    team_short_name: "CFC",
    season_id: "d2149ce9-8c6a-4160-87c5-ce87de69d856",
    season_name: "2026–27",
    role_title: "Leadership Group",
    total_members: 5,
    members: [
      {
        id: "1",
        player_id: "a378e4c6-f1f1-4304-9a7f-6ac754f2e014",
        player_name: "Nuno Reis",
        jersey_number: 4,
        position: "Defender",
        primary_position: "CB",
        nationality: "Portugal",
        is_indian: false,
        leadership_role: "Leadership Group",
        is_captain: false,
        is_vice_captain: false,
      },
      {
        id: "2",
        player_id: "77bee327-2929-4d41-9329-e2f2bd18c88e",
        player_name: "P. C. Laldinpuia",
        jersey_number: 3,
        position: "Defender",
        primary_position: "CB",
        nationality: "India",
        is_indian: true,
        leadership_role: "Leadership Group",
        is_captain: false,
        is_vice_captain: false,
      },
      {
        id: "3",
        player_id: "3a79ed6c-7620-44aa-8568-b1f2b3650062",
        player_name: "Nikola Stojanović",
        jersey_number: 8,
        position: "Midfielder",
        primary_position: "CM",
        nationality: "Serbia",
        is_indian: false,
        leadership_role: "Leadership Group",
        is_captain: false,
        is_vice_captain: false,
      },
      {
        id: "4",
        player_id: "ee362980-f66b-417d-8abb-c4004b703320",
        player_name: "Samik Mitra",
        jersey_number: 1,
        position: "Goalkeeper",
        primary_position: "GK",
        nationality: "India",
        is_indian: true,
        leadership_role: "Leadership Group",
        is_captain: false,
        is_vice_captain: false,
      },
      {
        id: "5",
        player_id: "f1f1efd2-6b7f-4f22-aba3-2bf79404a683",
        player_name: "Mohammad Nawaz",
        jersey_number: 13,
        position: "Goalkeeper",
        primary_position: "GK",
        nationality: "India",
        is_indian: true,
        leadership_role: "Leadership Group",
        is_captain: false,
        is_vice_captain: false,
      },
    ],
  }),
}));

describe("LeadershipGroupSection Component", () => {
  it("renders the 5 verified leadership group members", async () => {
    render(<LeadershipGroupSection />);

    // Check header
    expect(await screen.findByText(/Season Leadership Group • ISL 2026–27/i)).toBeInTheDocument();

    // Check all 5 player names
    expect(await screen.findByText("Nuno Reis")).toBeInTheDocument();
    expect(await screen.findByText("P. C. Laldinpuia")).toBeInTheDocument();
    expect(await screen.findByText("Nikola Stojanović")).toBeInTheDocument();
    expect(await screen.findByText("Samik Mitra")).toBeInTheDocument();
    expect(await screen.findByText("Mohammad Nawaz")).toBeInTheDocument();

    // Check positions
    expect(screen.getAllByText("Defender").length).toBe(2);
    expect(screen.getByText("Midfielder")).toBeInTheDocument();
    expect(screen.getAllByText("Goalkeeper").length).toBe(2);

    // Check that Leadership Group tags are displayed for all five
    const badges = screen.getAllByText("Leadership Group");
    expect(badges.length).toBe(5);
  });
});
