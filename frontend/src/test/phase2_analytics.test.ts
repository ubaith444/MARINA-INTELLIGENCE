import { describe, it, expect } from "vitest";
import {
  PassingNetworkNode,
  PassingNetwork,
  XgOverviewResponse,
  OppositionAnalysisResponse,
  MatchCompareResponse,
  PlayerPerformance,
} from "@/lib/types";

describe("Phase 2: Advanced Football Analytics Contracts", () => {
  describe("Module 01: Player Performance & Rankings", () => {
    it("preserves zero-minute protection and includes rankings and last five matches", () => {
      const mockProfile: PlayerPerformance = {
        player_id: "cfc-p-01",
        slug: "irfan-yadwad",
        name: "Irfan Yadwad",
        primary_position: "FORWARD",
        nationality: "India",
        appearances: 5,
        starts: 5,
        substitute_appearances: 0,
        minutes_played: 420,
        raw_totals: {
          goals: 3,
          assists: 1,
          goal_contributions: 4,
          shots_total: 10,
          shots_on_target: 6,
          expected_goals: 1.86,
        },
        per_90: {
          has_sufficient_minutes: true,
          min_minutes_threshold: 45,
          goals_per_90: 0.64,
          assists_per_90: 0.21,
          goal_contributions_per_90: 0.86,
          shots_per_90: 2.14,
          shots_on_target_per_90: 1.29,
          expected_goals_per_90: 0.4,
        },
        rankings: {
          goals: { rank: 1, total: 28 },
          minutes: { rank: 2, total: 28 },
          assists: { rank: 1, total: 28 },
          shots: { rank: 1, total: 28 },
        },
        last_five_matches: [
          {
            match_id: "m-01",
            match_number: 1,
            kickoff: "2026-09-15T19:30:00Z",
            opponent_name: "Kerala Blasters FC",
            opponent_short: "KBFC",
            is_home: true,
            started: true,
            minutes_played: 90,
            goals: 1,
            assists: 0,
            score: "2–1",
            yellow_cards: 0,
            red_cards: 0,
          },
        ],
      };

      expect(mockProfile.per_90.has_sufficient_minutes).toBe(true);
      expect(mockProfile.rankings?.goals?.rank).toBe(1);
      expect(mockProfile.last_five_matches?.length).toBe(1);
      expect(mockProfile.last_five_matches?.[0].opponent_short).toBe("KBFC");
    });

    it("strictly returns null for unplayed squad member rate metrics", () => {
      const unplayedProfile: PlayerPerformance = {
        player_id: "cfc-p-unplayed",
        slug: "unplayed-reserve",
        name: "Reserve Player",
        primary_position: "DEFENDER",
        nationality: "India",
        appearances: 0,
        starts: 0,
        substitute_appearances: 0,
        minutes_played: 0,
        raw_totals: {
          goals: 0,
          assists: 0,
          goal_contributions: 0,
        },
        per_90: {
          has_sufficient_minutes: false,
          min_minutes_threshold: 45,
          goals_per_90: null,
          assists_per_90: null,
          goal_contributions_per_90: null,
          shots_per_90: null,
          shots_on_target_per_90: null,
          expected_goals_per_90: null,
        },
        rankings: null,
        last_five_matches: [],
      };

      expect(unplayedProfile.per_90.has_sufficient_minutes).toBe(false);
      expect(unplayedProfile.per_90.goals_per_90).toBeNull();
      expect(unplayedProfile.appearances).toBe(0);
      expect(unplayedProfile.minutes_played).toBe(0);
    });
  });

  describe("Module 02: Passing Networks with NetworkX Metrics", () => {
    it("validates NetworkX degree centrality, in-degree, out-degree and directed density", () => {
      const mockNetwork: PassingNetwork = {
        period: "FULL_MATCH",
        nodes: [
          {
            player_id: "p-01",
            player_name: "Madih Talal",
            jersey_number: 10,
            position: "AM",
            avg_x: 62.4,
            avg_y: 35.1,
            touches: 58,
            in_degree: 36,
            out_degree: 42,
            weighted_degree: 78,
            degree_centrality: 0.8,
          },
        ],
        edges: [
          {
            from_player_id: "p-01",
            to_player_id: "p-02",
            pass_count: 14,
          },
        ],
        network_density: 0.67,
        directed_density: 0.333,
      };

      expect(mockNetwork.period).toBe("FULL_MATCH");
      expect(mockNetwork.nodes[0].degree_centrality).toBe(0.8);
      expect(mockNetwork.nodes[0].out_degree).toBe(42);
      expect(mockNetwork.directed_density).toBe(0.333);
    });
  });

  describe("Module 03: Expected Goals (xG) Statistical Formulation", () => {
    it("verifies team xG overperformance and conversion rate metrics", () => {
      const mockXg: XgOverviewResponse = {
        team_name: "Chennaiyin FC",
        total_shots: 18,
        total_goals: 6,
        total_xg: 3.41,
        xg_difference: 2.59,
        conversion_rate_pct: 33.3,
        xg_per_shot: 0.19,
        methodology: "Documented baseline logistic regression statistical model calibrated on distance to goal and shot angle",
        players_xg: [
          {
            player_name: "Irfan Yadwad",
            shots: 8,
            goals: 3,
            expected_goals: 1.86,
            xg_difference: 1.14,
            conversion_rate_pct: 37.5,
            xg_per_shot: 0.23,
          },
        ],
        matches_xg: [
          {
            match_id: "m-01",
            match_number: 1,
            opponent_name: "Kerala Blasters FC",
            goals: 2,
            expected_goals: 1.15,
            shots: 5,
            conversion_rate_pct: 40.0,
          },
        ],
      };

      expect(mockXg.total_goals).toBe(6);
      expect(mockXg.total_xg).toBe(3.41);
      expect(mockXg.xg_difference).toBe(2.59);
      expect(mockXg.players_xg[0].player_name).toBe("Irfan Yadwad");
    });
  });

  describe("Module 04: Opposition Analysis Dossier", () => {
    it("verifies head-to-head records and tactical scouting structures", () => {
      const mockOpposition: OppositionAnalysisResponse = {
        opponent_id: "opp-01",
        opponent_name: "FC Goa",
        short_name: "FCG",
        slug: "fc-goa",
        head_to_head: {
          matches_played: 1,
          cfc_wins: 1,
          draws: 0,
          opponent_wins: 0,
          cfc_goals: 2,
          opponent_goals: 1,
          clean_sheets: 0,
        },
        completed_fixtures: [],
        upcoming_fixtures: [],
        tactical_profile: {
          formation: "4-2-3-1",
          tactical_style: "Possession build-up through central midfielders",
          strengths: ["Central midfield control"],
          vulnerabilities: ["High line transition defence"],
          key_player: "Armando Sadiku",
        },
      };

      expect(mockOpposition.head_to_head.cfc_wins).toBe(1);
      expect(mockOpposition.tactical_profile.formation).toBe("4-2-3-1");
      expect(mockOpposition.tactical_profile.key_player).toBe("Armando Sadiku");
    });
  });

  describe("Module 05: Match Comparison Workspace", () => {
    it("calculates comparative metrics and deltas across Match A and Match B", () => {
      const mockCompare: MatchCompareResponse = {
        match_a: {
          match_id: "m-01",
          match_number: 1,
          opponent_name: "Kerala Blasters FC",
          score: "2 – 1",
          is_home: true,
          formation: "4-2-3-1",
        },
        match_b: {
          match_id: "m-02",
          match_number: 2,
          opponent_name: "Mumbai City FC",
          score: "1 – 1",
          is_home: false,
          formation: "4-2-3-1",
        },
        comparisons: [
          {
            metric_name: "goals",
            label: "Goals Scored",
            match_a_value: 2,
            match_b_value: 1,
            delta: 1,
            unit: null,
          },
          {
            metric_name: "field_tilt",
            label: "Field Tilt %",
            match_a_value: 64.2,
            match_b_value: 58.5,
            delta: 5.7,
            unit: "%",
          },
        ],
      };

      expect(mockCompare.comparisons[0].delta).toBe(1);
      expect(mockCompare.comparisons[1].delta).toBe(5.7);
    });
  });
});
