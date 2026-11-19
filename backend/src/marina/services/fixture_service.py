"""Fixture Service for Chennaiyin FC & ISL 2026–27 Fixture Management.

Enforces:
- Idempotent fixture imports (by season and match_number).
- Strict non-fabrication of upcoming scores (scores remain NULL).
- Preservation of verified results and historical match statistics.
- Tracking publication status, verification status, venue inferences, and discrepancies.
"""

import csv
import io
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.common import MatchStatus
from marina.models.competition import Competition, Season
from marina.models.match import Match
from marina.models.team import Team, Venue


TEAM_CATALOG = {
    "chennaiyin fc": ("Chennaiyin FC", "CFC", "chennaiyin-fc"),
    "cfc": ("Chennaiyin FC", "CFC", "chennaiyin-fc"),
    "fc goa": ("FC Goa", "FCG", "fc-goa"),
    "fcg": ("FC Goa", "FCG", "fc-goa"),
    "bengaluru fc": ("Bengaluru FC", "BFC", "bengaluru-fc"),
    "bfc": ("Bengaluru FC", "BFC", "bengaluru-fc"),
    "mohun bagan sg": ("Mohun Bagan SG", "MBSG", "mohun-bagan-sg"),
    "mohun bagan": ("Mohun Bagan SG", "MBSG", "mohun-bagan-sg"),
    "mbsg": ("Mohun Bagan SG", "MBSG", "mohun-bagan-sg"),
    "kerala blasters": ("Kerala Blasters FC", "KBFC", "kerala-blasters-fc"),
    "kerala blasters fc": ("Kerala Blasters FC", "KBFC", "kerala-blasters-fc"),
    "kbfc": ("Kerala Blasters FC", "KBFC", "kerala-blasters-fc"),
    "east bengal fc": ("East Bengal FC", "EBFC", "east-bengal-fc"),
    "east bengal": ("East Bengal FC", "EBFC", "east-bengal-fc"),
    "ebfc": ("East Bengal FC", "EBFC", "east-bengal-fc"),
    "punjab fc": ("Punjab FC", "PFC", "punjab-fc"),
    "pfc": ("Punjab FC", "PFC", "punjab-fc"),
    "mumbai city fc": ("Mumbai City FC", "MCFC", "mumbai-city-fc"),
    "mumbai city": ("Mumbai City FC", "MCFC", "mumbai-city-fc"),
    "mcfc": ("Mumbai City FC", "MCFC", "mumbai-city-fc"),
    "northeast united": ("NorthEast United FC", "NEUFC", "northeast-united-fc"),
    "northeast united fc": ("NorthEast United FC", "NEUFC", "northeast-united-fc"),
    "neufc": ("NorthEast United FC", "NEUFC", "northeast-united-fc"),
    "churchill brothers": ("Churchill Brothers", "CBFC", "churchill-brothers"),
    "cbfc": ("Churchill Brothers", "CBFC", "churchill-brothers"),
    "inter kashi": ("Inter Kashi", "IKFC", "inter-kashi"),
    "ikfc": ("Inter Kashi", "IKFC", "inter-kashi"),
    "odisha fc": ("Odisha FC", "OFC", "odisha-fc"),
    "ofc": ("Odisha FC", "OFC", "odisha-fc"),
    "sporting club delhi": ("Sporting Club Delhi", "SCD", "sporting-club-delhi"),
    "scd": ("Sporting Club Delhi", "SCD", "sporting-club-delhi"),
}

VENUE_CATALOG = {
    "fatorda stadium, goa": ("Pandit Jawaharlal Nehru Stadium (Fatorda)", "Goa"),
    "pandit jawaharlal nehru stadium, goa": ("Pandit Jawaharlal Nehru Stadium (Fatorda)", "Goa"),
    "sree kanteerava, bengaluru": ("Sree Kanteerava Stadium", "Bengaluru"),
    "vivekananda ybk, kolkata": ("Vivekananda Yuba Bharati Krirangan (Salt Lake Stadium)", "Kolkata"),
    "vivekananda yuba bharati krirangan, kolkata": ("Vivekananda Yuba Bharati Krirangan (Salt Lake Stadium)", "Kolkata"),
    "jln stadium, chennai": ("Jawaharlal Nehru Stadium (Marina Arena)", "Chennai"),
    "jawaharlal nehru stadium, chennai": ("Jawaharlal Nehru Stadium (Marina Arena)", "Chennai"),
    "indira gandhi stadium, guwahati": ("Indira Gandhi Athletic Stadium", "Guwahati"),
    "jln stadium, new delhi": ("Jawaharlal Nehru Stadium (Delhi)", "New Delhi"),
    "jawaharlal nehru stadium, new delhi": ("Jawaharlal Nehru Stadium (Delhi)", "New Delhi"),
    "mumbai football arena, mumbai": ("Mumbai Football Arena", "Mumbai"),
    "jawaharlal nehru stadium, kochi": ("Jawaharlal Nehru Stadium (Kaloor)", "Kochi"),
    "kalinga stadium, bhubaneswar": ("Kalinga Stadium", "Bhubaneswar"),
}


class FixtureService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def parse_raw_fixtures(raw_content: str | bytes, format_hint: str = "json") -> List[Dict[str, Any]]:
        """Parses raw JSON or CSV fixture payloads into standardized dictionary records."""
        if isinstance(raw_content, bytes):
            raw_content = raw_content.decode("utf-8")

        if format_hint.lower() == "json" or raw_content.strip().startswith("["):
            try:
                return json.loads(raw_content)
            except Exception:
                pass

        # Parse CSV
        reader = csv.DictReader(io.StringIO(raw_content))
        records = []
        for row in reader:
            records.append({k.strip(): v.strip() if v else None for k, v in row.items()})
        return records

    async def resolve_or_create_team(self, team_name_or_slug: str) -> Team:
        """Resolves team from database or creates it based on standardized ISL catalog."""
        clean = team_name_or_slug.strip().lower()
        official_name, short_name, slug = TEAM_CATALOG.get(clean, (team_name_or_slug.strip(), team_name_or_slug[:4].upper(), team_name_or_slug.strip().lower().replace(" ", "-")))

        stmt = select(Team).where(
            or_(
                Team.slug == slug,
                func.lower(Team.name) == official_name.lower(),
                func.lower(Team.short_name) == short_name.lower(),
            )
        )
        team = (await self.db.execute(stmt)).scalars().first()
        if team:
            return team

        team = Team(
            name=official_name,
            short_name=short_name,
            slug=slug,
            is_active=True,
        )
        self.db.add(team)
        await self.db.flush()
        return team

    async def resolve_or_create_venue(self, venue_str: Optional[str]) -> Optional[Venue]:
        """Resolves venue or creates it, returning None if TBC / missing."""
        if not venue_str:
            return None
        v_clean = venue_str.strip().lower()
        if v_clean in ("tbc", "none", "null", "—", "-"):
            return None

        v_name, city = VENUE_CATALOG.get(v_clean, (venue_str.strip(), "India"))

        stmt = select(Venue).where(
            or_(
                func.lower(Venue.name) == v_name.lower(),
                func.lower(Venue.name).ilike(f"%{city.lower()}%"),
            )
        )
        venue = (await self.db.execute(stmt)).scalars().first()
        if venue:
            return venue

        venue = Venue(
            name=v_name,
            city=city,
            country="India",
            is_active=True,
        )
        self.db.add(venue)
        await self.db.flush()
        return venue

    async def resolve_season(self, season_id: Optional[uuid.UUID] = None) -> Season:
        """Resolves active 2026–27 season."""
        if season_id:
            s_stmt = select(Season).where(Season.id == season_id)
            s = (await self.db.execute(s_stmt)).scalars().first()
            if s:
                return s

        stmt = select(Season).where(
            or_(
                Season.is_current.is_(True),
                Season.slug.ilike("%2026-27%"),
                Season.name.ilike("%2026–27%"),
            )
        )
        season = (await self.db.execute(stmt)).scalars().first()
        if not season:
            stmt_any = select(Season).limit(1)
            season = (await self.db.execute(stmt_any)).scalars().first()
        if not season:
            comp = Competition(code="ISL", name="Indian Super League", country="India", federation="AIFF")
            self.db.add(comp)
            await self.db.flush()
            season = Season(
                competition_id=comp.id,
                name="2026–27",
                slug="isl-2026-27",
                is_current=True,
            )
            self.db.add(season)
            await self.db.flush()
        return season

    async def import_fixtures(
        self,
        raw_records: List[Dict[str, Any]],
        season_id: Optional[uuid.UUID] = None,
        source_url_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Imports or updates 24 fixtures idempotently for Chennaiyin FC ISL 2026–27.
        
        Strict Non-Fabrication Rules:
        - Scores remain NULL for upcoming/unplayed fixtures.
        - Already recorded verified scores and match stats are NEVER overwritten.
        - Missing dates/venues/kickoffs (like #24 TBC) are kept as NULL.
        - Matches are identified by (season_id, match_number).
        """
        season = await self.resolve_season(season_id)
        batch_id = f"fix-sync-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        published_count = 0
        provisional_count = 0
        discrepancies_flagged = 0
        new_created = 0
        updated = 0
        total_processed = 0

        for r in raw_records:
            # Normalize keys to lowercase stripped
            norm = {str(k).strip().lower(): v for k, v in r.items() if k is not None}

            match_num_raw = norm.get("match_number") or norm.get("#") or norm.get("match_no")
            if match_num_raw is None:
                continue
            try:
                match_number = int(str(match_num_raw).strip())
            except ValueError:
                continue

            home_team_raw = norm.get("home_team") or norm.get("home") or norm.get("home team")
            away_team_raw = norm.get("away_team") or norm.get("away") or norm.get("away team")
            if not home_team_raw or not away_team_raw:
                continue

            home_team = await self.resolve_or_create_team(str(home_team_raw))
            away_team = await self.resolve_or_create_team(str(away_team_raw))

            # Venue resolution (NULL if TBC or missing)
            venue_raw = norm.get("venue") or norm.get("expected home venue") or norm.get("stadium")
            venue = await self.resolve_or_create_venue(str(venue_raw) if venue_raw else None)

            # Kickoff resolution (NULL if TBC or missing)
            kickoff_str = norm.get("scheduled_kickoff")
            kickoff_ist_raw = norm.get("kickoff_ist") or norm.get("kickoff") or norm.get("time")
            kickoff_time_ist = str(kickoff_ist_raw).strip() if kickoff_ist_raw and str(kickoff_ist_raw).strip().lower() != "tbc" else None

            scheduled_dt: Optional[datetime] = None
            if kickoff_str and str(kickoff_str).strip().lower() not in ("tbc", "none", "null", ""):
                try:
                    scheduled_dt = datetime.fromisoformat(str(kickoff_str).strip())
                except Exception:
                    pass

            # Fixture Leg & Phase
            fixture_leg = str(norm.get("fixture_leg") or ("FIRST_LEG" if match_number <= 12 else "SECOND_LEG")).upper()

            # Publication & Verification Status
            if fixture_leg == "FIRST_LEG":
                publication_status = "PUBLISHED"
                verification_status = "PUBLISHED"
                venue_verification_status = "CONFIRMED"
                published_count += 1
            else:
                publication_status = "PROVISIONAL"
                verification_status = "PENDING" if match_number == 24 else "PROVISIONAL"
                venue_verification_status = "TBC" if match_number == 24 else "INFERRED"
                provisional_count += 1

            # Discrepancy Flag (Fixture #7 Mumbai City FC discrepancy)
            has_discrepancy = False
            discrepancy_notes = norm.get("discrepancy_notes")

            if match_number == 7 or str(norm.get("has_discrepancy")).lower() in ("true", "1"):
                has_discrepancy = True
                verification_status = "DISCREPANCY_FLAGGED"
                discrepancies_flagged += 1
                if not discrepancy_notes:
                    discrepancy_notes = (
                        "Schedule discrepancy: Chennaiyin FC's own announcement lists Mumbai City away on 30 November, "
                        "while the official ISL fixtures page lists Chennaiyin at home on 28 November. "
                        "Working record follows ISL official schedule but is flagged for manual verification."
                    )

            source_url = source_url_override or norm.get("source_url") or "https://www.indiansuperleague.com/schedule-fixtures"

            # Check existing match fixture by season_id & match_number
            stmt = select(Match).where(
                Match.season_id == season.id,
                Match.match_number == match_number,
            )
            existing_match = (await self.db.execute(stmt)).scalars().first()

            if existing_match:
                # Update fixture details WITHOUT overwriting verified completed match scores
                existing_match.home_team_id = home_team.id
                existing_match.away_team_id = away_team.id
                existing_match.venue_id = venue.id if venue else None
                existing_match.scheduled_kickoff = scheduled_dt
                existing_match.kickoff_time_ist = kickoff_time_ist
                existing_match.fixture_leg = fixture_leg
                existing_match.publication_status = publication_status
                existing_match.verification_status = verification_status
                existing_match.venue_verification_status = venue_verification_status
                existing_match.has_discrepancy = has_discrepancy
                existing_match.discrepancy_notes = discrepancy_notes
                existing_match.source_url = source_url
                existing_match.last_verified_at = datetime.now(timezone.utc)

                # If match is NOT already finished, scores must remain NULL
                if existing_match.match_status != MatchStatus.FINISHED:
                    existing_match.home_score = None
                    existing_match.away_score = None
                    existing_match.match_status = MatchStatus.SCHEDULED

                updated += 1
            else:
                # Create brand new scheduled fixture
                new_match = Match(
                    season_id=season.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    venue_id=venue.id if venue else None,
                    match_number=match_number,
                    scheduled_kickoff=scheduled_dt,
                    kickoff_time_ist=kickoff_time_ist,
                    fixture_leg=fixture_leg,
                    publication_status=publication_status,
                    verification_status=verification_status,
                    venue_verification_status=venue_verification_status,
                    has_discrepancy=has_discrepancy,
                    discrepancy_notes=discrepancy_notes,
                    source_url=source_url,
                    last_verified_at=datetime.now(timezone.utc),
                    match_status=MatchStatus.SCHEDULED,
                    home_score=None,
                    away_score=None,
                )
                self.db.add(new_match)
                new_created += 1

            total_processed += 1

        await self.db.flush()

        return {
            "batch_id": batch_id,
            "season_id": str(season.id),
            "total_processed": total_processed,
            "published_count": published_count,
            "provisional_count": provisional_count,
            "discrepancies_flagged": discrepancies_flagged,
            "new_created": new_created,
            "updated": updated,
            "status": "COMPLETED",
            "message": f"Successfully imported {total_processed} fixtures for Chennaiyin FC ISL 2026–27.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def list_fixtures(
        self,
        season_id: Optional[uuid.UUID] = None,
        opponent: Optional[str] = None,
        home_away: Optional[str] = None,  # "HOME", "AWAY", "ALL"
        verification_status: Optional[str] = None,  # "PUBLISHED", "PROVISIONAL", "DISCREPANCY_FLAGGED", "COMPLETED"
        publication_status: Optional[str] = None,  # "PUBLISHED", "PROVISIONAL"
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Match]:
        """Queries fixtures with multi-criteria filtering."""
        season = await self.resolve_season(season_id)

        stmt = (
            select(Match)
            .where(Match.season_id == season.id)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
            )
            .order_by(Match.match_number.asc().nulls_last())
        )

        # Home/Away filter relative to Chennaiyin FC
        cfc_stmt = select(Team).where(Team.slug == "chennaiyin-fc")
        cfc = (await self.db.execute(cfc_stmt)).scalars().first()
        cfc_id = cfc.id if cfc else None

        if cfc_id and home_away:
            ha_upper = home_away.upper()
            if ha_upper == "HOME":
                stmt = stmt.where(Match.home_team_id == cfc_id)
            elif ha_upper == "AWAY":
                stmt = stmt.where(Match.away_team_id == cfc_id)

        # Opponent Filter
        if opponent:
            opp_pattern = f"%{opponent.strip().lower()}%"
            opp_team_ids_stmt = select(Team.id).where(
                or_(
                    func.lower(Team.name).ilike(opp_pattern),
                    func.lower(Team.short_name).ilike(opp_pattern),
                    func.lower(Team.slug).ilike(opp_pattern),
                )
            )
            opp_ids = (await self.db.execute(opp_team_ids_stmt)).scalars().all()
            if opp_ids:
                stmt = stmt.where(
                    or_(
                        Match.home_team_id.in_(opp_ids),
                        Match.away_team_id.in_(opp_ids),
                    )
                )

        # Verification Status Filter
        if verification_status and verification_status != "ALL":
            v_upper = verification_status.upper()
            if v_upper == "COMPLETED":
                stmt = stmt.where(Match.match_status == MatchStatus.FINISHED)
            else:
                stmt = stmt.where(Match.verification_status == v_upper)

        # Publication Status Filter
        if publication_status and publication_status != "ALL":
            stmt = stmt.where(Match.publication_status == publication_status.upper())

        # Date Range Filter
        if date_from:
            stmt = stmt.where(Match.scheduled_kickoff >= date_from)
        if date_to:
            stmt = stmt.where(Match.scheduled_kickoff <= date_to)

        stmt = stmt.offset(offset).limit(limit)
        results = (await self.db.execute(stmt)).scalars().all()
        return list(results)

    async def get_fixture_by_id(self, match_id: uuid.UUID) -> Optional[Match]:
        """Fetches full fixture record by ID."""
        stmt = (
            select(Match)
            .where(Match.id == match_id)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
                selectinload(Match.lineups),
                selectinload(Match.events),
            )
        )
        return (await self.db.execute(stmt)).scalars().first()

    async def get_season_fixtures(self, season_slug: str = "2026-27") -> List[Match]:
        """Returns all 24 fixtures for Chennaiyin FC 2026–27 season."""
        season = await self.resolve_season()
        stmt = (
            select(Match)
            .where(Match.season_id == season.id)
            .options(
                selectinload(Match.home_team),
                selectinload(Match.away_team),
                selectinload(Match.venue),
            )
            .order_by(Match.match_number.asc().nulls_last())
        )
        return list((await self.db.execute(stmt)).scalars().all())
