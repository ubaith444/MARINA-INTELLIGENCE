"""Module 3: Defensive Resilience & Disciplinary Analytics Engine."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.analytics.common import DataCoverageMetrics, safe_divide
from marina.models.common import EventType, MatchStatus
from marina.models.match import Match, MatchEvent
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team


class DefensiveAnalyticsEngine:
    """Calculates team defensive metrics, clean sheets, duel efficiency, and disciplinary profiles."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate_team_defensive_metrics(
        self,
        team_id: uuid.UUID,
        season_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Calculates defensive actions, goals conceded, clean sheets, and card counts."""
        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        # 1. Fetch finished matches to compute goals conceded and clean sheets
        match_stmt = select(Match).where(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
            Match.match_status == MatchStatus.FINISHED,
        )
        if season_id:
            match_stmt = match_stmt.where(Match.season_id == season_id)

        matches: List[Match] = list((await self.session.execute(match_stmt)).scalars().all())
        matches_count = len(matches)

        goals_conceded = 0
        clean_sheets = 0

        for m in matches:
            is_home = m.home_team_id == team_id
            opp_score = m.away_score if is_home else m.home_score
            if opp_score is not None:
                goals_conceded += opp_score
                if opp_score == 0:
                    clean_sheets += 1

        # 2. Fetch team match defensive statistics
        stat_stmt = select(TeamMatchStatistic).join(Match).where(
            TeamMatchStatistic.team_id == team_id,
            Match.match_status == MatchStatus.FINISHED,
        )
        if season_id:
            stat_stmt = stat_stmt.where(Match.season_id == season_id)

        stats: List[TeamMatchStatistic] = list((await self.session.execute(stat_stmt)).scalars().all())

        tackles_total = sum(s.tackles_total for s in stats if s.tackles_total is not None)
        tackles_won = sum(s.tackles_won for s in stats if s.tackles_won is not None)
        interceptions = sum(s.interceptions for s in stats if s.interceptions is not None)
        clearances = sum(s.clearances for s in stats if s.clearances is not None)
        saves = sum(s.saves for s in stats if s.saves is not None)
        blocked_shots = sum(s.blocked_shots for s in stats if s.blocked_shots is not None)
        fouls_committed = sum(s.fouls_committed for s in stats if s.fouls_committed is not None)
        yellow_cards = sum(s.yellow_cards for s in stats if s.yellow_cards is not None)
        red_cards = sum(s.red_cards for s in stats if s.red_cards is not None)

        # Expected Goals Conceded (xGA)
        xga_values = [s.expected_goals_conceded for s in stats if s.expected_goals_conceded is not None]
        total_xga: Optional[float] = round(sum(xga_values), 2) if xga_values else None
        xga_per_match = safe_divide(total_xga, len(xga_values)) if total_xga is not None else None

        # Derived percentages
        clean_sheet_pct = safe_divide(clean_sheets * 100.0, matches_count)
        goals_conceded_per_match = safe_divide(goals_conceded, matches_count)
        tackle_success_pct = safe_divide(tackles_won * 100.0, tackles_total)

        # Disciplinary Index: 1 point per yellow, 3 points per red
        discipline_index = yellow_cards + (3 * red_cards)

        total_defensive_actions = tackles_total + interceptions + clearances + blocked_shots
        defensive_actions_per_match = safe_divide(total_defensive_actions, matches_count)

        coverage = DataCoverageMetrics(
            sample_matches_count=matches_count,
            minutes_tracked=matches_count * 90,
            data_source_codes=["ISL_OFFICIAL"],
            has_event_level_data=True,
            has_tracking_gps_data=False,
            coverage_notes="Expected goals conceded aggregated only when tracked by official provider.",
        )

        return {
            "team_id": str(team.id),
            "team_name": team.name,
            "matches_analyzed": matches_count,
            "goals_conceded": goals_conceded,
            "goals_conceded_per_match": goals_conceded_per_match,
            "clean_sheets": clean_sheets,
            "clean_sheet_percentage": clean_sheet_pct,
            "expected_goals_conceded": total_xga,
            "expected_goals_conceded_per_match": xga_per_match,
            "tackles_total": tackles_total if tackles_total > 0 else None,
            "tackles_won": tackles_won if tackles_won > 0 else None,
            "tackle_success_pct": tackle_success_pct,
            "interceptions": interceptions if interceptions > 0 else None,
            "clearances": clearances if clearances > 0 else None,
            "saves": saves if saves > 0 else None,
            "blocked_shots": blocked_shots if blocked_shots > 0 else None,
            "total_defensive_actions": total_defensive_actions if total_defensive_actions > 0 else None,
            "defensive_actions_per_match": defensive_actions_per_match,
            "fouls_committed": fouls_committed if fouls_committed > 0 else None,
            "fouls_per_match": safe_divide(fouls_committed, matches_count),
            "yellow_cards": yellow_cards,
            "red_cards": red_cards,
            "discipline_index": discipline_index,
            "data_coverage": coverage.to_dict(),
        }
