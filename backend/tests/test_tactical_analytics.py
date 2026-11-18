"""Automated Tests for Module 6: Tactical Analytics, Passing Networks, Shot Maps, and Spatial Intelligence."""

import pytest
from marina.analytics.tactical import TacticalAnalyticsEngine


@pytest.fixture
def tactical_engine():
    return TacticalAnalyticsEngine()


def test_calculate_distance_and_angle_penalty_spot(tactical_engine):
    """Verify distance and angle calculation from standard penalty spot (94.0, 34.0)."""
    dist, angle = tactical_engine.calculate_distance_and_angle(94.0, 34.0)

    # Penalty spot is exactly 11.0m from goal line center (105 - 94 = 11.0)
    assert dist == 11.0
    # Goal width = 7.32m (+/- 3.66m from center).
    # Angle theta = 2 * arctan(3.66 / 11) = 2 * 18.41 deg ≈ 36.8 deg
    assert 35.0 <= angle <= 38.0


def test_calculate_distance_and_angle_edge_cases(tactical_engine):
    """Verify distance and angle at goal line and corner flag."""
    # At goal line center: distance is 0, angle subtended between the two opposite posts is 180 degrees
    dist, angle = tactical_engine.calculate_distance_and_angle(105.0, 34.0)
    assert dist == 0.0
    assert angle == 180.0

    # At corner flag on the goal line (105.0, 0.0): collinear with goal line, so angle is 0.0
    dist_c, angle_c = tactical_engine.calculate_distance_and_angle(105.0, 0.0)
    assert dist_c == 34.0
    assert angle_c == 0.0

    # From wide pitch position off the goal line (100.0, 5.0): angle is acute
    dist_w, angle_w = tactical_engine.calculate_distance_and_angle(100.0, 5.0)
    assert 0.0 < angle_w < 15.0


def test_is_progressive_pass(tactical_engine):
    """Verify progressive pass classification under modern football analytics rules."""
    # 1. Originating in defensive 40% (x1 < 42.0m) -> always False
    assert tactical_engine.is_progressive_pass(x1=30.0, y1=34.0, x2=55.0, y2=34.0) is False

    # 2. Forward pass moving ball >= 10m closer to opponent goal (105, 34)
    # Origin at (50, 34): distance = 55m. Destination at (65, 34): distance = 40m. Delta = 15m >= 10m -> True
    assert tactical_engine.is_progressive_pass(x1=50.0, y1=34.0, x2=65.0, y2=34.0) is True

    # 3. Sideways pass in attacking half (< 10m progression) -> False
    # (70, 10) to (70, 50): distance is roughly unchanged -> False
    assert tactical_engine.is_progressive_pass(x1=70.0, y1=10.0, x2=70.0, y2=20.0) is False

    # 4. Pass into opponent penalty box (x >= 88.5, 13.84 <= y <= 54.16) -> True even if progression < 10m
    # (82, 34) into box (89, 34): delta = 7m (<10m), but penetrates penalty area -> True
    assert tactical_engine.is_progressive_pass(x1=82.0, y1=34.0, x2=89.0, y2=34.0) is True


def test_generate_shot_map(tactical_engine):
    """Verify spatial shot map generation, xG aggregation, and conversion metrics."""
    raw_shots = [
        {"shot_id": "s1", "minute": 14, "player_name": "Farukh Choudhary", "x": 92.0, "y": 30.0, "outcome": "GOAL", "expected_goals": 0.35},
        {"shot_id": "s2", "minute": 33, "player_name": "Wilmar Jordan Gil", "x": 98.0, "y": 34.0, "outcome": "GOAL", "expected_goals": 0.62},
        {"shot_id": "s3", "minute": 55, "player_name": "Lukas Brambilla", "x": 84.0, "y": 25.0, "outcome": "SAVED", "expected_goals": 0.07},
        {"shot_id": "s4", "minute": 78, "player_name": "Connor Shields", "x": 88.0, "y": 42.0, "outcome": "MISSED", "expected_goals": 0.12},
    ]

    res = tactical_engine.generate_shot_map(raw_shots)

    assert res["total_shots"] == 4
    assert res["goals"] == 2
    assert res["conversion_rate_pct"] == 50.0
    # Expected goals: 0.35 + 0.62 + 0.07 + 0.12 = 1.16
    assert res["expected_goals_total"] == 1.16
    assert len(res["shots"]) == 4

    shot1 = res["shots"][0]
    assert shot1["distance_meters"] > 0
    assert shot1["angle_degrees"] > 0
    assert shot1["outcome"] == "GOAL"
    assert shot1["expected_goals"] == 0.35


def test_generate_passing_network(tactical_engine):
    """Verify passing network node positions, connection weights, and network density."""
    player_positions = [
        {"player_id": "1", "player_name": "GK Mitra", "jersey_number": 1, "avg_x": 12.0, "avg_y": 34.0, "touches": 25},
        {"player_id": "6", "player_name": "CB Edwards", "jersey_number": 6, "avg_x": 32.0, "avg_y": 45.0, "touches": 55},
        {"player_id": "8", "player_name": "CM Jiteshwor", "jersey_number": 8, "avg_x": 50.0, "avg_y": 34.0, "touches": 70},
    ]
    pass_connections = [
        {"passer_id": "1", "passer_name": "GK Mitra", "recipient_id": "6", "recipient_name": "CB Edwards", "pass_count": 8},
        {"passer_id": "6", "passer_name": "CB Edwards", "recipient_id": "8", "recipient_name": "CM Jiteshwor", "pass_count": 12},
    ]

    res = tactical_engine.generate_passing_network(player_positions, pass_connections)

    assert res["nodes_count"] == 3
    assert res["edges_count"] == 2
    # Potential edges for 3 nodes = 3 * 2 / 2 = 3. Network density = 2 / 3 = 0.67
    assert res["network_density"] == 0.67
    assert len(res["nodes"]) == 3
    assert len(res["edges"]) == 2


def test_calculate_field_tilt(tactical_engine):
    """Verify field tilt calculation and territorial dominance categorization."""
    # Dominant attack: 65 passes vs 25 opponent passes = 65 / 90 = 72.2% -> HIGH
    high_tilt = tactical_engine.calculate_field_tilt(team_final_third_passes=65, opponent_final_third_passes=25)
    assert high_tilt["field_tilt_pct"] == 72.22
    assert high_tilt["territorial_dominance"] == "HIGH"

    # Balanced: 50 passes vs 50 passes = 50.0% -> BALANCED
    balanced_tilt = tactical_engine.calculate_field_tilt(team_final_third_passes=50, opponent_final_third_passes=50)
    assert balanced_tilt["field_tilt_pct"] == 50.0
    assert balanced_tilt["territorial_dominance"] == "BALANCED"

    # Defensive/Pinned back: 20 passes vs 60 passes = 25.0% -> DEFENSIVE
    def_tilt = tactical_engine.calculate_field_tilt(team_final_third_passes=20, opponent_final_third_passes=60)
    assert def_tilt["field_tilt_pct"] == 25.0
    assert def_tilt["territorial_dominance"] == "DEFENSIVE"

    # Zero passes handling (no division by zero)
    zero_tilt = tactical_engine.calculate_field_tilt(team_final_third_passes=0, opponent_final_third_passes=0)
    assert zero_tilt["field_tilt_pct"] is None
