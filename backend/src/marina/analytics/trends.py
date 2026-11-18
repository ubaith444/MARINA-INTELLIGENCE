"""Module 5: Performance Trends & Chronological Trajectory Engine."""

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.analytics.common import DataCoverageMetrics, safe_divide
from marina.models.common import MatchStatus
from marina.models.match import Match
from marina.models.team import Team


class PerformanceTrendsEngine:
    """Calculates chronological match progressions, rolling trends, monthly outputs, and points trajectory."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate_performance_trends(
        self,
        team_id: uuid.UUID,
        season_id: Optional[uuid.UUID] = None,
        rolling_window: int = 3,
    ) -> Dict[str, Any]:
        """Calculates match-by-match results, last 5 fixtures, monthly goal distributions,
        cumulative points progression, and rolling form averages.
        """
        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        # Completed matches in chronological order
        stmt = (
            select(Match)
            .where(
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
                Match.match_status == MatchStatus.FINISHED,
            )
            .options(selectinload(Match.home_team), selectinload(Match.away_team))
            .order_by(Match.scheduled_kickoff.asc())
        )
        if season_id:
            stmt = stmt.where(Match.season_id == season_id)

        matches: List[Match] = list((await self.session.execute(stmt)).scalars().all())
        total_played = len(matches)

        match_results: List[Dict[str, Any]] = []
        monthly_gf: Dict[str, int] = defaultdict(int)
        monthly_ga: Dict[str, int] = defaultdict(int)
        points_progression: List[Dict[str, Any]] = []

        cumulative_pts = 0

        for m in matches:
            is_home = m.home_team_id == team_id
            t_score = m.home_score if is_home else m.away_score
            o_score = m.away_score if is_home else m.home_score
            opponent = m.away_team if is_home else m.home_team

            if t_score is None or o_score is None:
                continue

            if t_score > o_score:
                outcome = "W"
                pts = 3
            elif t_score == o_score:
                outcome = "D"
                pts = 1
            else:
                outcome = "L"
                pts = 0

            cumulative_pts += pts

            # Month key (YYYY-MM)
            month_key = m.scheduled_kickoff.strftime("%Y-%m")
            monthly_gf[month_key] += t_score
            monthly_ga[month_key] += o_score

            match_data = {
                "match_id": str(m.id),
                "match_number": m.match_number,
                "date": m.scheduled_kickoff.isoformat(),
                "opponent_name": opponent.name if opponent else "Opponent",
                "opponent_short": opponent.short_name if opponent else "OPP",
                "is_home": is_home,
                "score": f"{t_score}-{o_score}",
                "outcome": outcome,
                "points": pts,
                "goals_for": t_score,
                "goals_against": o_score,
            }
            match_results.append(match_data)

            points_progression.append({
                "match_number": m.match_number,
                "date": m.scheduled_kickoff.isoformat(),
                "opponent": opponent.short_name if opponent and opponent.short_name else (opponent.name if opponent else "OPP"),
                "points_earned": pts,
                "cumulative_points": cumulative_pts,
            })

        # Last 5 matches
        last_five = match_results[-5:] if total_played >= 5 else match_results

        # Rolling performance trends
        rolling_trends: List[Dict[str, Any]] = []
        window_size = max(1, rolling_window)
        for i, m_res in enumerate(match_results):
            window_slice = match_results[max(0, i - window_size + 1) : i + 1]
            w_len = len(window_slice)
            w_gf = sum(w["goals_for"] for w in window_slice)
            w_ga = sum(w["goals_against"] for w in window_slice)
            w_pts = sum(w["points"] for w in window_slice)

            rolling_trends.append({
                "match_number": m_res["match_number"],
                "match_id": m_res["match_id"],
                "date": m_res["date"],
                "rolling_goals_for_avg": safe_divide(w_gf, w_len),
                "rolling_goals_against_avg": safe_divide(w_ga, w_len),
                "rolling_points_per_match": safe_divide(w_pts, w_len),
            })

        coverage = DataCoverageMetrics(
            sample_matches_count=total_played,
            minutes_tracked=total_played * 90,
            data_source_codes=["ISL_OFFICIAL"],
            has_event_level_data=total_played > 0,
            has_tracking_gps_data=False,
            coverage_notes=f"Chronological trajectory computed over {total_played} official completed fixtures with a {window_size}-match rolling window.",
        )

        return {
            "team_id": str(team.id),
            "team_name": team.name,
            "season_id": str(season_id) if season_id else None,
            "matches_analyzed": total_played,
            "last_five_matches": last_five,
            "match_by_match_results": match_results,
            "monthly_goals_scored": dict(sorted(monthly_gf.items())),
            "monthly_goals_conceded": dict(sorted(monthly_ga.items())),
            "points_progression": points_progression,
            "rolling_trends": rolling_trends,
            "data_coverage": coverage.to_dict(),
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
