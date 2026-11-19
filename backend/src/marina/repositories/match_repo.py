"""Match, Lineup, and Match Event Repositories."""

import uuid
from datetime import date, datetime, time
from typing import Optional, Sequence
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from marina.models.common import MatchStatus
from marina.models.match import Lineup, Match, MatchEvent
from marina.models.team import Team, Venue
from marina.repositories.base import BaseRepository


class MatchRepository(BaseRepository[Match]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Match, session)

    async def get_match_detail(self, match_id: uuid.UUID) -> Optional[Match]:
        stmt = (
            select(Match)
            .where(Match.id == match_id)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
                selectinload(Match.lineups).selectinload(Lineup.player),
                selectinload(Match.events).selectinload(MatchEvent.primary_player),
                selectinload(Match.events).selectinload(MatchEvent.secondary_player),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_matches(
        self,
        season_id: Optional[uuid.UUID] = None,
        team_id: Optional[uuid.UUID] = None,
        status: Optional[MatchStatus] = None,
        is_home: Optional[bool] = None,
        matchweek: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Match]:
        stmt = (
            select(Match)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
            )
        )
        if season_id:
            stmt = stmt.where(Match.season_id == season_id)

        # Home / Away / Team filtering
        if team_id:
            if is_home is True:
                stmt = stmt.where(Match.home_team_id == team_id)
            elif is_home is False:
                stmt = stmt.where(Match.away_team_id == team_id)
            else:
                stmt = stmt.where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
        elif is_home is not None:
            # Default to club (Chennaiyin FC) if team_id not specified
            stmt_cfc = select(Team.id).where(Team.slug == "chennaiyin-fc").limit(1)
            cfc_res = await self.session.execute(stmt_cfc)
            cfc_id = cfc_res.scalar()
            if cfc_id:
                if is_home is True:
                    stmt = stmt.where(Match.home_team_id == cfc_id)
                elif is_home is False:
                    stmt = stmt.where(Match.away_team_id == cfc_id)

        if status:
            stmt = stmt.where(Match.match_status == status)

        if matchweek is not None:
            stmt = stmt.where(Match.match_number == matchweek)

        if start_date is not None:
            stmt = stmt.where(Match.scheduled_kickoff >= datetime.combine(start_date, time.min))

        if end_date is not None:
            stmt = stmt.where(Match.scheduled_kickoff <= datetime.combine(end_date, time.max))

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            home_team_alias = aliased(Team)
            away_team_alias = aliased(Team)
            venue_alias = aliased(Venue)
            stmt = (
                stmt.outerjoin(home_team_alias, Match.home_team_id == home_team_alias.id)
                .outerjoin(away_team_alias, Match.away_team_id == away_team_alias.id)
                .outerjoin(venue_alias, Match.venue_id == venue_alias.id)
                .where(
                    or_(
                        func.lower(home_team_alias.name).like(term),
                        func.lower(home_team_alias.short_name).like(term),
                        func.lower(away_team_alias.name).like(term),
                        func.lower(away_team_alias.short_name).like(term),
                        func.lower(venue_alias.name).like(term),
                        func.lower(venue_alias.city).like(term),
                    )
                )
            )

        stmt = stmt.order_by(Match.scheduled_kickoff.asc()).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()


class LineupRepository(BaseRepository[Lineup]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Lineup, session)

    async def list_by_match_team(
        self, match_id: uuid.UUID, team_id: uuid.UUID
    ) -> Sequence[Lineup]:
        stmt = (
            select(Lineup)
            .where(Lineup.match_id == match_id, Lineup.team_id == team_id)
            .options(selectinload(Lineup.player))
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()


class MatchEventRepository(BaseRepository[MatchEvent]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MatchEvent, session)

    async def list_by_match(self, match_id: uuid.UUID) -> Sequence[MatchEvent]:
        stmt = (
            select(MatchEvent)
            .where(MatchEvent.match_id == match_id)
            .order_by(MatchEvent.minute.asc(), MatchEvent.stoppage_minute.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()
