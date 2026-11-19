"""Season Cleanup & Historical Data Isolation Service.

Isolates historical mock/seed match data into an earlier season (2025-26) to
preserve test match events and team statistics without corrupting active
2026-27 season metrics.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.models.competition import Season
from marina.models.match import Match
from marina.models.common import MatchStatus
from marina.models.team import Team, Venue

logger = logging.getLogger(__name__)

MOCK_MATCH_ID = "8054b142-9fae-4351-bd72-e5bb5ecb1000"
HISTORICAL_SEASON_NAME = "2025–26"
HISTORICAL_SEASON_SLUG = "isl-2025-26"
ACTIVE_SEASON_SLUG = "isl-2026-27"


class SeasonCleanupService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def isolate_historical_data(self) -> Dict[str, Any]:
        """Ensures 2025-26 historical season exists, moves mock match 8054b142 to it

        as FINISHED (5-3 against East Bengal FC), and creates/verifies a pristine
        unplayed Match #7 in 2026-27.
        """
        # 1. Fetch active season (2026-27)
        active_season_stmt = select(Season).where(
            (Season.slug == ACTIVE_SEASON_SLUG) | (Season.name == "2026–27")
        )
        active_season = (await self.db.execute(active_season_stmt)).scalars().first()
        if not active_season:
            raise ValueError("Active season 2026–27 not found in database.")

        # 2. Find or create historical season (2025-26)
        hist_season_stmt = select(Season).where(
            (Season.slug == HISTORICAL_SEASON_SLUG) | (Season.name == HISTORICAL_SEASON_NAME)
        )
        hist_season = (await self.db.execute(hist_season_stmt)).scalars().first()

        if not hist_season:
            hist_season = Season(
                id=uuid.uuid4(),
                competition_id=active_season.competition_id,
                name=HISTORICAL_SEASON_NAME,
                slug=HISTORICAL_SEASON_SLUG,
                start_date=datetime(2025, 9, 15).date(),
                end_date=datetime(2026, 4, 30).date(),
                is_current=False,
                is_completed=True,
            )
            self.db.add(hist_season)
            await self.db.flush()
            logger.info("Created historical season %s (%s)", HISTORICAL_SEASON_NAME, hist_season.id)

        # 3. Check and restore historical mock match
        mock_uuid = uuid.UUID(MOCK_MATCH_ID)
        mock_match = (await self.db.execute(select(Match).where(Match.id == mock_uuid))).scalars().first()

        moved_mock = False
        if mock_match:
            mock_match.season_id = hist_season.id
            ebfc = (await self.db.execute(select(Team).where(Team.short_name == "EBFC"))).scalars().first()
            cfc = (await self.db.execute(select(Team).where(Team.short_name == "CFC"))).scalars().first()
            if cfc:
                mock_match.home_team_id = cfc.id
            if ebfc:
                mock_match.away_team_id = ebfc.id
            mock_match.match_number = 7
            mock_match.match_status = MatchStatus.FINISHED
            mock_match.home_score = 5
            mock_match.away_score = 3
            mock_match.has_discrepancy = False
            mock_match.discrepancy_notes = "Historical 2025-26 test match record with verified events."
            await self.db.flush()
            moved_mock = True
            logger.info("Reassigned mock match %s to season %s with 5-3 finished score", MOCK_MATCH_ID, hist_season.name)

        # 4. Check Match #7 in active season (2026-27)
        m7_active = (await self.db.execute(
            select(Match).where(
                Match.season_id == active_season.id,
                Match.match_number == 7,
            )
        )).scalars().first()

        chennaiyin = (await self.db.execute(select(Team).where(Team.short_name == "CFC"))).scalars().first()
        mumbai = (await self.db.execute(select(Team).where(Team.short_name == "MCFC"))).scalars().first()
        jln_venue = (await self.db.execute(
            select(Venue).where(Venue.name.ilike("%Jawaharlal Nehru Stadium (Marina Arena)%"))
        )).scalars().first()

        created_m7 = False
        if not m7_active:
            m7_active = Match(
                id=uuid.uuid4(),
                season_id=active_season.id,
                home_team_id=chennaiyin.id if chennaiyin else None,
                away_team_id=mumbai.id if mumbai else None,
                match_number=7,
                scheduled_kickoff=datetime(2026, 11, 28, 19, 30, tzinfo=timezone.utc),
                kickoff_time_ist="7:30 PM",
                venue_id=jln_venue.id if jln_venue else None,
                match_status=MatchStatus.SCHEDULED,
                home_score=None,
                away_score=None,
                fixture_leg="FIRST_LEG",
                publication_status="PUBLISHED",
                verification_status="DISCREPANCY_FLAGGED",
                venue_verification_status="CONFIRMED",
                has_discrepancy=True,
                discrepancy_notes="Schedule discrepancy: Chennaiyin FC's own announcement lists Mumbai City away on 30 November, while the official ISL fixtures page lists Chennaiyin at home on 28 November. Working record follows ISL official schedule but is flagged for manual verification.",
                source_url="https://www.indiansuperleague.com/schedule-fixtures",
                last_verified_at=datetime.now(timezone.utc),
            )
            self.db.add(m7_active)
            await self.db.flush()
            created_m7 = True
            logger.info("Created clean scheduled Match #7 in season %s", active_season.name)
        else:
            m7_active.match_status = MatchStatus.SCHEDULED
            m7_active.home_score = None
            m7_active.away_score = None
            m7_active.has_discrepancy = True
            m7_active.verification_status = "DISCREPANCY_FLAGGED"

        # 5. Audit all 2026-27 fixtures: ensure no scheduled matches have scores
        all_active_matches = (await self.db.execute(
            select(Match).where(Match.season_id == active_season.id)
        )).scalars().all()

        unplayed_reset_count = 0
        for match in all_active_matches:
            if match.match_status == MatchStatus.SCHEDULED:
                if match.home_score is not None or match.away_score is not None:
                    match.home_score = None
                    match.away_score = None
                    unplayed_reset_count += 1

        await self.db.commit()

        # Re-query total count in 2026-27
        final_active_matches = (await self.db.execute(
            select(Match).where(Match.season_id == active_season.id)
        )).scalars().all()

        return {
            "historical_season_id": str(hist_season.id),
            "historical_season_name": hist_season.name,
            "moved_mock_match": moved_mock,
            "created_clean_match_7": created_m7,
            "unplayed_scores_reset": unplayed_reset_count,
            "active_season_matches_count": len(final_active_matches),
        }
