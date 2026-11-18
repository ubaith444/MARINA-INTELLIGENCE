"""Module 4: Player Performance, Per-90 Standardizer, and Head-to-Head Comparison Engine."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.analytics.common import calculate_per_90, safe_divide
from marina.models.common import LineupRole, MatchStatus, PlayerPosition
from marina.models.match import Lineup, Match
from marina.models.player import Player, SquadRegistration
from marina.models.statistics import PlayerMatchStatistic


class PlayerIntelligenceEngine:
    """Computes player seasonal performance, per-90 metrics, position rankings, and head-to-head comparisons."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate_player_performance(
        self,
        player_id: uuid.UUID,
        season_id: Optional[uuid.UUID] = None,
        min_minutes_for_per90: int = 45,
    ) -> Dict[str, Any]:
        """Calculates comprehensive individual player performance and standardized per-90 rates."""
        player = (await self.session.execute(select(Player).where(Player.id == player_id))).scalars().first()
        if not player:
            raise ValueError(f"Player {player_id} not found.")

        # 1. Fetch lineups to calculate appearances, starts, bench
        lineup_stmt = select(Lineup).join(Match).where(
            Lineup.player_id == player_id,
            Match.match_status == MatchStatus.FINISHED,
        )
        if season_id:
            lineup_stmt = lineup_stmt.where(Match.season_id == season_id)

        lineups: List[Lineup] = list((await self.session.execute(lineup_stmt)).scalars().all())

        appearances = len(lineups)
        starts = sum(1 for l in lineups if l.lineup_role == LineupRole.STARTER)
        sub_appearances = sum(1 for l in lineups if l.is_substitute_in)

        # 2. Fetch PlayerMatchStatistics
        stat_stmt = select(PlayerMatchStatistic).join(Match).where(
            PlayerMatchStatistic.player_id == player_id,
            Match.match_status == MatchStatus.FINISHED,
        )
        if season_id:
            stat_stmt = stat_stmt.where(Match.season_id == season_id)

        stats: List[PlayerMatchStatistic] = list((await self.session.execute(stat_stmt)).scalars().all())

        total_minutes = sum(s.minutes_played for s in stats if s.minutes_played is not None)
        # If no statistics rows but lineups have minutes_played
        if total_minutes == 0 and lineups:
            total_minutes = sum(l.minutes_played for l in lineups if l.minutes_played is not None)

        # Aggregate raw metrics
        goals = sum(s.goals for s in stats if s.goals is not None)
        assists = sum(s.assists for s in stats if s.assists is not None)
        shots_total = sum(s.shots_total for s in stats if s.shots_total is not None)
        shots_on_target = sum(s.shots_on_target for s in stats if s.shots_on_target is not None)
        key_passes = sum(s.key_passes for s in stats if s.key_passes is not None)
        passes_total = sum(s.passes_total for s in stats if s.passes_total is not None)
        passes_completed = sum(s.passes_completed for s in stats if s.passes_completed is not None)
        tackles_total = sum(s.tackles_total for s in stats if s.tackles_total is not None)
        tackles_won = sum(s.tackles_won for s in stats if s.tackles_won is not None)
        interceptions = sum(s.interceptions for s in stats if s.interceptions is not None)
        clearances = sum(s.clearances for s in stats if s.clearances is not None)

        # Expected Goals & Assists (strictly None if not recorded)
        xg_vals = [s.expected_goals for s in stats if s.expected_goals is not None]
        total_xg: Optional[float] = round(sum(xg_vals), 2) if xg_vals else None

        xa_vals = [s.expected_assists for s in stats if s.expected_assists is not None]
        total_xa: Optional[float] = round(sum(xa_vals), 2) if xa_vals else None

        # Distance covered
        dist_vals = [s.distance_covered_km for s in stats if s.distance_covered_km is not None]
        total_dist_km: Optional[float] = round(sum(dist_vals), 2) if dist_vals else None

        # Percentages
        pass_accuracy_pct = safe_divide(passes_completed * 100.0, passes_total) if passes_total > 0 else None
        tackle_success_pct = safe_divide(tackles_won * 100.0, tackles_total) if tackles_total > 0 else None

        # Standardized Per-90 Metrics
        has_sufficient_minutes = total_minutes >= min_minutes_for_per90

        per_90_metrics = {
            "has_sufficient_minutes": has_sufficient_minutes,
            "min_minutes_threshold": min_minutes_for_per90,
            "goals_per_90": calculate_per_90(goals, total_minutes, min_minutes_for_per90),
            "assists_per_90": calculate_per_90(assists, total_minutes, min_minutes_for_per90),
            "goal_contributions_per_90": calculate_per_90(goals + assists, total_minutes, min_minutes_for_per90),
            "shots_per_90": calculate_per_90(shots_total, total_minutes, min_minutes_for_per90) if shots_total > 0 else None,
            "shots_on_target_per_90": calculate_per_90(shots_on_target, total_minutes, min_minutes_for_per90) if shots_on_target > 0 else None,
            "expected_goals_per_90": calculate_per_90(total_xg, total_minutes, min_minutes_for_per90) if total_xg is not None else None,
            "expected_assists_per_90": calculate_per_90(total_xa, total_minutes, min_minutes_for_per90) if total_xa is not None else None,
            "passes_completed_per_90": calculate_per_90(passes_completed, total_minutes, min_minutes_for_per90) if passes_completed > 0 else None,
            "tackles_per_90": calculate_per_90(tackles_total, total_minutes, min_minutes_for_per90) if tackles_total > 0 else None,
            "interceptions_per_90": calculate_per_90(interceptions, total_minutes, min_minutes_for_per90) if interceptions > 0 else None,
        }

        return {
            "player_id": str(player.id),
            "slug": player.slug,
            "name": player.known_name or f"{player.first_name} {player.last_name}",
            "primary_position": player.primary_position.value if player.primary_position else "UNKNOWN",
            "nationality": player.nationality,
            "appearances": appearances,
            "starts": starts,
            "substitute_appearances": sub_appearances,
            "minutes_played": total_minutes,
            "raw_totals": {
                "goals": goals,
                "assists": assists,
                "goal_contributions": goals + assists,
                "shots_total": shots_total if shots_total > 0 else None,
                "shots_on_target": shots_on_target if shots_on_target > 0 else None,
                "expected_goals": total_xg,
                "expected_assists": total_xa,
                "key_passes": key_passes if key_passes > 0 else None,
                "passes_total": passes_total if passes_total > 0 else None,
                "passes_completed": passes_completed if passes_completed > 0 else None,
                "pass_accuracy_pct": pass_accuracy_pct,
                "tackles_total": tackles_total if tackles_total > 0 else None,
                "tackles_won": tackles_won if tackles_won > 0 else None,
                "tackle_success_pct": tackle_success_pct,
                "interceptions": interceptions if interceptions > 0 else None,
                "clearances": clearances if clearances > 0 else None,
                "distance_covered_km": total_dist_km,
            },
            "per_90": per_90_metrics,
        }

    async def compare_players(
        self,
        player_a_id: uuid.UUID,
        player_b_id: uuid.UUID,
        season_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Performs head-to-head statistical comparison and normalized tactical radar dimensions."""
        profile_a = await self.calculate_player_performance(player_a_id, season_id)
        profile_b = await self.calculate_player_performance(player_b_id, season_id)

        # Radar Dimension Calculations (0-100 scale based on standard tactical benchmarks)
        # Dimensions: Scoring, Creation, Distribution, Defending, Activity
        def _get_radar_score(val: Optional[float], max_benchmark: float) -> float:
            if val is None:
                return 0.0
            score = (val / max_benchmark) * 100.0
            return round(min(100.0, max(0.0, score)), 1)

        p90_a = profile_a["per_90"]
        p90_b = profile_b["per_90"]

        radar_dimensions = [
            {
                "dimension": "Scoring Threat",
                "player_a_score": _get_radar_score(p90_a.get("goals_per_90") or 0.0, max_benchmark=0.8),
                "player_b_score": _get_radar_score(p90_b.get("goals_per_90") or 0.0, max_benchmark=0.8),
            },
            {
                "dimension": "Shot Volume",
                "player_a_score": _get_radar_score(p90_a.get("shots_per_90") or 0.0, max_benchmark=3.5),
                "player_b_score": _get_radar_score(p90_b.get("shots_per_90") or 0.0, max_benchmark=3.5),
            },
            {
                "dimension": "Playmaking / Assists",
                "player_a_score": _get_radar_score(p90_a.get("assists_per_90") or 0.0, max_benchmark=0.5),
                "player_b_score": _get_radar_score(p90_b.get("assists_per_90") or 0.0, max_benchmark=0.5),
            },
            {
                "dimension": "Passing Output",
                "player_a_score": _get_radar_score(p90_a.get("passes_completed_per_90") or 0.0, max_benchmark=55.0),
                "player_b_score": _get_radar_score(p90_b.get("passes_completed_per_90") or 0.0, max_benchmark=55.0),
            },
            {
                "dimension": "Defensive Ball Winning",
                "player_a_score": _get_radar_score((p90_a.get("tackles_per_90") or 0.0) + (p90_a.get("interceptions_per_90") or 0.0), max_benchmark=4.5),
                "player_b_score": _get_radar_score((p90_b.get("tackles_per_90") or 0.0) + (p90_b.get("interceptions_per_90") or 0.0), max_benchmark=4.5),
            },
        ]

        return {
            "player_a": profile_a,
            "player_b": profile_b,
            "radar_comparison": radar_dimensions,
        }
