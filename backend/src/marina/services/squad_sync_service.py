"""Chennaiyin FC Squad Synchronization and Roster Ingestion Service.

Implements:
1. Normalization of market values into INR while retaining original display strings.
2. Robust parsing of dates (DD/MM/YYYY), heights, positions, dual nationalities.
3. Player identity matching by slug, known name, or first/last name with duplicate detection.
4. Preview generation with categorization into new, updated, retained, and leaving players.
5. Transactional synchronization:
   - Preserves historical player identities and match statistics.
   - Deactivates departed players for the active season instead of deleting records.
   - Upserts season-specific team squad memberships and registrations.
   - Logs audit history in squad_import_history.
"""

import csv
import io
import json
import re
import uuid
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from marina.models.common import PlayerPosition, SquadStatus
from marina.models.competition import Season
from marina.models.player import (
    Player,
    SquadImportHistory,
    SquadRegistration,
    TeamSquadMembership,
)
from marina.models.team import Team


def parse_market_value(val: Optional[str]) -> Tuple[Optional[int], Optional[str]]:
    """Normalizes market value strings like '₹1.10 Cr', '₹55 L', '₹27.50 L' into INR integers.
    Retains original display string. Preserves missing/unknown values as None.
    """
    if not val:
        return None, None
    s = val.strip()
    if s in ("—", "-", "", "N/A", "null", "None"):
        return None, None

    clean = s.replace("₹", "").replace(",", "").strip()

    # Crore: 1 Cr = 10,000,000 (10^7)
    cr_match = re.search(r"([\d\.]+)\s*(?:Cr|Crore)", clean, re.IGNORECASE)
    if cr_match:
        try:
            num = float(cr_match.group(1))
            inr = int(round(num * 10_000_000))
            return inr, s
        except ValueError:
            pass

    # Lakh: 1 L = 100,000 (10^5)
    lakh_match = re.search(r"([\d\.]+)\s*(?:L|Lakh|Lac)", clean, re.IGNORECASE)
    if lakh_match:
        try:
            num = float(lakh_match.group(1))
            inr = int(round(num * 100_000))
            return inr, s
        except ValueError:
            pass

    # Plain integer or decimal
    try:
        num = float(clean)
        return int(round(num)), s
    except ValueError:
        return None, s


def parse_height(height_str: Optional[str]) -> Tuple[Optional[float], Optional[int]]:
    """Parses height string like '1.74 m' or '188 cm' into (height_m, height_cm)."""
    if not height_str:
        return None, None
    s = height_str.strip()
    if s in ("—", "-", "", "N/A"):
        return None, None

    m_match = re.search(r"([\d\.]+)\s*m", s, re.IGNORECASE)
    if m_match:
        try:
            h_m = float(m_match.group(1))
            h_cm = int(round(h_m * 100))
            return h_m, h_cm
        except ValueError:
            pass

    cm_match = re.search(r"(\d+)\s*cm", s, re.IGNORECASE)
    if cm_match:
        try:
            h_cm = int(cm_match.group(1))
            h_m = round(h_cm / 100.0, 2)
            return h_m, h_cm
        except ValueError:
            pass

    return None, None


def parse_date_dmy(date_str: Optional[str]) -> Tuple[Optional[date], Optional[int]]:
    """Parses 'DD/MM/YYYY (Age)' or 'DD/MM/YYYY' or 'YYYY-MM-DD' into (date_obj, age)."""
    if not date_str:
        return None, None
    s = str(date_str).strip()
    if s in ("—", "-", "", "N/A"):
        return None, None

    supplied_age = None
    age_match = re.search(r"\((\d+)\)", s)
    if age_match:
        supplied_age = int(age_match.group(1))
        s = re.sub(r"\s*\(\d+\)", "", s).strip()

    parsed_date = None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            parsed_date = datetime.strptime(s, fmt).date()
            break
        except ValueError:
            continue

    calc_age = None
    if parsed_date:
        ref_year = 2026
        calc_age = ref_year - parsed_date.year
        if supplied_age is not None:
            calc_age = supplied_age

    return parsed_date, calc_age


def parse_nationality(nat_str: Optional[str]) -> Tuple[str, Optional[str]]:
    """Splits dual nationality strings like 'Portugal / Switzerland' into primary and secondary."""
    if not nat_str or nat_str.strip() in ("—", "-", ""):
        return "India", None
    parts = [p.strip() for p in nat_str.split("/") if p.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return parts[0], None
    return "India", None


def parse_position(pos_str: Optional[str]) -> Tuple[PlayerPosition, str]:
    """Maps position string to PlayerPosition enum and broad position group (GK, DEF, MID, FWD)."""
    if not pos_str:
        return PlayerPosition.CM, "MID"
    p = pos_str.strip().lower()

    if "goal" in p or p == "gk":
        return PlayerPosition.GK, "GK"
    if "defender" in p or p == "def":
        return PlayerPosition.DEF, "DEF"
    if "centre-back" in p or "center-back" in p or "cb" in p:
        return PlayerPosition.CB, "DEF"
    if "left-back" in p or "lb" in p:
        return PlayerPosition.LB, "DEF"
    if "right-back" in p or "rb" in p:
        return PlayerPosition.RB, "DEF"
    if "defensive mid" in p or "dm" in p:
        return PlayerPosition.DM, "MID"
    if "attacking mid" in p or "am" in p:
        return PlayerPosition.AM, "MID"
    if "central mid" in p or "midfield" in p or "cm" in p:
        return PlayerPosition.CM, "MID"
    if "left wing" in p or p == "lw":
        return PlayerPosition.LW, "FWD"
    if "right wing" in p or p == "rw":
        return PlayerPosition.RW, "FWD"
    if "striker" in p or p == "st":
        return PlayerPosition.ST, "FWD"
    if "centre-forward" in p or "center-forward" in p or "forward" in p or p == "cf":
        return PlayerPosition.CF, "FWD"

    return PlayerPosition.CM, "MID"


def generate_player_slug(name: str) -> str:
    """Generates a url-friendly unique slug from a player's name."""
    clean = re.sub(r"[^a-zA-Z0-9\s-]", "", name).strip().lower()
    return re.sub(r"\s+", "-", clean)


class SquadSyncService:
    """Service to parse, validate, preview, and synchronize Chennaiyin FC squad rosters."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def parse_raw_records(content: Union[str, bytes], format_hint: str = "auto") -> List[Dict[str, Any]]:
        """Parses CSV or JSON file/string content into normalized raw record dictionaries."""
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        text = text.strip()

        if format_hint == "json" or (format_hint == "auto" and text.startswith("[") or text.startswith("{")):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return parsed
                elif isinstance(parsed, dict) and "players" in parsed:
                    return parsed["players"]
            except Exception:
                pass

        # Parse CSV
        reader = csv.DictReader(io.StringIO(text))
        rows = []
        for r in reader:
            normalized_row = {}
            for k, v in r.items():
                if not k:
                    continue
                k_clean = k.strip().lower().replace(" ", "_").replace("#", "squad_number")
                normalized_row[k_clean] = v.strip() if v else None
            rows.append(normalized_row)
        return rows

    def normalize_incoming_player(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Validates and normalizes an incoming raw player record."""
        # Standardize dictionary keys to lowercase stripped
        raw_norm: Dict[str, Any] = {}
        for k, v in raw.items():
            if k is not None:
                k_clean = str(k).strip().lower().replace(" ", "_")
                raw_norm[k_clean] = v

        # Squad number
        sq_val = raw_norm.get("squad_number") or raw_norm.get("#") or raw_norm.get("number") or raw_norm.get("jersey")
        squad_number = int(sq_val) if sq_val is not None and str(sq_val).isdigit() else None

        # Name
        full_name = raw_norm.get("player") or raw_norm.get("player_name") or raw_norm.get("name") or "Unknown Player"
        full_name = full_name.strip()
        parts = full_name.split()
        first_name = parts[0] if parts else "Player"
        last_name = " ".join(parts[1:]) if len(parts) > 1 else parts[0]
        known_name = full_name
        slug = generate_player_slug(full_name)

        # Position
        pos_raw = raw_norm.get("position") or "Midfielder"
        primary_pos, pos_group = parse_position(pos_raw)

        # Date of birth & Age
        dob_raw = raw_norm.get("date_of_birth") or raw_norm.get("date_of_birth_(age)") or raw_norm.get("dob")
        dob, age = parse_date_dmy(dob_raw)

        # Nationality
        nat_raw = raw_norm.get("nationality") or "India"
        pri_nat, sec_nat = parse_nationality(nat_raw)
        is_domestic = (pri_nat == "India")

        # Height
        h_raw = raw_norm.get("height")
        height_m, height_cm = parse_height(h_raw)

        # Foot
        foot_raw = raw_norm.get("preferred_foot") or raw_norm.get("foot")
        preferred_foot = foot_raw.strip().capitalize() if foot_raw and str(foot_raw).strip() not in ("—", "-") else None

        # Joined date
        joined_raw = raw_norm.get("joined_date") or raw_norm.get("joined")
        joined_date, _ = parse_date_dmy(joined_raw)

        # Previous club
        prev_club = raw_norm.get("previous_club") or raw_norm.get("signed_from")
        if prev_club and str(prev_club).strip() in ("—", "-"):
            prev_club = None

        # Contract expiry
        exp_raw = raw_norm.get("contract_expiry") or raw_norm.get("contract_until")
        contract_expiry, _ = parse_date_dmy(exp_raw)

        # Market value
        mv_raw = raw_norm.get("market_value")
        mv_inr, mv_orig = parse_market_value(mv_raw)

        return {
            "squad_number": squad_number,
            "player_name": full_name,
            "first_name": first_name,
            "last_name": last_name,
            "known_name": known_name,
            "slug": slug,
            "position": pos_raw,
            "primary_position": primary_pos.value,
            "pos_group": pos_group,
            "date_of_birth": dob.isoformat() if dob else None,
            "age": age,
            "nationality": pri_nat,
            "secondary_nationality": sec_nat,
            "is_domestic": is_domestic,
            "height_m": height_m,
            "height_cm": height_cm,
            "preferred_foot": preferred_foot,
            "joined_date": joined_date.isoformat() if joined_date else None,
            "previous_club": prev_club,
            "contract_expiry": contract_expiry.isoformat() if contract_expiry else None,
            "market_value_inr": mv_inr,
            "market_value_original": mv_orig,
        }

    async def preview_squad_import(
        self,
        team_id: uuid.UUID,
        season_id: uuid.UUID,
        raw_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Performs pre-synchronization audit, duplicate detection, and delta analysis."""
        batch_id = f"sync-preview-{uuid.uuid4().hex[:8]}"

        # 1. Fetch team & season
        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        season = (await self.session.execute(select(Season).where(Season.id == season_id))).scalars().first()
        if not season:
            raise ValueError(f"Season {season_id} not found.")

        # 2. Fetch all existing players in DB
        all_players: List[Player] = list((await self.session.execute(select(Player))).scalars().all())
        players_by_slug = {p.slug: p for p in all_players}
        players_by_known = {p.known_name.lower(): p for p in all_players if p.known_name}
        players_by_name = {f"{p.first_name} {p.last_name}".lower(): p for p in all_players}

        # 3. Fetch active squad memberships for 2026-27
        mem_stmt = (
            select(TeamSquadMembership)
            .where(
                TeamSquadMembership.team_id == team_id,
                TeamSquadMembership.season_id == season_id,
                TeamSquadMembership.is_active.is_(True),
            )
            .options(selectinload(TeamSquadMembership.player))
        )
        active_memberships = list((await self.session.execute(mem_stmt)).scalars().all())
        active_player_ids = {m.player_id: m for m in active_memberships}

        normalized_incoming: List[Dict[str, Any]] = []
        new_players: List[Dict[str, Any]] = []
        updated_players: List[Dict[str, Any]] = []
        retained_players: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []

        seen_numbers: Dict[int, str] = {}
        seen_names: Dict[str, int] = {}
        missing_fields_summary = {
            "height": 0,
            "preferred_foot": 0,
            "joined_date": 0,
            "previous_club": 0,
            "contract_expiry": 0,
            "market_value": 0,
        }

        matched_existing_player_ids = set()

        for idx, raw in enumerate(raw_records):
            norm = self.normalize_incoming_player(raw)
            normalized_incoming.append(norm)

            # Check duplicate numbers
            sq = norm["squad_number"]
            name = norm["player_name"]
            if sq is not None:
                if sq in seen_numbers:
                    warnings.append({
                        "type": "DUPLICATE_SQUAD_NUMBER",
                        "message": f"Squad number #{sq} is assigned to both '{seen_numbers[sq]}' and '{name}'.",
                        "player": name,
                    })
                seen_numbers[sq] = name

            # Check duplicate names
            if name in seen_names:
                warnings.append({
                    "type": "DUPLICATE_NAME",
                    "message": f"Player name '{name}' appears more than once in the incoming dataset.",
                    "player": name,
                })
            seen_names[name] = idx

            # Track missing fields
            if norm["height_m"] is None:
                missing_fields_summary["height"] += 1
            if norm["preferred_foot"] is None:
                missing_fields_summary["preferred_foot"] += 1
            if norm["joined_date"] is None:
                missing_fields_summary["joined_date"] += 1
            if norm["previous_club"] is None:
                missing_fields_summary["previous_club"] += 1
            if norm["contract_expiry"] is None:
                missing_fields_summary["contract_expiry"] += 1
            if norm["market_value_inr"] is None:
                missing_fields_summary["market_value"] += 1

            # Match against DB
            matched_player: Optional[Player] = (
                players_by_slug.get(norm["slug"])
                or players_by_known.get(name.lower())
                or players_by_name.get(name.lower())
            )

            if matched_player:
                matched_existing_player_ids.add(matched_player.id)
                norm["existing_player_id"] = str(matched_player.id)
                updated_players.append(norm)

                if matched_player.id in active_player_ids:
                    retained_players.append(norm)
            else:
                norm["existing_player_id"] = None
                new_players.append(norm)

        # 4. Identify departing players who are currently active in 2026-27 squad but missing from incoming roster
        leaving_players: List[Dict[str, Any]] = []
        for p_id, mem in active_player_ids.items():
            if p_id not in matched_existing_player_ids:
                p = mem.player
                leaving_players.append({
                    "player_id": str(p.id),
                    "name": p.known_name or f"{p.first_name} {p.last_name}",
                    "squad_number": mem.squad_number,
                    "position": mem.position or p.primary_position.value,
                    "nationality": p.nationality,
                    "status": "DEACTIVATING_FROM_2026_27",
                    "historical_records_retained": True,
                })

        return {
            "team_id": str(team.id),
            "season_id": str(season.id),
            "batch_id": batch_id,
            "total_incoming": len(normalized_incoming),
            "new_players": new_players,
            "updated_players": updated_players,
            "leaving_players": leaving_players,
            "retained_players": retained_players,
            "warnings": warnings,
            "missing_fields_summary": missing_fields_summary,
            "requires_confirmation": len(leaving_players) > 0,
        }

    async def synchronize_squad(
        self,
        team_id: uuid.UUID,
        season_id: uuid.UUID,
        incoming_records: List[Dict[str, Any]],
        confirmed: bool = True,
        deactivate_absent: bool = True,
    ) -> Dict[str, Any]:
        """Atomically synchronizes the club's 2026-27 active squad.

        Guarantees:
        1. Fully transactional (rolls back on failure).
        2. Preserves historical player records and match statistics.
        3. Never deletes departed players - deactivates their active season membership.
        4. Logs audit entry in squad_import_history.
        """
        batch_id = f"sync-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        team = (await self.session.execute(select(Team).where(Team.id == team_id))).scalars().first()
        if not team:
            raise ValueError(f"Team {team_id} not found.")

        season = (await self.session.execute(select(Season).where(Season.id == season_id))).scalars().first()
        if not season:
            raise ValueError(f"Season {season_id} not found.")

        # Cache existing players
        all_players: List[Player] = list((await self.session.execute(select(Player))).scalars().all())
        players_by_slug = {p.slug: p for p in all_players}
        players_by_known = {p.known_name.lower(): p for p in all_players if p.known_name}
        players_by_name = {f"{p.first_name} {p.last_name}".lower(): p for p in all_players}

        # Cache existing memberships for this team and season
        mem_stmt = (
            select(TeamSquadMembership)
            .where(
                TeamSquadMembership.team_id == team_id,
                TeamSquadMembership.season_id == season_id,
            )
            .options(selectinload(TeamSquadMembership.player))
        )
        existing_memberships: List[TeamSquadMembership] = list((await self.session.execute(mem_stmt)).scalars().all())
        memberships_by_player_id = {m.player_id: m for m in existing_memberships}

        # Cache squad registrations for backwards compatibility
        reg_stmt = select(SquadRegistration).where(
            SquadRegistration.team_id == team_id,
            SquadRegistration.season_id == season_id,
        )
        existing_regs = list((await self.session.execute(reg_stmt)).scalars().all())
        regs_by_player_id = {r.player_id: r for r in existing_regs}

        new_created_count = 0
        updated_count = 0
        retained_count = 0
        deactivated_count = 0

        active_incoming_player_ids = set()

        for raw in incoming_records:
            norm = self.normalize_incoming_player(raw)
            slug = norm["slug"]
            name = norm["player_name"]

            # Match player
            player = (
                players_by_slug.get(slug)
                or players_by_known.get(name.lower())
                or players_by_name.get(name.lower())
            )

            # Date of birth object
            dob_obj = date.fromisoformat(norm["date_of_birth"]) if norm["date_of_birth"] else None
            joined_obj = date.fromisoformat(norm["joined_date"]) if norm["joined_date"] else None
            expiry_obj = date.fromisoformat(norm["contract_expiry"]) if norm["contract_expiry"] else None
            primary_pos_enum = PlayerPosition(norm["primary_position"])

            if player:
                # Update existing profile
                player.known_name = norm["known_name"]
                player.primary_position = primary_pos_enum
                player.nationality = norm["nationality"]
                player.secondary_nationality = norm["secondary_nationality"]
                if norm["height_m"] is not None:
                    player.height_m = norm["height_m"]
                if norm["height_cm"] is not None:
                    player.height_cm = norm["height_cm"]
                if norm["preferred_foot"]:
                    player.preferred_foot = norm["preferred_foot"]
                if dob_obj:
                    player.date_of_birth = dob_obj
                player.squad_number = norm["squad_number"]
                if joined_obj:
                    player.joined_date = joined_obj
                if expiry_obj:
                    player.contract_expiry = expiry_obj
                if norm["previous_club"]:
                    player.previous_club = norm["previous_club"]
                if norm["market_value_inr"] is not None:
                    player.market_value_inr = norm["market_value_inr"]
                if norm["market_value_original"]:
                    player.market_value_original = norm["market_value_original"]
                player.is_active = True
                player.verified_at = datetime.now(timezone.utc)
                updated_count += 1
            else:
                # Create brand new player
                player = Player(
                    slug=slug,
                    first_name=norm["first_name"],
                    last_name=norm["last_name"],
                    known_name=norm["known_name"],
                    date_of_birth=dob_obj,
                    nationality=norm["nationality"],
                    secondary_nationality=norm["secondary_nationality"],
                    primary_position=primary_pos_enum,
                    height_m=norm["height_m"],
                    height_cm=norm["height_cm"],
                    preferred_foot=norm["preferred_foot"],
                    squad_number=norm["squad_number"],
                    joined_date=joined_obj,
                    previous_club=norm["previous_club"],
                    contract_expiry=expiry_obj,
                    market_value_inr=norm["market_value_inr"],
                    market_value_original=norm["market_value_original"],
                    source_name="Chennaiyin FC Official / Transfermarkt",
                    verified_at=datetime.now(timezone.utc),
                    is_active=True,
                )
                self.session.add(player)
                await self.session.flush()
                players_by_slug[slug] = player
                players_by_known[name.lower()] = player
                new_created_count += 1

            active_incoming_player_ids.add(player.id)

            # Upsert TeamSquadMembership
            membership = memberships_by_player_id.get(player.id)
            if membership:
                membership.squad_number = norm["squad_number"]
                membership.position = norm["position"]
                membership.joined_date = joined_obj
                membership.previous_club = norm["previous_club"]
                membership.contract_expiry = expiry_obj
                membership.market_value_inr = norm["market_value_inr"]
                membership.market_value_original = norm["market_value_original"]
                membership.is_active = True
                retained_count += 1
            else:
                membership = TeamSquadMembership(
                    team_id=team_id,
                    season_id=season_id,
                    player_id=player.id,
                    squad_number=norm["squad_number"],
                    position=norm["position"],
                    joined_date=joined_obj,
                    previous_club=norm["previous_club"],
                    contract_expiry=expiry_obj,
                    market_value_inr=norm["market_value_inr"],
                    market_value_original=norm["market_value_original"],
                    is_active=True,
                )
                self.session.add(membership)
                memberships_by_player_id[player.id] = membership

            # Upsert SquadRegistration (for backwards compatibility with Lineup FKs)
            reg = regs_by_player_id.get(player.id)
            if reg:
                reg.jersey_number = norm["squad_number"]
                reg.is_active = True
                reg.registered_at = joined_obj
            else:
                reg = SquadRegistration(
                    team_id=team_id,
                    season_id=season_id,
                    player_id=player.id,
                    jersey_number=norm["squad_number"],
                    squad_status=SquadStatus.FIRST_TEAM,
                    registered_at=joined_obj,
                    is_active=True,
                )
                self.session.add(reg)
                regs_by_player_id[player.id] = reg

        # Deactivate departed players for 2026-27 season
        if deactivate_absent:
            for m in existing_memberships:
                if m.player_id not in active_incoming_player_ids and m.is_active:
                    m.is_active = False
                    deactivated_count += 1

            for r in existing_regs:
                if r.player_id not in active_incoming_player_ids and r.is_active:
                    r.is_active = False
                    r.deregistered_at = date.today()

        # Audit History Record
        history_record = SquadImportHistory(
            team_id=team_id,
            season_id=season_id,
            batch_id=batch_id,
            source_name="Chennaiyin FC 2026-27 Official Roster",
            total_incoming=len(incoming_records),
            new_players=new_created_count,
            updated_players=updated_count,
            deactivated_players=deactivated_count,
            retained_players=retained_count,
            status="COMPLETED",
            report_summary=json.dumps({
                "batch_id": batch_id,
                "total_incoming": len(incoming_records),
                "new_created": new_created_count,
                "updated": updated_count,
                "deactivated": deactivated_count,
                "retained": retained_count,
                "active_squad_total": len(active_incoming_player_ids),
                "preservation_guarantee": "All historical player records and match statistics preserved intact.",
            }),
            imported_by="admin",
        )
        self.session.add(history_record)

        # Commit transaction
        await self.session.commit()

        return {
            "batch_id": batch_id,
            "team_id": str(team.id),
            "season_id": str(season.id),
            "total_processed": len(incoming_records),
            "new_created": new_created_count,
            "updated": updated_count,
            "deactivated": deactivated_count,
            "retained": retained_count,
            "active_squad_count": len(active_incoming_player_ids),
            "status": "COMPLETED",
            "message": f"Successfully synchronized Chennaiyin FC 2026-27 squad ({len(active_incoming_player_ids)} active players). Departed players deactivated with historical statistics preserved.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def get_active_squad(
        self,
        team_id: uuid.UUID,
        season_id: uuid.UUID,
        include_inactive: bool = False,
        position_filter: Optional[str] = None,
        nationality_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Returns the synchronized squad list with full player profile and contract details."""
        stmt = (
            select(TeamSquadMembership)
            .where(
                TeamSquadMembership.team_id == team_id,
                TeamSquadMembership.season_id == season_id,
            )
            .options(selectinload(TeamSquadMembership.player))
            .order_by(TeamSquadMembership.squad_number.asc().nullslast())
        )
        if not include_inactive:
            stmt = stmt.where(TeamSquadMembership.is_active.is_(True))

        memberships = list((await self.session.execute(stmt)).scalars().all())
        output = []

        for m in memberships:
            p = m.player
            if not p:
                continue

            pos_raw = m.position or p.primary_position.value
            _, pos_group = parse_position(pos_raw)
            is_dom = (p.nationality == "India")

            if position_filter and position_filter.upper() != "ALL" and pos_group != position_filter.upper():
                continue
            if nationality_filter == "DOMESTIC" and not is_dom:
                continue
            if nationality_filter == "OVERSEAS" and is_dom:
                continue

            # Calculate Age
            age = None
            if p.date_of_birth:
                age = 2026 - p.date_of_birth.year

            output.append({
                "id": str(m.id),
                "player_id": str(p.id),
                "name": p.known_name or f"{p.first_name} {p.last_name}",
                "known_name": p.known_name,
                "squad_number": m.squad_number or p.squad_number,
                "position": pos_raw,
                "pos_group": pos_group,
                "nationality": p.nationality,
                "secondary_nationality": p.secondary_nationality,
                "is_domestic": is_dom,
                "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else None,
                "age": age,
                "height_m": p.height_m,
                "height_cm": p.height_cm,
                "preferred_foot": p.preferred_foot,
                "joined_date": m.joined_date.isoformat() if m.joined_date else (p.joined_date.isoformat() if p.joined_date else None),
                "previous_club": m.previous_club or p.previous_club,
                "contract_expiry": m.contract_expiry.isoformat() if m.contract_expiry else (p.contract_expiry.isoformat() if p.contract_expiry else None),
                "market_value_inr": m.market_value_inr if m.market_value_inr is not None else p.market_value_inr,
                "market_value_original": m.market_value_original or p.market_value_original,
                "is_active": m.is_active,
            })

        return output

    async def get_import_history(
        self,
        team_id: Optional[uuid.UUID] = None,
        season_id: Optional[uuid.UUID] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Returns squad synchronization and import history logs."""
        stmt = select(SquadImportHistory).order_by(SquadImportHistory.created_at.desc()).limit(limit)
        if team_id:
            stmt = stmt.where(SquadImportHistory.team_id == team_id)
        if season_id:
            stmt = stmt.where(SquadImportHistory.season_id == season_id)

        logs = list((await self.session.execute(stmt)).scalars().all())
        return [
            {
                "id": str(l.id),
                "batch_id": l.batch_id,
                "team_id": str(l.team_id),
                "season_id": str(l.season_id),
                "source_name": l.source_name,
                "total_incoming": l.total_incoming,
                "new_players": l.new_players,
                "updated_players": l.updated_players,
                "deactivated_players": l.deactivated_players,
                "retained_players": l.retained_players,
                "status": l.status,
                "report_summary": l.report_summary,
                "imported_by": l.imported_by,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ]
