"""MARINA INTELLIGENCE — Historical Match Lineups & Substitutions Ingestion Service.

Imports verified Chennaiyin FC starting lineups, tactical formations, and actual substitutions
for the first 5 completed ISL 2026–27 matches.
Enforces transactional integrity, exact 11-starter validation, and strict non-fabrication.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.common import (
    EventType,
    LineupRole,
    MatchPeriod,
    MatchStatus,
    PlayerPosition,
    ProviderType,
    VerificationStatus,
)
from marina.models.match import Lineup, Match, MatchEvent, MatchLineup, MatchSubstitute
from marina.models.player import Player
from marina.models.provenance import DataSource
from marina.models.statistics import PlayerMatchStatistic
from marina.models.team import Team

logger = logging.getLogger(__name__)

# Official 5 completed matches lineup specifications
HISTORICAL_LINEUP_SPECS = [
    {
        "match_number": 1,
        "fixture_code": "FCG_vs_CFC",
        "opponent": "FC Goa",
        "is_home": False,
        "match_date": "2026-10-10",
        "formation": "4-3-3",
        "source": "Official ISL match centre (194635) · 365scores",
        "starting_xi": [
            {"name": "Mohammad Nawaz", "position": PlayerPosition.GK, "jersey_number": 13, "is_captain": True, "sub_out_minute": None},
            {"name": "Muhammed Saheef", "position": PlayerPosition.LB, "jersey_number": 5, "is_captain": False, "sub_out_minute": None},
            {"name": "Emmanuel Imanishimwe", "position": PlayerPosition.LB, "jersey_number": 2, "is_captain": False, "sub_out_minute": None},
            {"name": "Nuno Reis", "position": PlayerPosition.CB, "jersey_number": 4, "is_captain": False, "sub_out_minute": None},
            {"name": "Namgyal Bhutia", "position": PlayerPosition.RB, "jersey_number": 27, "is_captain": False, "sub_out_minute": 86},
            {"name": "Ayush Dev Chhetri", "position": PlayerPosition.DM, "jersey_number": 14, "is_captain": False, "sub_out_minute": None},
            {"name": "Glan Martins", "position": PlayerPosition.DM, "jersey_number": 25, "is_captain": False, "sub_out_minute": 38},
            {"name": "Nikola Stojanović", "position": PlayerPosition.CM, "jersey_number": 8, "is_captain": False, "sub_out_minute": 60},
            {"name": "Brison Fernandes", "position": PlayerPosition.LW, "jersey_number": 42, "is_captain": False, "sub_out_minute": 60},
            {"name": "Ramon Tanque", "position": PlayerPosition.CF, "jersey_number": 7, "is_captain": False, "sub_out_minute": None},
            {"name": "Irfan Yadwad", "position": PlayerPosition.CF, "jersey_number": 24, "is_captain": False, "sub_out_minute": 86},
        ],
        "substitutions": [
            {"minute": 38, "period": MatchPeriod.FIRST_HALF, "player_in": "Lalhriatpuia Chawngthu", "player_out": "Glan Martins", "position": PlayerPosition.CM, "jersey_number": 17},
            {"minute": 60, "period": MatchPeriod.SECOND_HALF, "player_in": "Bryce Miranda", "player_out": "Brison Fernandes", "position": PlayerPosition.LW, "jersey_number": 11},
            {"minute": 60, "period": MatchPeriod.SECOND_HALF, "player_in": "Madih Talal", "player_out": "Nikola Stojanović", "position": PlayerPosition.AM, "jersey_number": 10},
            {"minute": 86, "period": MatchPeriod.SECOND_HALF, "player_in": "PC Laldinpuia", "player_out": "Namgyal Bhutia", "position": PlayerPosition.CB, "jersey_number": 3},
            {"minute": 86, "period": MatchPeriod.SECOND_HALF, "player_in": "Nitishkumar Meitei Yengkhom", "player_out": "Irfan Yadwad", "position": PlayerPosition.CM, "jersey_number": 43},
        ],
        "additional_events": [],
    },
    {
        "match_number": 2,
        "fixture_code": "BFC_vs_CFC",
        "opponent": "Bengaluru FC",
        "is_home": False,
        "match_date": "2026-10-17",
        "formation": "4-4-2",
        "source": "Official ISL match centre (194642) · 365scores",
        "starting_xi": [
            {"name": "Mohammad Nawaz", "position": PlayerPosition.GK, "jersey_number": 13, "is_captain": True, "sub_out_minute": None},
            {"name": "Muhammed Saheef", "position": PlayerPosition.LB, "jersey_number": 5, "is_captain": False, "sub_out_minute": None},
            {"name": "Emmanuel Imanishimwe", "position": PlayerPosition.LB, "jersey_number": 2, "is_captain": False, "sub_out_minute": None},
            {"name": "Nuno Reis", "position": PlayerPosition.CB, "jersey_number": 4, "is_captain": False, "sub_out_minute": None},
            {"name": "Namgyal Bhutia", "position": PlayerPosition.RB, "jersey_number": 27, "is_captain": False, "sub_out_minute": 67},
            {"name": "Ayush Dev Chhetri", "position": PlayerPosition.DM, "jersey_number": 14, "is_captain": False, "sub_out_minute": 83},
            {"name": "Lalhriatpuia Chawngthu", "position": PlayerPosition.CM, "jersey_number": 17, "is_captain": False, "sub_out_minute": 83},
            {"name": "Prakadeswaran S", "position": PlayerPosition.RW, "jersey_number": 52, "is_captain": False, "sub_out_minute": 61},
            {"name": "Madih Talal", "position": PlayerPosition.AM, "jersey_number": 10, "is_captain": False, "sub_out_minute": None},
            {"name": "Irfan Yadwad", "position": PlayerPosition.CF, "jersey_number": 24, "is_captain": False, "sub_out_minute": 67},
            {"name": "Ramon Tanque", "position": PlayerPosition.CF, "jersey_number": 7, "is_captain": False, "sub_out_minute": None},
        ],
        "substitutions": [
            {"minute": 61, "period": MatchPeriod.SECOND_HALF, "player_in": "Brison Fernandes", "player_out": "Prakadeswaran S", "position": PlayerPosition.LW, "jersey_number": 42},
            {"minute": 67, "period": MatchPeriod.SECOND_HALF, "player_in": "Bryce Miranda", "player_out": "Irfan Yadwad", "position": PlayerPosition.LW, "jersey_number": 11},
            {"minute": 67, "period": MatchPeriod.SECOND_HALF, "player_in": "PC Laldinpuia", "player_out": "Namgyal Bhutia", "position": PlayerPosition.CB, "jersey_number": 3},
            {"minute": 83, "period": MatchPeriod.SECOND_HALF, "player_in": "Yumkhaibam Jiteshwor Singh", "player_out": "Lalhriatpuia Chawngthu", "position": PlayerPosition.DM, "jersey_number": 37},
            {"minute": 83, "period": MatchPeriod.SECOND_HALF, "player_in": "Shubham Rawat", "player_out": "Ayush Dev Chhetri", "position": PlayerPosition.CF, "jersey_number": 16},
        ],
        "additional_events": [],
    },
    {
        "match_number": 3,
        "fixture_code": "MBSG_vs_CFC",
        "opponent": "Mohun Bagan SG",
        "is_home": False,
        "match_date": "2026-10-26",
        "formation": "4-2-3-1",
        "source": "Official ISL match centre (194650) · Pitchlabstats",
        "starting_xi": [
            {"name": "Mohammad Nawaz", "position": PlayerPosition.GK, "jersey_number": 13, "is_captain": True, "sub_out_minute": None},
            {"name": "Namgyal Bhutia", "position": PlayerPosition.RB, "jersey_number": 27, "is_captain": False, "sub_out_minute": 89},
            {"name": "PC Laldinpuia", "position": PlayerPosition.CB, "jersey_number": 3, "is_captain": False, "sub_out_minute": None},
            {"name": "Emmanuel Imanishimwe", "position": PlayerPosition.LB, "jersey_number": 2, "is_captain": False, "sub_out_minute": None},
            {"name": "Muhammed Saheef", "position": PlayerPosition.LB, "jersey_number": 5, "is_captain": False, "sub_out_minute": None},
            {"name": "Irfan Yadwad", "position": PlayerPosition.CF, "jersey_number": 24, "is_captain": False, "sub_out_minute": 73},
            {"name": "Nikola Stojanović", "position": PlayerPosition.CM, "jersey_number": 8, "is_captain": False, "sub_out_minute": 89},
            {"name": "Ayush Dev Chhetri", "position": PlayerPosition.DM, "jersey_number": 14, "is_captain": False, "sub_out_minute": 73},
            {"name": "Brison Fernandes", "position": PlayerPosition.LW, "jersey_number": 42, "is_captain": False, "sub_out_minute": 62},
            {"name": "Madih Talal", "position": PlayerPosition.AM, "jersey_number": 10, "is_captain": False, "sub_out_minute": None},
            {"name": "Ramon Tanque", "position": PlayerPosition.CF, "jersey_number": 7, "is_captain": False, "sub_out_minute": None},
        ],
        "substitutions": [
            {"minute": 62, "period": MatchPeriod.SECOND_HALF, "player_in": "Bryce Miranda", "player_out": "Brison Fernandes", "position": PlayerPosition.LW, "jersey_number": 11},
            {"minute": 73, "period": MatchPeriod.SECOND_HALF, "player_in": "Lalhriatpuia Chawngthu", "player_out": "Ayush Dev Chhetri", "position": PlayerPosition.CM, "jersey_number": 17},
            {"minute": 73, "period": MatchPeriod.SECOND_HALF, "player_in": "Prakadeswaran S", "player_out": "Irfan Yadwad", "position": PlayerPosition.RW, "jersey_number": 52},
            {"minute": 89, "period": MatchPeriod.SECOND_HALF, "player_in": "Dippendu Biswas", "player_out": "Namgyal Bhutia", "position": PlayerPosition.CB, "jersey_number": 32},
            {"minute": 89, "period": MatchPeriod.SECOND_HALF, "player_in": "Yumkhaibam Jiteshwor Singh", "player_out": "Nikola Stojanović", "position": PlayerPosition.DM, "jersey_number": 37},
        ],
        "additional_events": [],
    },
    {
        "match_number": 4,
        "fixture_code": "CFC_vs_KBFC",
        "opponent": "Kerala Blasters FC",
        "is_home": True,
        "match_date": "2026-10-31",
        "formation": "4-2-3-1",
        "source": "Official ISL match centre (194653) · badb.info",
        "starting_xi": [
            {"name": "Mohammad Nawaz", "position": PlayerPosition.GK, "jersey_number": 13, "is_captain": True, "sub_out_minute": None},
            {"name": "Namgyal Bhutia", "position": PlayerPosition.RB, "jersey_number": 27, "is_captain": False, "sub_out_minute": 87},
            {"name": "PC Laldinpuia", "position": PlayerPosition.CB, "jersey_number": 3, "is_captain": False, "sub_out_minute": None},
            {"name": "Emmanuel Imanishimwe", "position": PlayerPosition.LB, "jersey_number": 2, "is_captain": False, "sub_out_minute": None},
            {"name": "Muhammed Saheef", "position": PlayerPosition.LB, "jersey_number": 5, "is_captain": False, "sub_out_minute": None},
            {"name": "Nikola Stojanović", "position": PlayerPosition.CM, "jersey_number": 8, "is_captain": False, "sub_out_minute": None},
            {"name": "Irfan Yadwad", "position": PlayerPosition.CF, "jersey_number": 24, "is_captain": False, "sub_out_minute": None},
            {"name": "Ayush Dev Chhetri", "position": PlayerPosition.DM, "jersey_number": 14, "is_captain": False, "sub_out_minute": 56},
            {"name": "Brison Fernandes", "position": PlayerPosition.LW, "jersey_number": 42, "is_captain": False, "sub_out_minute": 65},
            {"name": "Ramon Tanque", "position": PlayerPosition.CF, "jersey_number": 7, "is_captain": False, "sub_out_minute": 87},
            {"name": "Madih Talal", "position": PlayerPosition.AM, "jersey_number": 10, "is_captain": False, "sub_out_minute": None},
        ],
        "substitutions": [
            {"minute": 56, "period": MatchPeriod.SECOND_HALF, "player_in": "Lalhriatpuia Chawngthu", "player_out": "Ayush Dev Chhetri", "position": PlayerPosition.CM, "jersey_number": 17},
            {"minute": 65, "period": MatchPeriod.SECOND_HALF, "player_in": "Prakadeswaran S", "player_out": "Brison Fernandes", "position": PlayerPosition.RW, "jersey_number": 52},
            {"minute": 87, "period": MatchPeriod.SECOND_HALF, "player_in": "Dippendu Biswas", "player_out": "Namgyal Bhutia", "position": PlayerPosition.CB, "jersey_number": 32},
            {"minute": 87, "period": MatchPeriod.SECOND_HALF, "player_in": "Bryce Miranda", "player_out": "Ramon Tanque", "position": PlayerPosition.LW, "jersey_number": 11},
        ],
        "additional_events": [
            {
                "minute": 88,
                "stoppage_minute": None,
                "period": MatchPeriod.SECOND_HALF,
                "event_type": EventType.YELLOW_CARD,
                "player_name": "Emmanuel Imanishimwe",
                "description": "Yellow card: Emmanuel Imanishimwe (reckless challenge)",
            },
            {
                "minute": 90,
                "stoppage_minute": 3,
                "period": MatchPeriod.SECOND_HALF,
                "event_type": EventType.SECOND_YELLOW,
                "player_name": "Emmanuel Imanishimwe",
                "description": "Second yellow card: Emmanuel Imanishimwe",
            },
            {
                "minute": 90,
                "stoppage_minute": 3,
                "period": MatchPeriod.SECOND_HALF,
                "event_type": EventType.RED_CARD,
                "player_name": "Emmanuel Imanishimwe",
                "description": "Red card dismissal: Emmanuel Imanishimwe (second yellow)",
            },
        ],
    },
    {
        "match_number": 5,
        "fixture_code": "CFC_vs_EBFC",
        "opponent": "East Bengal FC",
        "is_home": True,
        "match_date": "2026-11-07",
        "formation": "4-2-3-1",
        "source": "Official ISL match centre (194661) · Pitchlabstats",
        "starting_xi": [
            {"name": "Mohammad Nawaz", "position": PlayerPosition.GK, "jersey_number": 13, "is_captain": True, "sub_out_minute": None},
            {"name": "Namgyal Bhutia", "position": PlayerPosition.RB, "jersey_number": 27, "is_captain": False, "sub_out_minute": None},
            {"name": "Nuno Reis", "position": PlayerPosition.CB, "jersey_number": 4, "is_captain": False, "sub_out_minute": None},
            {"name": "PC Laldinpuia", "position": PlayerPosition.CB, "jersey_number": 3, "is_captain": False, "sub_out_minute": None},
            {"name": "Muhammed Saheef", "position": PlayerPosition.LB, "jersey_number": 5, "is_captain": False, "sub_out_minute": None},
            {"name": "Nikola Stojanović", "position": PlayerPosition.CM, "jersey_number": 8, "is_captain": False, "sub_out_minute": 81},
            {"name": "Ayush Dev Chhetri", "position": PlayerPosition.DM, "jersey_number": 14, "is_captain": False, "sub_out_minute": 81},
            {"name": "Irfan Yadwad", "position": PlayerPosition.CF, "jersey_number": 24, "is_captain": False, "sub_out_minute": None},
            {"name": "Madih Talal", "position": PlayerPosition.AM, "jersey_number": 10, "is_captain": False, "sub_out_minute": 36},
            {"name": "Brison Fernandes", "position": PlayerPosition.LW, "jersey_number": 42, "is_captain": False, "sub_out_minute": 56},
            {"name": "Ramon Tanque", "position": PlayerPosition.CF, "jersey_number": 7, "is_captain": False, "sub_out_minute": 81},
        ],
        "substitutions": [
            {"minute": 36, "period": MatchPeriod.FIRST_HALF, "player_in": "Lalhriatpuia Chawngthu", "player_out": "Madih Talal", "position": PlayerPosition.CM, "jersey_number": 17},
            {"minute": 56, "period": MatchPeriod.SECOND_HALF, "player_in": "Bryce Miranda", "player_out": "Brison Fernandes", "position": PlayerPosition.LW, "jersey_number": 11},
            {"minute": 81, "period": MatchPeriod.SECOND_HALF, "player_in": "Glan Martins", "player_out": "Ayush Dev Chhetri", "position": PlayerPosition.DM, "jersey_number": 25},
            {"minute": 81, "period": MatchPeriod.SECOND_HALF, "player_in": "Prakadeswaran S", "player_out": "Ramon Tanque", "position": PlayerPosition.RW, "jersey_number": 52},
            {"minute": 81, "period": MatchPeriod.SECOND_HALF, "player_in": "Yumkhaibam Jiteshwor Singh", "player_out": "Nikola Stojanović", "position": PlayerPosition.DM, "jersey_number": 37},
        ],
        "additional_events": [],
    },
]


class LineupImportService:
    """Service for transactionally importing and verifying historical match lineups."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _resolve_player_map(self) -> Dict[str, Player]:
        """Resolves names to Player model instances from DB."""
        stmt = select(Player)
        res = await self.db.execute(stmt)
        players = res.scalars().all()

        player_map: Dict[str, Player] = {}
        for p in players:
            full_name = f"{p.first_name} {p.last_name}".strip()
            player_map[full_name.lower()] = p
            if p.known_name:
                player_map[p.known_name.lower()] = p

        # Specialized alias mapping
        aliases = {
            "nuno reis": "nuno rice",
            "nikola stojanović": "nikola stojanovic",
            "nikola stojanovic": "nikola stojanovic",
            "yumkhaibam jiteshwor singh": "jiteshwor singh",
            "jiteshwor singh": "jiteshwor singh",
            "pc laldinpuia": "pc laldinpuia",
            "prakadeswaran s": "prakadeswaran s",
            "nitishkumar meitei yengkhom": "nitishkumar meitei yengkhom",
        }

        resolved: Dict[str, Player] = {}
        for canonical_name, target in aliases.items():
            if target in player_map:
                resolved[canonical_name] = player_map[target]

        # Merge
        for k, v in player_map.items():
            resolved[k] = v

        return resolved

    def _find_player(self, name: str, player_map: Dict[str, Player]) -> Optional[Player]:
        key = name.strip().lower()
        if key in player_map:
            return player_map[key]
        for p_name, p in player_map.items():
            if key in p_name or p_name in key:
                return p
        return None

    async def validate_spec(
        self, player_map: Dict[str, Player]
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Pre-validates all 5 matches before database mutations.
        Returns (is_valid, errors, validation_summary).
        """
        errors: List[str] = []
        summary: Dict[str, Any] = {
            "matches_checked": len(HISTORICAL_LINEUP_SPECS),
            "starting_xi_counts": {},
            "substitution_counts": {},
            "player_matching_failures": [],
            "duplicate_records_detected": 0,
            "missing_matchday_bench": (
                "Official match centres published only active participating substitutes. "
                "Unused bench rosters remain strictly NULL without synthetic fabrication."
            ),
        }

        # Check Chennaiyin FC team
        cfc_stmt = select(Team).where(Team.slug == "chennaiyin-fc")
        cfc_res = await self.db.execute(cfc_stmt)
        cfc = cfc_res.scalar_one_or_none()
        if not cfc:
            errors.append("Chennaiyin FC team record not found in database.")

        for spec in HISTORICAL_LINEUP_SPECS:
            mw = spec["match_number"]
            # 1. Check starting XI count
            s_count = len(spec["starting_xi"])
            summary["starting_xi_counts"][f"Match #{mw}"] = s_count
            if s_count != 11:
                errors.append(f"Match #{mw} has {s_count} starters; exactly 11 required.")

            # 2. Check starting XI player mapping
            starters_in_match = set()
            for s in spec["starting_xi"]:
                p = self._find_player(s["name"], player_map)
                if not p:
                    errors.append(f"Match #{mw} starter '{s['name']}' failed to map to a valid Player ID.")
                    summary["player_matching_failures"].append(f"Match #{mw}: Starter '{s['name']}'")
                else:
                    if p.id in starters_in_match:
                        errors.append(f"Match #{mw} duplicate starter detected: '{s['name']}' (ID: {p.id}).")
                        summary["duplicate_records_detected"] += 1
                    starters_in_match.add(p.id)

            # 3. Check substitutions
            sub_count = len(spec["substitutions"])
            summary["substitution_counts"][f"Match #{mw}"] = sub_count

            current_pitch_players = set(starters_in_match)
            for sub in spec["substitutions"]:
                p_in = self._find_player(sub["player_in"], player_map)
                p_out = self._find_player(sub["player_out"], player_map)

                if not p_in:
                    errors.append(f"Match #{mw} sub-in '{sub['player_in']}' failed to map to Player ID.")
                    summary["player_matching_failures"].append(f"Match #{mw}: Sub-in '{sub['player_in']}'")
                if not p_out:
                    errors.append(f"Match #{mw} sub-out '{sub['player_out']}' failed to map to Player ID.")
                    summary["player_matching_failures"].append(f"Match #{mw}: Sub-out '{sub['player_out']}'")

                if p_out and p_out.id not in current_pitch_players:
                    errors.append(
                        f"Match #{mw} sub-out '{sub['player_out']}' is not currently on the pitch at minute {sub['minute']}."
                    )
                if p_in and p_in.id in current_pitch_players:
                    errors.append(
                        f"Match #{mw} sub-in '{sub['player_in']}' is already on the pitch at minute {sub['minute']}."
                    )

                if p_out:
                    current_pitch_players.discard(p_out.id)
                if p_in:
                    current_pitch_players.add(p_in.id)

            # 4. Check additional events (cards/dismissals)
            for ev in spec.get("additional_events", []):
                p_ev = self._find_player(ev["player_name"], player_map)
                if not p_ev:
                    errors.append(f"Match #{mw} event player '{ev['player_name']}' failed to map.")

        is_valid = len(errors) == 0
        return is_valid, errors, summary

    async def import_historical_lineups(self) -> Dict[str, Any]:
        """Executes transactional import of historical lineups for all 5 matches.
        Rolls back if any match or player validation fails.
        """
        player_map = await self._resolve_player_map()
        is_valid, errors, summary = await self.validate_spec(player_map)

        if not is_valid:
            logger.error("Pre-validation failed for historical lineups: %s", errors)
            raise ValueError(f"Lineup import validation failed with {len(errors)} error(s): {errors}")

        cfc_stmt = select(Team).where(Team.slug == "chennaiyin-fc")
        cfc_res = await self.db.execute(cfc_stmt)
        cfc = cfc_res.scalar_one()

        ds_stmt = select(DataSource).where(DataSource.name == "Indian Super League Official Match Center")
        ds_res = await self.db.execute(ds_stmt)
        ds = ds_res.scalar_one_or_none()
        if not ds:
            ds_any_stmt = select(DataSource).limit(1)
            ds = (await self.db.execute(ds_any_stmt)).scalar_one_or_none()
            if not ds:
                ds = DataSource(
                    id=uuid.uuid4(),
                    name="Indian Super League Official Match Center",
                    provider_type=ProviderType.OFFICIAL_LEAGUE,
                    is_active=True,
                )
                self.db.add(ds)
                await self.db.flush()

        imported_match_ids: List[str] = []
        validation_results: List[Dict[str, Any]] = []

        # Find the 5 completed matches
        matches_stmt = (
            select(Match)
            .where(Match.match_status == MatchStatus.FINISHED)
            .order_by(Match.scheduled_kickoff.asc())
        )
        matches_res = await self.db.execute(matches_stmt)
        completed_matches = matches_res.scalars().all()

        if len(completed_matches) < 5:
            raise ValueError(
                f"Expected at least 5 completed matches in database, found {len(completed_matches)}."
            )

        match_by_mw = {m.match_number: m for m in completed_matches if m.match_number in [1, 2, 3, 4, 5]}

        # Atomic transaction loop
        for spec in HISTORICAL_LINEUP_SPECS:
            mw = spec["match_number"]
            match = match_by_mw.get(mw)
            if not match:
                raise ValueError(f"Match record for Matchweek #{mw} not found in database.")

            match_id = match.id
            imported_match_ids.append(str(match_id))

            # 1. Clean existing lineup, substitute, and substitution events for CFC to allow idempotent import
            await self.db.execute(delete(MatchLineup).where(MatchLineup.match_id == match_id, MatchLineup.team_id == cfc.id))
            await self.db.execute(delete(MatchSubstitute).where(MatchSubstitute.match_id == match_id, MatchSubstitute.team_id == cfc.id))
            await self.db.execute(delete(Lineup).where(Lineup.match_id == match_id, Lineup.team_id == cfc.id))
            await self.db.execute(
                delete(MatchEvent).where(
                    MatchEvent.match_id == match_id,
                    MatchEvent.team_id == cfc.id,
                    MatchEvent.event_type == EventType.SUBSTITUTION,
                )
            )

            # Clean card events if Match 4 to re-insert verified cards cleanly
            if mw == 4:
                await self.db.execute(
                    delete(MatchEvent).where(
                        MatchEvent.match_id == match_id,
                        MatchEvent.team_id == cfc.id,
                        MatchEvent.event_type.in_([EventType.YELLOW_CARD, EventType.SECOND_YELLOW, EventType.RED_CARD]),
                    )
                )

            # Map substitution minute info
            sub_outs: Dict[uuid.UUID, int] = {}
            for sub in spec["substitutions"]:
                p_out = self._find_player(sub["player_out"], player_map)
                if p_out:
                    sub_outs[p_out.id] = sub["minute"]

            # 2. Insert 11 Starting XI into match_lineups and lineups
            for s in spec["starting_xi"]:
                p = self._find_player(s["name"], player_map)
                if not p:
                    raise ValueError(f"Player {s['name']} not found")
                sub_out_min = sub_outs.get(p.id, s.get("sub_out_minute"))
                minutes_played = sub_out_min if sub_out_min is not None else 90

                # MatchLineup (Dedicated Starting XI table)
                ml = MatchLineup(
                    id=uuid.uuid4(),
                    match_id=match_id,
                    team_id=cfc.id,
                    player_id=p.id,
                    lineup_role=LineupRole.STARTER,
                    position=s["position"],
                    tactical_formation=spec["formation"],
                    jersey_number=s["jersey_number"],
                    is_captain=s["is_captain"],
                    minutes_played=minutes_played,
                    sub_out_minute=sub_out_min,
                    verification_status=VerificationStatus.VERIFIED,
                    is_verified=True,
                )
                self.db.add(ml)

                # Lineup (Standard backwards-compatible table)
                lp = Lineup(
                    id=uuid.uuid4(),
                    match_id=match_id,
                    team_id=cfc.id,
                    player_id=p.id,
                    lineup_role=LineupRole.STARTER,
                    position=s["position"],
                    tactical_formation=spec["formation"],
                    jersey_number=s["jersey_number"],
                    is_captain=s["is_captain"],
                    minutes_played=minutes_played,
                    is_substitute_in=False,
                    sub_in_minute=None,
                    sub_out_minute=sub_out_min,
                )
                self.db.add(lp)

                # Upsert PlayerMatchStatistic for starter appearance
                stat_stmt = select(PlayerMatchStatistic).where(
                    PlayerMatchStatistic.match_id == match_id,
                    PlayerMatchStatistic.player_id == p.id,
                )
                stat_res = await self.db.execute(stat_stmt)
                stat_obj = stat_res.scalar_one_or_none()
                if not stat_obj:
                    stat_obj = PlayerMatchStatistic(
                        id=uuid.uuid4(),
                        match_id=match_id,
                        player_id=p.id,
                        team_id=cfc.id,
                        data_source_id=ds.id,
                        minutes_played=minutes_played,
                        is_verified=True,
                        verification_status=VerificationStatus.VERIFIED,
                    )
                    self.db.add(stat_obj)
                else:
                    stat_obj.minutes_played = minutes_played

            # 3. Insert Actual Substitutions into match_substitutes, lineups, and match_events
            for sub in spec["substitutions"]:
                p_in = self._find_player(sub["player_in"], player_map)
                p_out = self._find_player(sub["player_out"], player_map)
                if not p_in or not p_out:
                    raise ValueError(f"Substitution players not found: {sub['player_in']}, {sub['player_out']}")
                sub_min = sub["minute"]
                min_played = 90 - sub_min

                # MatchSubstitute (Dedicated substitutes table)
                ms = MatchSubstitute(
                    id=uuid.uuid4(),
                    match_id=match_id,
                    team_id=cfc.id,
                    player_id=p_in.id,
                    jersey_number=sub["jersey_number"],
                    position=sub["position"],
                    is_used=True,
                    sub_in_minute=sub_min,
                    sub_out_minute=None,
                    replaced_player_id=p_out.id,
                    minutes_played=min_played,
                    is_verified=True,
                    verification_status=VerificationStatus.VERIFIED,
                )
                self.db.add(ms)

                # Lineup (Substitute Appearance row)
                lp_sub = Lineup(
                    id=uuid.uuid4(),
                    match_id=match_id,
                    team_id=cfc.id,
                    player_id=p_in.id,
                    lineup_role=LineupRole.BENCH,
                    position=sub["position"],
                    tactical_formation=spec["formation"],
                    jersey_number=sub["jersey_number"],
                    is_captain=False,
                    minutes_played=min_played,
                    is_substitute_in=True,
                    sub_in_minute=sub_min,
                    sub_out_minute=None,
                )
                self.db.add(lp_sub)

                # MatchEvent for Substitution
                raw_meta = {
                    "event_type": "substitution",
                    "minute": sub_min,
                    "player_in": sub["player_in"],
                    "player_out": sub["player_out"],
                    "team": "Chennaiyin FC",
                    "source_verified": True,
                }
                ev = MatchEvent(
                    id=uuid.uuid4(),
                    match_id=match_id,
                    team_id=cfc.id,
                    primary_player_id=p_in.id,
                    secondary_player_id=p_out.id,
                    data_source_id=ds.id,
                    event_type=EventType.SUBSTITUTION,
                    period=sub["period"],
                    minute=sub_min,
                    description=f"Substitution: {sub['player_in']} for {sub['player_out']}",
                    verification_status=VerificationStatus.VERIFIED,
                    is_verified=True,
                    raw_metadata=json.dumps(raw_meta),
                )
                self.db.add(ev)

                # Upsert PlayerMatchStatistic for substitute appearance
                sub_stat_stmt = select(PlayerMatchStatistic).where(
                    PlayerMatchStatistic.match_id == match_id,
                    PlayerMatchStatistic.player_id == p_in.id,
                )
                sub_stat_res = await self.db.execute(sub_stat_stmt)
                sub_stat_obj = sub_stat_res.scalar_one_or_none()
                if not sub_stat_obj:
                    sub_stat_obj = PlayerMatchStatistic(
                        id=uuid.uuid4(),
                        match_id=match_id,
                        player_id=p_in.id,
                        team_id=cfc.id,
                        data_source_id=ds.id,
                        minutes_played=min_played,
                        is_verified=True,
                        verification_status=VerificationStatus.VERIFIED,
                    )
                    self.db.add(sub_stat_obj)
                else:
                    sub_stat_obj.minutes_played = min_played

            # 4. Insert Additional Verified Events (e.g. Imanishimwe cards in Match 4)
            for ev_data in spec.get("additional_events", []):
                p_ev = self._find_player(ev_data["player_name"], player_map)
                if not p_ev:
                    raise ValueError(f"Event player {ev_data['player_name']} not found")
                card_ev = MatchEvent(
                    id=uuid.uuid4(),
                    match_id=match_id,
                    team_id=cfc.id,
                    primary_player_id=p_ev.id,
                    secondary_player_id=None,
                    data_source_id=ds.id,
                    event_type=ev_data["event_type"],
                    period=ev_data["period"],
                    minute=ev_data["minute"],
                    stoppage_minute=ev_data.get("stoppage_minute"),
                    description=ev_data["description"],
                    verification_status=VerificationStatus.VERIFIED,
                    is_verified=True,
                )
                self.db.add(card_ev)

                # Update player match statistics for yellow/red cards
                ev_stat_stmt = select(PlayerMatchStatistic).where(
                    PlayerMatchStatistic.match_id == match_id,
                    PlayerMatchStatistic.player_id == p_ev.id,
                )
                ev_stat_res = await self.db.execute(ev_stat_stmt)
                ev_stat_obj = ev_stat_res.scalar_one_or_none()
                if ev_stat_obj:
                    if ev_data["event_type"] == EventType.YELLOW_CARD:
                        ev_stat_obj.yellow_cards = 1
                    elif ev_data["event_type"] in [EventType.RED_CARD, EventType.SECOND_YELLOW]:
                        ev_stat_obj.red_cards = 1

            validation_results.append({
                "match_number": mw,
                "match_id": str(match_id),
                "opponent": spec["opponent"],
                "starting_xi_count": 11,
                "substitutions_count": len(spec["substitutions"]),
                "formation": spec["formation"],
                "status": "VALIDATED_AND_COMMITTED",
            })

        # Commit all 5 matches in one transaction
        await self.db.commit()

        return {
            "status": "SUCCESS",
            "imported_match_ids": imported_match_ids,
            "starting_xi_counts": summary["starting_xi_counts"],
            "substitution_counts": summary["substitution_counts"],
            "player_id_matching_failures": summary["player_matching_failures"],
            "duplicate_records_detected": summary["duplicate_records_detected"],
            "missing_matchday_bench": summary["missing_matchday_bench"],
            "validation_results": validation_results,
        }
