"""Script to verify ingested match data and season overview metrics."""
import asyncio
from marina.db.session import AsyncSessionLocal
from sqlalchemy import select, func
from marina.models.match import Match, MatchEvent, Lineup, MatchShot, MatchPass
from marina.models.statistics import TeamMatchStatistic, PlayerMatchStatistic
from marina.models.provenance import DataMetricVerification, DataSyncLog
from marina.services.season_overview_service import SeasonOverviewService


from sqlalchemy.orm import selectinload

async def main():
    async with AsyncSessionLocal() as session:
        # Check matches
        matches = (await session.execute(
            select(Match).where(Match.match_number.in_([1, 2, 3, 4, 5])).order_by(Match.match_number)
        )).scalars().all()

        print("=== MATCHES 1-5 ===")
        for m in matches:
            print(f"Match #{m.match_number}: {m.home_team.short_name} {m.home_score} - {m.away_score} {m.away_team.short_name} | status: {m.match_status.value} | Ref: {m.referee} | Att: {m.attendance}")

        # Check events count with eager loading
        events_stmt = (
            select(MatchEvent)
            .options(
                selectinload(MatchEvent.primary_player),
                selectinload(MatchEvent.secondary_player),
                selectinload(MatchEvent.match),
            )
            .order_by(MatchEvent.minute)
        )
        events = (await session.execute(events_stmt)).scalars().all()
        print(f"\nTotal Match Events: {len(events)}")
        for e in events:
            p_name = e.primary_player.known_name if e.primary_player else "N/A"
            s_name = f", Assist: {e.secondary_player.known_name}" if e.secondary_player else ""
            print(f"  Match #{e.match.match_number} | {e.minute}' | {e.event_type.value} | {p_name}{s_name}")

        # Check Team stats
        ts_count = len((await session.execute(select(TeamMatchStatistic))).scalars().all())
        print(f"\nTotal TeamMatchStatistic records: {ts_count}")

        # Check Player stats
        ps_count = len((await session.execute(select(PlayerMatchStatistic))).scalars().all())
        print(f"Total PlayerMatchStatistic records: {ps_count}")

        # Check verifications
        verifs = (await session.execute(select(DataMetricVerification))).scalars().all()
        print(f"\nTotal DataMetricVerification records: {len(verifs)}")
        for v in verifs:
            print(f"  [{v.verification_status}] {v.metric_name}: primary={v.primary_source} ({v.primary_value}) vs sec={v.secondary_source} ({v.secondary_value}) - disputed={v.is_disputed}")

        # Check Season Overview
        sos = SeasonOverviewService(session)
        overview = await sos.get_overview()
        print("\n=== CALCULATED SEASON OVERVIEW ===")
        print(f"Matches Played: {overview.matches_played}")
        print(f"Matches Remaining: {overview.matches_remaining}")
        print(f"Record (W-D-L): {overview.wins}-{overview.draws}-{overview.losses}")
        print(f"Points: {overview.points}")
        print(f"Goals Scored: {overview.goals_scored}")
        print(f"Goals Conceded: {overview.goals_conceded}")
        print(f"Goal Difference: {overview.goal_difference}")
        print(f"Recent Form: {overview.recent_form}")
        print(f"Clean Sheets: {overview.clean_sheets}")

        # Top Scorers
        top_scorers = await sos.get_top_scorers(limit=5)
        print("\n=== TOP SCORERS ===")
        for s in top_scorers:
            print(f"  {s.name} (#{s.jersey_number}): {s.goals} goals, {s.assists} assists ({s.minutes_played} mins)")


if __name__ == "__main__":
    asyncio.run(main())
