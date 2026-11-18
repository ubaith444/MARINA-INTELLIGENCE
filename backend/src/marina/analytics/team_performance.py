"""Module 1: Team Performance & Seasonal Form Intelligence Engine."""

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


class TeamPerformanceEngine:
    """Calculates comprehensive team season performance, home/away splits, and recent form."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def calculate_team_season_performance(
        self,
        team_id: uuid.UUID,
        season_id: uuid.UUID,
        form_window: int = 5,
    ) -> Dict[str, Any]:
        """Calculates seasonal record, home/away split, and recent form sequence."""
        # 1. Fetch team
        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        # 2. Fetch completed matches for this team in designated season
        stmt = (
            select(Match)
            .where(
                Match.season_id == season_id,
                or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
                Match.match_status == MatchStatus.FINISHED,
            )
            .options(selectinload(Match.home_team), selectinload(Match.away_team))
            .order_by(Match.scheduled_kickoff.asc())
        )
        matches: List[Match] = list((await self.session.execute(stmt)).scalars().all())

        total_played = len(matches)

        # Initialize counters
        wins = 0
        draws = 0
        losses = 0
        goals_for = 0
        goals_against = 0
        clean_sheets = 0

        # Home / Away counters
        home_m, home_w, home_d, home_l, home_gf, home_ga, home_cs = 0, 0, 0, 0, 0, 0, 0
        away_m, away_w, away_d, away_l, away_gf, away_ga, away_cs = 0, 0, 0, 0, 0, 0, 0

        form_results: List[Dict[str, Any]] = []

        for m in matches:
            is_home = m.home_team_id == team_id
            team_score = m.home_score if is_home else m.away_score
            opp_score = m.away_score if is_home else m.home_score
            opponent = m.away_team if is_home else m.home_team

            # Guard against corrupt null scores on finished match
            if team_score is None or opp_score is None:
                continue

            goals_for += team_score
            goals_against += opp_score

            if opp_score == 0:
                clean_sheets += 1

            if is_home:
                home_m += 1
                home_gf += team_score
                home_ga += opp_score
                if opp_score == 0:
                    home_cs += 1
            else:
                away_m += 1
                away_gf += team_score
                away_ga += opp_score
                if opp_score == 0:
                    away_cs += 1

            # Result determination
            if team_score > opp_score:
                outcome = "W"
                wins += 1
                if is_home:
                    home_w += 1
                else:
                    away_w += 1
            elif team_score == opp_score:
                outcome = "D"
                draws += 1
                if is_home:
                    home_d += 1
                else:
                    away_d += 1
            else:
                outcome = "L"
                losses += 1
                if is_home:
                    home_l += 1
                else:
                    away_l += 1

            form_results.append({
                "match_id": str(m.id),
                "match_number": m.match_number,
                "kickoff": m.scheduled_kickoff.isoformat(),
                "opponent_name": opponent.name if opponent else "Opponent",
                "opponent_short": opponent.short_name if opponent else "OPP",
                "is_home": is_home,
                "score": f"{team_score}-{opp_score}",
                "outcome": outcome,
                "points": 3 if outcome == "W" else (1 if outcome == "D" else 0),
            })

        points = (wins * 3) + draws
        goal_diff = goals_for - goals_against
        win_pct = safe_divide(wins * 100.0, total_played)
        points_per_match = safe_divide(points, total_played)
        clean_sheet_pct = safe_divide(clean_sheets * 100.0, total_played)
        gf_per_match = safe_divide(goals_for, total_played)
        ga_per_match = safe_divide(goals_against, total_played)

        # Home record
        home_pts = (home_w * 3) + home_d
        home_rec = {
            "matches_played": home_m,
            "wins": home_w,
            "draws": home_d,
            "losses": home_l,
            "points": home_pts,
            "goals_for": home_gf,
            "goals_against": home_ga,
            "goal_difference": home_gf - home_ga,
            "clean_sheets": home_cs,
            "win_percentage": safe_divide(home_w * 100.0, home_m),
            "points_per_match": safe_divide(home_pts, home_m),
        }

        # Away record
        away_pts = (away_w * 3) + away_d
        away_rec = {
            "matches_played": away_m,
            "wins": away_w,
            "draws": away_d,
            "losses": away_l,
            "points": away_pts,
            "goals_for": away_gf,
            "goals_against": away_ga,
            "goal_difference": away_gf - away_ga,
            "clean_sheets": away_cs,
            "win_percentage": safe_divide(away_w * 100.0, away_m),
            "points_per_match": safe_divide(away_pts, away_m),
        }

        # Recent form window (most recent last form_window fixtures)
        recent_matches = form_results[-form_window:] if total_played >= form_window else form_results
        form_sequence = [m["outcome"] for m in recent_matches]
        form_points = sum(m["points"] for m in recent_matches)
        form_ppm = safe_divide(form_points, len(recent_matches))

        # Query team match statistics for average possession
        stat_stmt = (
            select(TeamMatchStatistic)
            .join(Match)
            .where(
                TeamMatchStatistic.team_id == team_id,
                Match.season_id == season_id,
                Match.match_status == MatchStatus.FINISHED,
            )
        )
        match_stats = list((await self.session.execute(stat_stmt)).scalars().all())
        possession_values = [s.possession_pct for s in match_stats if s.possession_pct is not None]
        avg_possession = (
            safe_divide(sum(possession_values), len(possession_values))
            if possession_values
            else None
        )

        coverage = DataCoverageMetrics(
            sample_matches_count=total_played,
            minutes_tracked=total_played * 90,
            data_source_codes=["ISL_OFFICIAL"],
            has_event_level_data=total_played > 0,
            has_tracking_gps_data=False,
            coverage_notes="Verified ISL 2026-27 results record.",
        )

        return {
            "team_id": str(team.id),
            "team_name": team.name,
            "short_name": team.short_name,
            "season_id": str(season_id),
            "matches_played": total_played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "points": points,
            "goals_for": goals_for,
            "goals_against": goals_against,
            "goal_difference": goal_diff,
            "win_percentage": win_pct,
            "points_per_match": points_per_match,
            "clean_sheets": clean_sheets,
            "clean_sheet_percentage": clean_sheet_pct,
            "goals_for_per_match": gf_per_match,
            "goals_against_per_match": ga_per_match,
            "average_possession_pct": avg_possession,
            "home_record": home_rec,
            "away_record": away_rec,
            "recent_form": {
                "sequence": form_sequence,
                "sequence_str": "-".join(form_sequence) if form_sequence else "N/A",
                "form_points": form_points,
                "form_ppm": form_ppm,
                "matches": recent_matches,
            },
            "data_coverage": coverage.to_dict(),
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def calculate_home_away_analysis(
        self,
        team_id: uuid.UUID,
        season_id: Optional[uuid.UUID] = None,
    ) -> Dict[str, Any]:
        """Generates dedicated home vs away venue performance splits and comparative indices."""
        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        stmt = select(Match).where(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
            Match.match_status == MatchStatus.FINISHED,
        )
        if season_id:
            stmt = stmt.where(Match.season_id == season_id)
        stmt = stmt.order_by(Match.scheduled_kickoff.asc())

        matches: List[Match] = list((await self.session.execute(stmt)).scalars().all())

        home_m, home_w, home_d, home_l, home_gf, home_ga, home_cs = 0, 0, 0, 0, 0, 0, 0
        away_m, away_w, away_d, away_l, away_gf, away_ga, away_cs = 0, 0, 0, 0, 0, 0, 0

        for m in matches:
            is_home = m.home_team_id == team_id
            t_score = m.home_score if is_home else m.away_score
            o_score = m.away_score if is_home else m.home_score

            if t_score is None or o_score is None:
                continue

            if is_home:
                home_m += 1
                home_gf += t_score
                home_ga += o_score
                if o_score == 0:
                    home_cs += 1
                if t_score > o_score:
                    home_w += 1
                elif t_score == o_score:
                    home_d += 1
                else:
                    home_l += 1
            else:
                away_m += 1
                away_gf += t_score
                away_ga += o_score
                if o_score == 0:
                    away_cs += 1
                if t_score > o_score:
                    away_w += 1
                elif t_score == o_score:
                    away_d += 1
                else:
                    away_l += 1

        home_pts = (home_w * 3) + home_d
        away_pts = (away_w * 3) + away_d
        home_win_pct = safe_divide(home_w * 100.0, home_m)
        away_win_pct = safe_divide(away_w * 100.0, away_m)

        home_rec = {
            "matches_played": home_m,
            "wins": home_w,
            "draws": home_d,
            "losses": home_l,
            "points": home_pts,
            "goals_for": home_gf,
            "goals_against": home_ga,
            "goal_difference": home_gf - home_ga,
            "clean_sheets": home_cs,
            "win_percentage": home_win_pct,
            "points_per_match": safe_divide(home_pts, home_m),
            "goals_for_per_match": safe_divide(home_gf, home_m),
            "goals_against_per_match": safe_divide(home_ga, home_m),
        }

        away_rec = {
            "matches_played": away_m,
            "wins": away_w,
            "draws": away_d,
            "losses": away_l,
            "points": away_pts,
            "goals_for": away_gf,
            "goals_against": away_ga,
            "goal_difference": away_gf - away_ga,
            "clean_sheets": away_cs,
            "win_percentage": away_win_pct,
            "points_per_match": safe_divide(away_pts, away_m),
            "goals_for_per_match": safe_divide(away_gf, away_m),
            "goals_against_per_match": safe_divide(away_ga, away_m),
        }

        comparison = {
            "point_ratio_home_to_away": safe_divide(home_pts, away_pts),
            "win_pct_delta": (
                round(home_win_pct - away_win_pct, 2)
                if home_win_pct is not None and away_win_pct is not None
                else None
            ),
            "home_advantage_index": (
                safe_divide(home_pts * 100.0, home_pts + away_pts)
                if (home_pts + away_pts) > 0
                else None
            ),
        }

        return {
            "team_id": str(team.id),
            "team_name": team.name,
            "season_id": str(season_id) if season_id else None,
            "home_record": home_rec,
            "away_record": away_rec,
            "comparison": comparison,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }
