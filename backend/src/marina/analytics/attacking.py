"""Module 2: Attacking Performance & Shot Quality Analytics Engine."""

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.analytics.common import DataCoverageMetrics, safe_divide
from marina.models.common import EventType, MatchPeriod, MatchStatus
from marina.models.match import Match, MatchEvent
from marina.models.player import Player
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team


class AttackingAnalyticsEngine:
    """Calculates team attacking metrics, shot conversion, shot efficiency, and goalscorer distributions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate_team_attacking_metrics(
        self,
        team_id: uuid.UUID,
        season_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Calculates volume, efficiency, expected goals (if recorded), and player contributions."""
        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        # Query team match statistics
        stat_stmt = (
            select(TeamMatchStatistic)
            .join(Match)
            .where(
                TeamMatchStatistic.team_id == team_id,
                Match.match_status == MatchStatus.FINISHED,
            )
            .options(
                selectinload(TeamMatchStatistic.match).selectinload(Match.home_team),
                selectinload(TeamMatchStatistic.match).selectinload(Match.away_team),
            )
        )
        if season_id:
            stat_stmt = stat_stmt.where(Match.season_id == season_id)
        stat_stmt = stat_stmt.order_by(Match.scheduled_kickoff.asc())

        stats: List[TeamMatchStatistic] = list((await self.session.execute(stat_stmt)).scalars().all())
        matches_count = len(stats)
        match_ids = [s.match_id for s in stats]

        # 1. Aggregation of Shot Volume
        shots_total = sum(s.shots_total for s in stats if s.shots_total is not None)
        shots_on_target = sum(s.shots_on_target for s in stats if s.shots_on_target is not None)
        shots_off_target = sum(s.shots_off_target for s in stats if s.shots_off_target is not None)
        blocked_shots = sum(s.blocked_shots for s in stats if s.blocked_shots is not None)

        # 2. Expected Goals (xG)
        xg_values = [s.expected_goals for s in stats if s.expected_goals is not None]
        total_xg: Optional[float] = round(sum(xg_values), 2) if xg_values else None
        xg_per_match = safe_divide(total_xg, len(xg_values)) if total_xg is not None else None

        # 3. Big Chances
        big_chances_created = sum(s.big_chances_created for s in stats if s.big_chances_created is not None)
        big_chances_missed = sum(s.big_chances_missed for s in stats if s.big_chances_missed is not None)

        # 4. Goals by Match & Total Goals
        goals_by_match: List[Dict[str, Any]] = []
        match_goals_sum = 0
        for s in stats:
            m = s.match
            if not m:
                continue
            is_home = m.home_team_id == team_id
            opponent = m.away_team if is_home else m.home_team
            t_score = (m.home_score if is_home else m.away_score) or 0
            match_goals_sum += t_score
            goals_by_match.append({
                "match_id": str(m.id),
                "match_number": m.match_number,
                "opponent_name": opponent.name if opponent else "Opponent",
                "opponent_short": opponent.short_name if opponent else "OPP",
                "goals": t_score,
                "kickoff": m.scheduled_kickoff.isoformat(),
            })

        # 5. Fetch Goals and Events for the Team
        goal_events: List[MatchEvent] = []
        if match_ids:
            event_stmt = (
                select(MatchEvent)
                .where(
                    MatchEvent.team_id == team_id,
                    MatchEvent.match_id.in_(match_ids),
                    MatchEvent.event_type.in_([EventType.GOAL, EventType.PENALTY_GOAL]),
                )
                .options(
                    selectinload(MatchEvent.primary_player),
                    selectinload(MatchEvent.secondary_player),
                )
            )
            goal_events = list((await self.session.execute(event_stmt)).scalars().all())

        total_goals = len(goal_events) if goal_events else match_goals_sum

        # Half-by-half breakdown
        first_half_goals = sum(1 for e in goal_events if e.period == MatchPeriod.FIRST_HALF)
        second_half_goals = sum(1 for e in goal_events if e.period == MatchPeriod.SECOND_HALF)
        extra_time_goals = sum(1 for e in goal_events if e.period in [MatchPeriod.EXTRA_FIRST, MatchPeriod.EXTRA_SECOND])

        # Shooting accuracy & conversion
        shooting_accuracy_pct = safe_divide(shots_on_target * 100.0, shots_total)
        conversion_rate_pct = safe_divide(total_goals * 100.0, shots_total)

        # Shot efficiency (goals minus xG, only when xG is available!)
        shot_efficiency = round(total_goals - total_xg, 2) if total_xg is not None else None

        # Player Goal Contributions
        player_goals = defaultdict(int)
        player_assists = defaultdict(int)
        player_names = {}

        for ge in goal_events:
            if ge.primary_player:
                p_id = str(ge.primary_player.id)
                player_goals[p_id] += 1
                player_names[p_id] = ge.primary_player.known_name or f"{ge.primary_player.first_name} {ge.primary_player.last_name}"
            if ge.secondary_player:
                a_id = str(ge.secondary_player.id)
                player_assists[a_id] += 1
                player_names[a_id] = ge.secondary_player.known_name or f"{ge.secondary_player.first_name} {ge.secondary_player.last_name}"

        # Combine contributions
        contributions = []
        all_player_ids = set(player_goals.keys()) | set(player_assists.keys())
        for pid in all_player_ids:
            g = player_goals[pid]
            a = player_assists[pid]
            contributions.append({
                "player_id": pid,
                "player_name": player_names.get(pid, "Player"),
                "goals": g,
                "assists": a,
                "goal_contributions": g + a,
            })
        contributions.sort(key=lambda x: (x["goal_contributions"], x["goals"]), reverse=True)

        total_assists = sum(player_assists.values()) if player_assists else None

        coverage = DataCoverageMetrics(
            sample_matches_count=matches_count,
            minutes_tracked=matches_count * 90,
            data_source_codes=["ISL_OFFICIAL"],
            has_event_level_data=total_goals > 0,
            has_tracking_gps_data=False,
            coverage_notes="Expected goals computed only when tracked by official league providers.",
        )

        return {
            "team_id": str(team.id),
            "team_name": team.name,
            "season_id": str(season_id) if season_id else None,
            "matches_analyzed": matches_count,
            "goals_scored": total_goals,
            "goals_per_match": safe_divide(total_goals, matches_count),
            "shots_total": shots_total,
            "shots_per_match": safe_divide(shots_total, matches_count),
            "shots_on_target": shots_on_target,
            "shots_off_target": shots_off_target,
            "blocked_shots": blocked_shots,
            "shooting_accuracy_pct": shooting_accuracy_pct,
            "conversion_rate_pct": conversion_rate_pct,
            "expected_goals": total_xg,
            "expected_goals_per_match": xg_per_match,
            "shot_efficiency": shot_efficiency,
            "total_assists": total_assists,
            "big_chances_created": big_chances_created if big_chances_created > 0 else None,
            "big_chances_missed": big_chances_missed if big_chances_missed > 0 else None,
            "half_breakdown": {
                "first_half_goals": first_half_goals,
                "second_half_goals": second_half_goals,
                "first_half_pct": safe_divide(first_half_goals * 100.0, total_goals),
                "second_half_pct": safe_divide(second_half_goals * 100.0, total_goals),
            },
            "goals_by_competition_phase": {
                "first_half_goals": first_half_goals,
                "second_half_goals": second_half_goals,
                "extra_time_goals": extra_time_goals,
            },
            "goals_by_match": goals_by_match,
            "goals_by_player": contributions,
            "top_contributors": contributions[:10],
            "data_coverage": coverage.to_dict(),
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
