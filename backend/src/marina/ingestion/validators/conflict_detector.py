"""Football Data Conflict and Duplicate Detection Service."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from marina.models.common import MatchStatus, VerificationStatus

logger = logging.getLogger("marina.ingestion.conflict")


@dataclass
class ConflictRecord:
    entity_type: str
    identifier: str
    conflict_type: str
    existing_value: Any
    incoming_value: Any
    source_code: str
    resolution: str
    detected_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ConflictDetector:
    """Detects score discrepancies, duplicate fixtures, duplicate jersey numbers, and schema violations."""

    def __init__(self) -> None:
        self.conflicts: List[ConflictRecord] = []

    def check_match_score_conflict(
        self,
        match_id: str,
        existing_status: MatchStatus,
        existing_home: Optional[int],
        existing_away: Optional[int],
        incoming_status: MatchStatus,
        incoming_home: Optional[int],
        incoming_away: Optional[int],
        source_code: str,
    ) -> Tuple[bool, VerificationStatus]:
        """Detects whether an incoming scoreline contradicts an already-recorded match score.

        RULE: Never silently overwrite conflicting results. If contradiction exists,
        set VerificationStatus to DISPUTED and log conflict for manual commissioner review.
        """
        # If neither has scores yet, no conflict
        if existing_home is None and incoming_home is None:
            return False, VerificationStatus.OFFICIAL

        # If existing is already recorded and incoming differs
        if (
            existing_home is not None
            and incoming_home is not None
            and (existing_home != incoming_home or existing_away != incoming_away)
        ):
            conflict = ConflictRecord(
                entity_type="MATCH_SCORE",
                identifier=match_id,
                conflict_type="SCORE_DISCREPANCY",
                existing_value=f"{existing_home}-{existing_away}",
                incoming_value=f"{incoming_home}-{incoming_away}",
                source_code=source_code,
                resolution="PRESERVED_EXISTING_FLAGGED_DISPUTED",
            )
            self.conflicts.append(conflict)
            logger.warning(
                "SCORE CONFLICT DETECTED for match %s: Existing %s vs Incoming %s from %s. Flagging DISPUTED.",
                match_id,
                conflict.existing_value,
                conflict.incoming_value,
                source_code,
            )
            return True, VerificationStatus.DISPUTED

        # If incoming provides score for finished match that lacked it
        if existing_home is None and incoming_home is not None:
            return False, VerificationStatus.VERIFIED

        return False, VerificationStatus.OFFICIAL

    def check_duplicate_fixtures(
        self,
        existing_matches: List[Dict[str, Any]],
        home_slug: str,
        away_slug: str,
        kickoff: datetime,
        window_hours: int = 48,
    ) -> Optional[Dict[str, Any]]:
        """Detects if a fixture between the same two teams is already scheduled within a short time window."""
        window = timedelta(hours=window_hours)
        for m in existing_matches:
            if m["home_team_slug"] == home_slug and m["away_team_slug"] == away_slug:
                diff = abs(m["kickoff"] - kickoff)
                if diff <= window:
                    return m
        return None

    def check_duplicate_jersey_number(
        self,
        squad_players: List[Dict[str, Any]],
        jersey_number: Optional[int],
        player_slug: str,
    ) -> bool:
        """Detects whether two active players share the same squad jersey number."""
        if jersey_number is None:
            return False
        for p in squad_players:
            if p.get("jersey_number") == jersey_number and p.get("slug") != player_slug:
                conflict = ConflictRecord(
                    entity_type="SQUAD_JERSEY",
                    identifier=f"jersey-{jersey_number}",
                    conflict_type="DUPLICATE_JERSEY_NUMBER",
                    existing_value=p.get("slug"),
                    incoming_value=player_slug,
                    source_code="SQUAD_VERIFICATION",
                    resolution="FLAGGED_DUPLICATE_NUMBER",
                )
                self.conflicts.append(conflict)
                return True
        return False
