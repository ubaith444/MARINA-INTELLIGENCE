"""Module 6: Tactical Analytics, Passing Networks, Shot Maps, and Spatial Intelligence."""

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from mplsoccer import Pitch

from marina.analytics.common import safe_divide


class TacticalAnalyticsEngine:
    """Calculates spatial passing networks, shot maps, progressive passes, and field tilt."""

    PITCH_LENGTH = 105.0
    PITCH_WIDTH = 68.0

    def __init__(self, pitch_type: str = "custom") -> None:
        self.pitch_type = pitch_type
        self.pitch = Pitch(pitch_type="custom", pitch_length=self.PITCH_LENGTH, pitch_width=self.PITCH_WIDTH)

    def calculate_distance_and_angle(self, x: float, y: float) -> Tuple[float, float]:
        """Calculates distance (meters) to goal center (105, 34) and shooting angle (degrees)."""
        goal_x = self.PITCH_LENGTH
        goal_y = self.PITCH_WIDTH / 2.0  # 34m center

        dx = goal_x - x
        dy = goal_y - y
        distance = math.sqrt(dx * dx + dy * dy)

        # Angle subtended by 7.32m goalposts (at y = 30.34 and y = 37.66)
        post1_y = goal_y - 3.66
        post2_y = goal_y + 3.66

        v1 = (dx, post1_y - y)
        v2 = (dx, post2_y - y)

        dot = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)

        if mag1 * mag2 == 0:
            angle_deg = 0.0
        else:
            cos_theta = max(-1.0, min(1.0, dot / (mag1 * mag2)))
            angle_deg = math.degrees(math.acos(cos_theta))

        return round(distance, 2), round(angle_deg, 2)

    def is_progressive_pass(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        """Determines if a pass is progressive according to Wyscout / Opta standards:
        - Originates at least outside defensive 40% of pitch.
        - Moves ball at least 10m closer to opponent goal (or into penalty box: x >= 88.5, 13.84 <= y <= 54.16).
        """
        # Exclude passes in own defensive 40%
        if x1 < self.PITCH_LENGTH * 0.4:
            return False

        goal_x = self.PITCH_LENGTH
        goal_y = self.PITCH_WIDTH / 2.0

        dist1 = math.sqrt((goal_x - x1)**2 + (goal_y - y1)**2)
        dist2 = math.sqrt((goal_x - x2)**2 + (goal_y - y2)**2)

        # Penalty box check
        is_into_box = (x2 >= 88.5 and 13.84 <= y2 <= 54.16) and (x1 < 88.5 or y1 < 13.84 or y1 > 54.16)

        return (dist1 - dist2 >= 10.0) or is_into_box

    def generate_shot_map(self, raw_shots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Processes raw shot events into spatial shot-map with distances, angles, and outcomes."""
        processed_shots = []
        total_shots = len(raw_shots)
        goals = 0
        total_xg = 0.0
        has_xg = False

        for s in raw_shots:
            x = float(s.get("x", 85.0))
            y = float(s.get("y", 34.0))
            dist, angle = self.calculate_distance_and_angle(x, y)

            outcome = s.get("outcome", "MISSED").upper()
            if outcome == "GOAL":
                goals += 1

            xg = s.get("expected_goals") or s.get("xg")
            if xg is not None:
                has_xg = True
                total_xg += float(xg)

            processed_shots.append({
                "shot_id": s.get("shot_id", str(len(processed_shots) + 1)),
                "minute": s.get("minute", 0),
                "player_name": s.get("player_name", "Player"),
                "team_name": s.get("team_name", "Team"),
                "x": x,
                "y": y,
                "distance_meters": dist,
                "angle_degrees": angle,
                "outcome": outcome,
                "expected_goals": round(float(xg), 2) if xg is not None else None,
                "body_part": s.get("body_part", "RIGHT_FOOT"),
            })

        return {
            "total_shots": total_shots,
            "goals": goals,
            "conversion_rate_pct": safe_divide(goals * 100.0, total_shots),
            "expected_goals_total": round(total_xg, 2) if has_xg else None,
            "pitch_dimensions": {"length": self.PITCH_LENGTH, "width": self.PITCH_WIDTH},
            "shots": processed_shots,
        }

    def generate_passing_network(
        self,
        player_positions: List[Dict[str, Any]],
        pass_connections: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Constructs a passing network graph with average player nodes and weighted edges."""
        nodes = []
        for p in player_positions:
            nodes.append({
                "player_id": p.get("player_id"),
                "player_name": p.get("player_name"),
                "jersey_number": p.get("jersey_number"),
                "avg_x": round(float(p.get("avg_x", 50.0)), 1),
                "avg_y": round(float(p.get("avg_y", 34.0)), 1),
                "touches": p.get("touches", 1),
            })

        edges = []
        for c in pass_connections:
            edges.append({
                "passer_id": c.get("passer_id"),
                "passer_name": c.get("passer_name"),
                "recipient_id": c.get("recipient_id"),
                "recipient_name": c.get("recipient_name"),
                "pass_count": int(c.get("pass_count", 1)),
            })

        # Calculate network density: edges / potential edges
        n = len(nodes)
        potential_edges = n * (n - 1) / 2 if n > 1 else 1
        density = safe_divide(len(edges), potential_edges)

        return {
            "nodes_count": len(nodes),
            "edges_count": len(edges),
            "network_density": density,
            "nodes": nodes,
            "edges": edges,
        }

    def calculate_field_tilt(
        self,
        team_final_third_passes: int,
        opponent_final_third_passes: int,
    ) -> Dict[str, Any]:
        """Calculates Field Tilt: Team's share of final third passes (possession territory dominance)."""
        total = team_final_third_passes + opponent_final_third_passes
        field_tilt_pct = safe_divide(team_final_third_passes * 100.0, total)
        return {
            "team_final_third_passes": team_final_third_passes,
            "opponent_final_third_passes": opponent_final_third_passes,
            "field_tilt_pct": field_tilt_pct,
            "territorial_dominance": "HIGH" if (field_tilt_pct or 0) >= 60.0 else ("BALANCED" if (field_tilt_pct or 0) >= 45.0 else "DEFENSIVE"),
        }
