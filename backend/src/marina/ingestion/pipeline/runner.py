"""Complete Football Ingestion Pipeline Orchestrator."""

import logging
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from marina.core.exceptions import (
    FabricatedDataViolationError,
    IntegrityConstraintViolationError,
)
from marina.ingestion.archive.raw_storage import RawArchiveStorage
from marina.ingestion.extractors.chennaiyin_fc import ChennaiyinFCOfficialExtractor
from marina.ingestion.extractors.isl_official import ISLOfficialExtractor
from marina.ingestion.transformers.normalizer import FootballNormalizer
from marina.ingestion.validators.conflict_detector import ConflictDetector
from marina.ingestion.validators.schemas import (
    FixturesDataFrameSchema,
    IngestedFixtureRecord,
    IngestedPlayerRecord,
    SquadDataFrameSchema,
)
from marina.models.common import (
    BatchStatus,
    EventType,
    LineupRole,
    MatchPeriod,
    MatchStatus,
    ProviderType,
    SquadStatus,
    VerificationStatus,
)
from marina.models.competition import Competition, Season
from marina.models.match import Match, MatchEvent
from marina.models.player import Player, SquadRegistration
from marina.models.provenance import DataSource, ImportHistory
from marina.models.statistics import TeamMatchStatistic
from marina.models.team import Team, Venue

logger = logging.getLogger("marina.ingestion.pipeline")


class IngestionPipelineRunner:
    """End-to-end ingestion orchestrator for MARINA INTELLIGENCE."""

    def __init__(
        self,
        session: AsyncSession,
        archive_storage: Optional[RawArchiveStorage] = None,
        mock_mode: bool = False,
    ) -> None:
        self.session = session
        self.archive = archive_storage or RawArchiveStorage()
        self.conflict_detector = ConflictDetector()
        self.mock_mode = mock_mode

    async def ensure_data_sources_registered(self) -> Dict[str, DataSource]:
        """Registers and returns all authoritative data sources."""
        sources_to_register = [
            ("ISL_OFFICIAL", "Indian Super League Official Match Center", ProviderType.OFFICIAL_LEAGUE, "https://www.indiansuperleague.com", 100),
            ("CHENNAIYIN_FC_OFFICIAL", "Chennaiyin FC Official Club Portal", ProviderType.CLUB_COMMUNICATIONS, "https://chennaiyinfc.com", 100),
            ("AIFF_OFFICIAL", "All India Football Federation Official Registry", ProviderType.FEDERATION, "https://www.the-aiff.com", 95),
            ("MANUAL_CURATION", "Manually Verified File Ingestion", ProviderType.MANUAL_CURATION, None, 90),
            ("STATSBOMB_OPEN_DATA", "StatsBomb Open Data (Algorithmic Test Benchmark)", ProviderType.DATA_PROVIDER, "https://raw.githubusercontent.com/statsbomb/open-data/master/data", 80),
        ]

        result: Dict[str, DataSource] = {}
        for code, name, ptype, url, trust in sources_to_register:
            stmt = select(DataSource).where(DataSource.code == code)
            res = await self.session.execute(stmt)
            ds = res.scalars().first()
            if not ds:
                ds = DataSource(
                    code=code,
                    name=name,
                    provider_type=ptype,
                    base_url=url,
                    trust_score=trust,
                )
                self.session.add(ds)
                await self.session.flush()
            result[code] = ds

        return result

    async def ensure_competition_and_season(
        self, season_code: str = "2026–27"
    ) -> Tuple[Competition, Season]:
        """Ensures Indian Super League competition and designated season exist."""
        # Competition
        comp_stmt = select(Competition).where(Competition.code == "ISL")
        comp = (await self.session.execute(comp_stmt)).scalars().first()
        if not comp:
            comp = Competition(
                code="ISL",
                name="Indian Super League",
                country="India",
                federation="AIFF",
                tier=1,
                competition_type="LEAGUE",
            )
            self.session.add(comp)
            await self.session.flush()

        # Season
        slug = f"isl-{FootballNormalizer.normalize_slug(season_code)}"
        season_stmt = select(Season).where(Season.competition_id == comp.id, Season.slug == slug)
        season = (await self.session.execute(season_stmt)).scalars().first()
        if not season:
            season = Season(
                competition_id=comp.id,
                name=season_code,
                slug=slug,
                start_date=date(2026, 9, 15),
                end_date=date(2027, 4, 30),
                is_current=True,
            )
            self.session.add(season)
            await self.session.flush()

        return comp, season

    async def ensure_team_and_venue(self, team_dict: Dict[str, str], venue_name: Optional[str] = None) -> Team:
        """Ensures club team and optional primary venue are registered idempotently."""
        slug = team_dict["slug"]
        stmt = select(Team).where(Team.slug == slug)
        team = (await self.session.execute(stmt)).scalars().first()

        venue_id = None
        if venue_name:
            v_stmt = select(Venue).where(Venue.name == venue_name)
            venue = (await self.session.execute(v_stmt)).scalars().first()
            if not venue:
                venue = Venue(
                    name=venue_name,
                    city="Chennai" if "Marina" in venue_name else "Unknown",
                    country="India",
                )
                self.session.add(venue)
                await self.session.flush()
            venue_id = venue.id

        if not team:
            team = Team(
                name=team_dict["name"],
                short_name=team_dict["short_name"],
                slug=slug,
                primary_venue_id=venue_id,
                primary_color=team_dict.get("primary_color"),
                secondary_color=team_dict.get("secondary_color"),
            )
            self.session.add(team)
            await self.session.flush()

        return team

    async def ingest_fixtures(self, season_code: str = "2026–27") -> Dict[str, Any]:
        """Ingests ISL fixtures from official source."""
        sources = await self.ensure_data_sources_registered()
        source = sources["ISL_OFFICIAL"]
        comp, season = await self.ensure_competition_and_season(season_code)

        batch_id = f"batch-fixtures-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        extractor = ISLOfficialExtractor(mock_mode=self.mock_mode)

        # 1. Extraction
        raw_data = await extractor.extract_fixtures(season_code=season_code)

        # 2. Immutable Raw Archive Storage
        archive_meta = self.archive.archive_payload(
            source_code=source.code,
            entity_type="FIXTURES",
            batch_id=batch_id,
            content=raw_data,
            source_url=raw_data.get("source_url"),
        )

        fixtures_list = raw_data.get("fixtures", [])
        imported_count = 0

        # Convert to DataFrame for Pandera validation
        if fixtures_list:
            df_rows = []
            for f in fixtures_list:
                df_rows.append({
                    "home_team": f["home_team"],
                    "away_team": f["away_team"],
                    "scheduled_kickoff": pd.to_datetime(f["scheduled_kickoff"]),
                    "match_status": f.get("match_status", "SCHEDULED"),
                    "home_score": f.get("home_score"),
                    "away_score": f.get("away_score"),
                })
            df = pd.DataFrame(df_rows)
            # Pandera validation
            FixturesDataFrameSchema.validate(df)

        # 3. Transform & Idempotent Upsert
        for item in fixtures_list:
            # Pydantic validation
            rec = IngestedFixtureRecord.model_validate(item)

            home_dict = FootballNormalizer.resolve_team(rec.home_team)
            away_dict = FootballNormalizer.resolve_team(rec.away_team)
            home_team = await self.ensure_team_and_venue(home_dict, venue_name=item.get("venue"))
            away_team = await self.ensure_team_and_venue(away_dict)

            kickoff = FootballNormalizer.normalize_datetime(rec.scheduled_kickoff)
            status_enum = MatchStatus(rec.match_status.upper())

            # Check existing match (by season, home_team, away_team)
            match_stmt = select(Match).where(
                Match.season_id == season.id,
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id,
            )
            existing_match = (await self.session.execute(match_stmt)).scalars().first()

            if existing_match:
                # Update without duplicating
                existing_match.scheduled_kickoff = kickoff
                existing_match.match_number = rec.match_number or existing_match.match_number
                existing_match.match_status = status_enum
            else:
                new_match = Match(
                    season_id=season.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    venue_id=home_team.primary_venue_id,
                    match_number=rec.match_number,
                    scheduled_kickoff=kickoff,
                    match_status=status_enum,
                    home_score=None,  # Preserved as None for SCHEDULED!
                    away_score=None,
                )
                self.session.add(new_match)

            imported_count += 1

        # 4. Ingestion Batch Audit Record
        history = ImportHistory(
            data_source_id=source.id,
            entity_type="FIXTURES",
            batch_id=batch_id,
            status=BatchStatus.COMPLETED,
            records_imported=imported_count,
            records_failed=0,
            checksum_hash=archive_meta["checksum_sha256"],
            source_url=archive_meta["source_url"],
            payload_path=archive_meta["payload_path"],
        )
        self.session.add(history)
        await self.session.flush()

        return {
            "status": "COMPLETED",
            "batch_id": batch_id,
            "records_imported": imported_count,
            "archive_path": archive_meta["payload_path"],
        }

    async def ingest_results(self, season_code: str = "2026–27") -> Dict[str, Any]:
        """Ingests verified match results, events, and stats (e.g. CFC 5–3 East Bengal)."""
        sources = await self.ensure_data_sources_registered()
        source = sources["ISL_OFFICIAL"]
        comp, season = await self.ensure_competition_and_season(season_code)

        batch_id = f"batch-results-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        extractor = ISLOfficialExtractor(mock_mode=self.mock_mode)

        # 1. Extraction
        raw_data = await extractor.extract_results(season_code=season_code)

        # 2. Raw Archive Storage
        archive_meta = self.archive.archive_payload(
            source_code=source.code,
            entity_type="RESULTS",
            batch_id=batch_id,
            content=raw_data,
            source_url=raw_data.get("source_url"),
        )

        results_list = raw_data.get("results", [])
        imported_count = 0

        for r in results_list:
            home_dict = FootballNormalizer.resolve_team(r["home_team"])
            away_dict = FootballNormalizer.resolve_team(r["away_team"])
            home_team = await self.ensure_team_and_venue(home_dict, venue_name=r.get("venue"))
            away_team = await self.ensure_team_and_venue(away_dict)
            kickoff = FootballNormalizer.normalize_datetime(r["kickoff"])

            # Find or create match
            stmt = select(Match).where(
                Match.season_id == season.id,
                Match.home_team_id == home_team.id,
                Match.away_team_id == away_team.id,
            )
            match = (await self.session.execute(stmt)).scalars().first()

            incoming_home_score = r.get("home_score")
            incoming_away_score = r.get("away_score")

            if match:
                # CONFLICT DETECTION CHECK
                is_conflict, v_status = self.conflict_detector.check_match_score_conflict(
                    match_id=str(match.id),
                    existing_status=match.match_status,
                    existing_home=match.home_score,
                    existing_away=match.away_score,
                    incoming_status=MatchStatus.FINISHED,
                    incoming_home=incoming_home_score,
                    incoming_away=incoming_away_score,
                    source_code=source.code,
                )

                if not is_conflict:
                    match.home_score = incoming_home_score
                    match.away_score = incoming_away_score
                    match.match_status = MatchStatus.FINISHED
                    match.actual_kickoff = kickoff
                    match.attendance = r.get("attendance")
            else:
                match = Match(
                    season_id=season.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    venue_id=home_team.primary_venue_id,
                    match_number=r.get("match_number"),
                    scheduled_kickoff=kickoff,
                    actual_kickoff=kickoff,
                    match_status=MatchStatus.FINISHED,
                    home_score=incoming_home_score,
                    away_score=incoming_away_score,
                    attendance=r.get("attendance"),
                )
                self.session.add(match)
                await self.session.flush()

            # Ingest discrete events (goals, cards, substitutions)
            for ev in r.get("events", []):
                event_type_str = ev.get("event_type", "GOAL").upper()
                ev_type = EventType(event_type_str)
                team_target = home_team if ev.get("team") == home_team.name else away_team

                # Ensure player exists for the event
                player_name = ev.get("player")
                primary_player_id = None
                if player_name:
                    p_slug = FootballNormalizer.normalize_slug(player_name)
                    p_stmt = select(Player).where(Player.slug == p_slug)
                    player_obj = (await self.session.execute(p_stmt)).scalars().first()
                    if not player_obj:
                        name_parts = player_name.split()
                        player_obj = Player(
                            slug=p_slug,
                            first_name=name_parts[0],
                            last_name=" ".join(name_parts[1:]) if len(name_parts) > 1 else name_parts[0],
                            known_name=player_name,
                        )
                        self.session.add(player_obj)
                        await self.session.flush()
                    primary_player_id = player_obj.id

                match_event = MatchEvent(
                    match_id=match.id,
                    team_id=team_target.id,
                    primary_player_id=primary_player_id,
                    data_source_id=source.id,
                    event_type=ev_type,
                    period=MatchPeriod(ev.get("period", "FIRST_HALF")),
                    minute=ev.get("minute", 0),
                    description=ev.get("description"),
                    verification_status=VerificationStatus.OFFICIAL,
                    is_verified=True,
                )
                self.session.add(match_event)

            # Ingest Team Match Statistics (preserves NULL for unmeasured metrics)
            team_stats = r.get("team_statistics", {})
            for t_name, stats in team_stats.items():
                target_team = home_team if t_name == home_team.name else away_team

                # Check existing stats
                stat_stmt = select(TeamMatchStatistic).where(
                    TeamMatchStatistic.match_id == match.id,
                    TeamMatchStatistic.team_id == target_team.id,
                    TeamMatchStatistic.data_source_id == source.id,
                )
                existing_stat = (await self.session.execute(stat_stmt)).scalars().first()

                if not existing_stat:
                    new_stat = TeamMatchStatistic(
                        match_id=match.id,
                        team_id=target_team.id,
                        data_source_id=source.id,
                        verification_status=VerificationStatus.OFFICIAL,
                        is_verified=True,
                        possession_pct=FootballNormalizer.normalize_nullable_metric(stats.get("possession_pct"), float),
                        shots_total=FootballNormalizer.normalize_nullable_metric(stats.get("shots_total"), int),
                        shots_on_target=FootballNormalizer.normalize_nullable_metric(stats.get("shots_on_target"), int),
                        shots_off_target=FootballNormalizer.normalize_nullable_metric(stats.get("shots_off_target"), int),
                        blocked_shots=FootballNormalizer.normalize_nullable_metric(stats.get("blocked_shots"), int),
                        expected_goals=FootballNormalizer.normalize_nullable_metric(stats.get("expected_goals"), float),
                        corners=FootballNormalizer.normalize_nullable_metric(stats.get("corners"), int),
                        fouls_committed=FootballNormalizer.normalize_nullable_metric(stats.get("fouls_committed"), int),
                        yellow_cards=FootballNormalizer.normalize_nullable_metric(stats.get("yellow_cards"), int),
                        red_cards=FootballNormalizer.normalize_nullable_metric(stats.get("red_cards"), int),
                    )
                    self.session.add(new_stat)

            imported_count += 1

        history = ImportHistory(
            data_source_id=source.id,
            entity_type="RESULTS",
            batch_id=batch_id,
            status=BatchStatus.COMPLETED,
            records_imported=imported_count,
            records_failed=0,
            checksum_hash=archive_meta["checksum_sha256"],
            source_url=archive_meta["source_url"],
            payload_path=archive_meta["payload_path"],
        )
        self.session.add(history)
        await self.session.flush()

        return {
            "status": "COMPLETED",
            "batch_id": batch_id,
            "records_imported": imported_count,
            "conflicts_detected": len(self.conflict_detector.conflicts),
        }

    async def ingest_squad(self, season_code: str = "2026–27") -> Dict[str, Any]:
        """Ingests official Chennaiyin FC squad from chennaiyinfc.com."""
        sources = await self.ensure_data_sources_registered()
        source = sources["CHENNAIYIN_FC_OFFICIAL"]
        comp, season = await self.ensure_competition_and_season(season_code)

        batch_id = f"batch-squad-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        extractor = ChennaiyinFCOfficialExtractor(mock_mode=self.mock_mode)

        # 1. Extraction
        raw_data = await extractor.extract_squad(season_code=season_code)

        # 2. Raw Archive Storage
        archive_meta = self.archive.archive_payload(
            source_code=source.code,
            entity_type="SQUAD",
            batch_id=batch_id,
            content=raw_data,
            source_url=raw_data.get("source_url"),
        )

        players_list = raw_data.get("players", [])
        club_dict = FootballNormalizer.resolve_team(raw_data.get("club_name", "Chennaiyin FC"))
        team = await self.ensure_team_and_venue(club_dict)

        # Pandera validation
        if players_list:
            df_rows = [
                {
                    "first_name": p["first_name"],
                    "last_name": p["last_name"],
                    "jersey_number": p.get("jersey_number"),
                    "position": p.get("position"),
                    "nationality": p.get("nationality", "India"),
                }
                for p in players_list
            ]
            SquadDataFrameSchema.validate(pd.DataFrame(df_rows))

        imported_count = 0
        for p in players_list:
            rec = IngestedPlayerRecord.model_validate(p)
            slug = FootballNormalizer.normalize_slug(f"{rec.first_name}-{rec.last_name}")
            pos_enum = FootballNormalizer.normalize_position(rec.position)
            dob = date.fromisoformat(p["date_of_birth"]) if p.get("date_of_birth") else None

            # 1. Decoupled Player Identity
            p_stmt = select(Player).where(Player.slug == slug)
            player_entity = (await self.session.execute(p_stmt)).scalars().first()

            if not player_entity:
                player_entity = Player(
                    slug=slug,
                    first_name=rec.first_name,
                    last_name=rec.last_name,
                    known_name=rec.known_name or f"{rec.first_name} {rec.last_name}",
                    date_of_birth=dob,
                    nationality=rec.nationality,
                    primary_position=pos_enum,
                )
                self.session.add(player_entity)
                await self.session.flush()

            # 2. Squad Registration for 2026-27 Season
            reg_stmt = select(SquadRegistration).where(
                SquadRegistration.player_id == player_entity.id,
                SquadRegistration.team_id == team.id,
                SquadRegistration.season_id == season.id,
            )
            squad_reg = (await self.session.execute(reg_stmt)).scalars().first()

            if not squad_reg:
                squad_reg = SquadRegistration(
                    player_id=player_entity.id,
                    team_id=team.id,
                    season_id=season.id,
                    jersey_number=rec.jersey_number,
                    squad_status=SquadStatus(rec.squad_status.upper()),
                    registered_at=date(2026, 8, 1),
                )
                self.session.add(squad_reg)
            else:
                squad_reg.jersey_number = rec.jersey_number
                squad_reg.squad_status = SquadStatus(rec.squad_status.upper())

            imported_count += 1

        history = ImportHistory(
            data_source_id=source.id,
            entity_type="SQUAD",
            batch_id=batch_id,
            status=BatchStatus.COMPLETED,
            records_imported=imported_count,
            records_failed=0,
            checksum_hash=archive_meta["checksum_sha256"],
            source_url=archive_meta["source_url"],
            payload_path=archive_meta["payload_path"],
        )
        self.session.add(history)
        await self.session.flush()

        return {
            "status": "COMPLETED",
            "batch_id": batch_id,
            "records_imported": imported_count,
            "archive_path": archive_meta["payload_path"],
        }
