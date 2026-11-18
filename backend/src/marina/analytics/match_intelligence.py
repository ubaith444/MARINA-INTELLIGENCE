"""Module 5: Match Intelligence, Opponent Comparison, and Half-by-Half Tactical Analytics."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.analytics.common import safe_divide
from marina.models.common import EventType, MatchPeriod, MatchStatus
from marina.models.match import Lineup, Match, MatchEvent
from marina.models.statistics import TeamMatchStatistic


class MatchIntelligenceEngine:
    """Generates detailed single-match comparative reports, half-by-half analysis, and momentum comparisons."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def generate_match_report(self, match_id: uuid.UUID) -> Dict[str, Any]:
        """Generates comprehensive tactical report for a single match fixture."""
        stmt = (
            select(Match)
            .where(Match.id == match_id)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
                selectinload(Match.events).selectinload(MatchEvent.primary_player),
                selectinload(Match.events).selectinload(MatchEvent.secondary_player),
                selectinload(Match.team_statistics),
                selectinload(Match.lineups).selectinload(Lineup.player),
            )
        )
        match: Optional[Match] = (await self.session.execute(stmt)).scalars().first()
        if not match:
            raise ValueError(f"Match {match_id} not found.")

        # Extract team stats for home and away
        home_stat = next((s for s in match.team_statistics if s.team_id == match.home_team_id), None)
        away_stat = next((s for s in match.team_statistics if s.team_id == match.away_team_id), None)

        def _get_team_metric_dict(s: Optional[TeamMatchStatistic]) -> Dict[str, Any]:
            if not s:
                return {}
            return {
                "possession_pct": s.possession_pct,
                "shots_total": s.shots_total,
                "shots_on_target": s.shots_on_target,
                "shots_off_target": s.shots_off_target,
                "blocked_shots": s.blocked_shots,
                "expected_goals": s.expected_goals,
                "shooting_accuracy_pct": safe_divide((s.shots_on_target or 0) * 100.0, s.shots_total),
                "passes_total": s.passes_total,
                "passes_completed": s.passes_completed,
                "pass_accuracy_pct": s.pass_accuracy_pct,
                "tackles_total": s.tackles_total,
                "tackles_won": s.tackles_won,
                "interceptions": s.interceptions,
                "clearances": s.clearances,
                "corners": s.corners,
                "fouls_committed": s.fouls_committed,
                "yellow_cards": s.yellow_cards,
                "red_cards": s.red_cards,
                "saves": s.saves,
            }

        # Half-by-half analysis
        first_half_events = [e for e in match.events if e.period == MatchPeriod.FIRST_HALF]
        second_half_events = [e for e in match.events if e.period == MatchPeriod.SECOND_HALF]

        first_half_goals_home = sum(1 for e in first_half_events if e.team_id == match.home_team_id and e.event_type in (EventType.GOAL, EventType.PENALTY_GOAL))
        first_half_goals_away = sum(1 for e in first_half_events if e.team_id == match.away_team_id and e.event_type in (EventType.GOAL, EventType.PENALTY_GOAL))

        second_half_goals_home = sum(1 for e in second_half_events if e.team_id == match.home_team_id and e.event_type in (EventType.GOAL, EventType.PENALTY_GOAL))
        second_half_goals_away = sum(1 for e in second_half_events if e.team_id == match.away_team_id and e.event_type in (EventType.GOAL, EventType.PENALTY_GOAL))

        # Event timeline
        timeline = []
        for e in match.events:
            p_name = e.primary_player.known_name or f"{e.primary_player.first_name} {e.primary_player.last_name}" if e.primary_player else None
            s_name = e.secondary_player.known_name or f"{e.secondary_player.first_name} {e.secondary_player.last_name}" if e.secondary_player else None
            team_name = match.home_team.name if e.team_id == match.home_team_id else (match.away_team.name if e.team_id == match.away_team_id else "Match")

            timeline.append({
                "minute": e.minute,
                "stoppage_minute": e.stoppage_minute,
                "period": e.period.value if hasattr(e.period, "value") else str(e.period),
                "event_type": e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type),
                "team_name": team_name,
                "primary_player": p_name,
                "secondary_player": s_name,
                "description": e.description,
            })

        return {
            "match_id": str(match.id),
            "match_number": match.match_number,
            "match_status": match.match_status.value if hasattr(match.match_status, "value") else str(match.match_status),
            "kickoff": match.scheduled_kickoff.isoformat(),
            "venue": match.venue.name if match.venue else "Unknown Venue",
            "attendance": match.attendance,
            "referee": match.referee,
            "home_team": {
                "id": str(match.home_team.id),
                "name": match.home_team.name,
                "short_name": match.home_team.short_name,
                "score": match.home_score,
                "statistics": _get_team_metric_dict(home_stat),
            },
            "away_team": {
                "id": str(match.away_team.id),
                "name": match.away_team.name,
                "short_name": match.away_team.short_name,
                "score": match.away_score,
                "statistics": _get_team_metric_dict(away_stat),
            },
            "half_by_half": {
                "first_half": {
                    "score": f"{first_half_goals_home}-{first_half_goals_away}",
                    "home_goals": first_half_goals_home,
                    "away_goals": first_half_goals_away,
                    "events_count": len(first_half_events),
                },
                "second_half": {
                    "score": f"{second_half_goals_home}-{second_half_goals_away}",
                    "home_goals": second_half_goals_home,
                    "away_goals": second_half_goals_away,
                    "events_count": len(second_half_events),
                },
            },
            "timeline": timeline,
        }

    async def calculate_head_to_head(
        self,
        team_a_id: uuid.UUID,
        team_b_id: uuid.UUID,
    ) -> Dict[str, Any]:
        """Calculates head-to-head historical record between two teams."""
        stmt = (
            select(Match)
            .where(
                or_(
                    (Match.home_team_id == team_a_id) & (Match.away_team_id == team_b_id),
                    (Match.home_team_id == team_b_id) & (Match.away_team_id == team_a_id),
                ),
                Match.match_status == MatchStatus.FINISHED,
            )
            .order_by(Match.scheduled_kickoff.desc())
        )
        matches: List[Match] = list((await self.session.execute(stmt)).scalars().all())

        total = len(matches)
        wins_a = 0
        wins_b = 0
        draws = 0
        goals_a = 0
        goals_b = 0

        for m in matches:
            a_is_home = m.home_team_id == team_a_id
            score_a = m.home_score if a_is_home else m.away_score
            score_b = m.away_score if a_is_home else m.home_score

            if score_a is not None and score_b is not None:
                goals_a += score_a
                goals_b += score_b
                if score_a > score_b:
                    wins_a += 1
                elif score_b > score_a:
                    wins_b += 1
                else:
                    draws += 1

        return {
            "team_a_id": str(team_a_id),
            "team_b_id": str(team_b_id),
            "matches_played": total,
            "team_a_wins": wins_a,
            "team_b_wins": wins_b,
            "draws": draws,
            "team_a_goals": goals_a,
            "team_b_goals": goals_b,
        }
