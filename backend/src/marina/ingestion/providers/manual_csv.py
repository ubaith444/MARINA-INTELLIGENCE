"""Manual CSV / File Provider Adapter.

Supports ingesting verified team statistics, advanced performance indicators,
and supplemental metrics when commercial APIs do not cover them for ISL.
"""

from typing import Any, Dict, List, Optional
from marina.ingestion.providers.base import BaseFootballDataProvider
from marina.ingestion.providers.fbref import FBREF_5_MATCHES


class ManualCsvProviderAdapter(BaseFootballDataProvider):
    """Adapter for ingesting manually curated and verified CSV/JSON match records."""

    def __init__(self, data_registry: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            provider_code="MANUAL_CSV_VERIFIED",
            provider_name="Manual Curated CSV / Match Sheet Archive",
            base_url="file://backend/src/marina/data",
        )
        self.data_registry = data_registry or FBREF_5_MATCHES

    async def fetch_match_details(self, fixture_identifier: str) -> Dict[str, Any]:
        match = self.data_registry.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in manual registry.")
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
            "match_number": match["match_number"],
            "date": match["date"],
            "venue": match["venue"],
            "status": match["status"],
            "home_score": match["home_score"],
            "away_score": match["away_score"],
            "verified_by_analyst": True,
        }

    async def fetch_team_statistics(self, fixture_identifier: str) -> Dict[str, Any]:
        match = self.data_registry.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in manual registry.")
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
            "possession_pct": match["possession_pct"],
            "shots_total": match["shots_total"],
            "shots_on_target": match["shots_on_target"],
            "opponent_shots_total": match["opponent_shots_total"],
            "opponent_shots_on_target": match["opponent_shots_on_target"],
            "goalkeeper_saves": match["goalkeeper_saves"],
            "clean_sheet": match["clean_sheet"],
        }

    async def fetch_lineups(self, fixture_identifier: str) -> Dict[str, Any]:
        match = self.data_registry.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in manual registry.")
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
            "formation": match["formation"],
            "captain": match["captain"],
            "starting_goalkeeper": match["goalkeeper"],
        }

    async def fetch_events(self, fixture_identifier: str) -> Dict[str, Any]:
        match = self.data_registry.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in manual registry.")
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
            "goals_scored": match["chennaiyin_score"],
            "goals_conceded": match["opponent_score"],
            "top_scorer": match.get("top_scorer"),
        }

    async def fetch_player_statistics(self, fixture_identifier: str) -> Dict[str, Any]:
        match = self.data_registry.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in manual registry.")
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
            "goalkeeper_minutes": match["goalkeeper_minutes"],
            "goalkeeper_saves": match["goalkeeper_saves"],
        }

    async def fetch_spatial_events(self, fixture_identifier: str) -> Dict[str, Any]:
        return {
            "source": self.provider_name,
            "has_shot_coordinates": False,
            "has_pass_coordinates": False,
            "has_xg": False,
            "shot_coordinates": None,
            "pass_coordinates": None,
        }

    def get_supported_metrics(self) -> Dict[str, bool]:
        return {
            "match_date": True,
            "venue": True,
            "scores": True,
            "match_status": True,
            "possession_pct": True,
            "shots_total": True,
            "shots_on_target": True,
            "opponent_shots_total": True,
            "opponent_shots_on_target": True,
            "goalkeeper_saves": True,
            "clean_sheets": True,
            "tactical_formation": True,
            "captain": True,
            "shot_coordinates_xy": False,
            "pass_coordinates_xy": False,
            "expected_goals_xg": False,
            "progressive_passes": False,
        }
