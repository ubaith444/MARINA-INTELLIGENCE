"""Module 4: Passing & Possession Analytics Engine."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.analytics.common import DataCoverageMetrics, safe_divide
from marina.models.common import MatchStatus
from marina.models.match import Match
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team


class PassingAnalyticsEngine:
    """Calculates team passing metrics, distribution volume, passing accuracy %, and match-by-match passing performance."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate_team_passing_metrics(
        self,
        team_id: uuid.UUID,
        season_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Calculates total passes, completed passes, failed passes, accuracy %, average possession, and per-match breakdowns."""
        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        # Query completed matches for the team
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
        match_ids = [m.id for m in matches]

        # Query team match statistics for these matches
        stats_by_match: Dict[uuid.UUID, TeamMatchStatistic] = {}
        if match_ids:
            stat_stmt = select(TeamMatchStatistic).where(
                TeamMatchStatistic.team_id == team_id,
                TeamMatchStatistic.match_id.in_(match_ids),
            )
            stats_list = list((await self.session.execute(stat_stmt)).scalars().all())
            for s in stats_list:
                stats_by_match[s.match_id] = s

        matches_analyzed = len(matches)

        # Aggregate metrics
        passes_total_sum = 0
        passes_completed_sum = 0
        has_passes_data = False

        possession_values: List[float] = []
        passing_by_match: List[Dict[str, Any]] = []

        for m in matches:
            is_home = m.home_team_id == team_id
            opponent = m.away_team if is_home else m.home_team
            s = stats_by_match.get(m.id)

            p_total = s.passes_total if s else None
            p_comp = s.passes_completed if s else None
            p_acc = s.pass_accuracy_pct if s else None
            poss = s.possession_pct if s else None

            # Calculate failed passes if both total and completed exist
            failed = None
            if p_total is not None and p_comp is not None:
                failed = max(0, p_total - p_comp)

            if p_total is not None:
                passes_total_sum += p_total
                has_passes_data = True
            if p_comp is not None:
                passes_completed_sum += p_comp

            if poss is not None:
                possession_values.append(poss)

            calc_acc = p_acc if p_acc is not None else (safe_divide(p_comp * 100.0, p_total) if (p_total and p_comp is not None) else None)

            passing_by_match.append({
                "match_id": str(m.id),
                "match_number": m.match_number,
                "opponent_name": opponent.name if opponent else "Opponent",
                "opponent_short": opponent.short_name if opponent else "OPP",
                "is_home": is_home,
                "passes_total": p_total,
                "passes_completed": p_comp,
                "failed_passes": failed,
                "pass_accuracy_pct": calc_acc,
                "possession_pct": poss,
            })

        total_passes = passes_total_sum if has_passes_data else None
        successful_passes = passes_completed_sum if has_passes_data else None
        failed_passes = (total_passes - successful_passes) if (total_passes is not None and successful_passes is not None) else None
        passing_accuracy_pct = safe_divide(successful_passes * 100.0, total_passes) if (total_passes and successful_passes is not None) else None
        avg_possession = safe_divide(sum(possession_values), len(possession_values)) if possession_values else None

        coverage = DataCoverageMetrics(
            sample_matches_count=matches_analyzed,
            minutes_tracked=matches_analyzed * 90,
            data_source_codes=["ISL_OFFICIAL"],
            has_event_level_data=has_passes_data,
            has_tracking_gps_data=False,
            coverage_notes="Aggregated from match-level TeamMatchStatistic feeds. Distinguishes match-level aggregates from granular event telemetry.",
        )

        return {
            "team_id": str(team.id),
            "team_name": team.name,
            "season_id": str(season_id) if season_id else None,
            "matches_analyzed": matches_analyzed,
            "total_passes": total_passes,
            "successful_passes": successful_passes,
            "failed_passes": failed_passes,
            "passing_accuracy_pct": passing_accuracy_pct,
            "average_possession_pct": avg_possession,
            "passing_by_match": passing_by_match,
            "data_coverage": coverage.to_dict(),
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
