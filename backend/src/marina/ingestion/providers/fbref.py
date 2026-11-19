"""FBref Authoritative Verified Data Adapter for Chennaiyin FC 2026–27.

Encapsulates the verified 5-match baseline dataset published by FBref and
serves as the authoritative ground truth for provider coverage evaluation.
"""

from typing import Any, Dict, List, Optional
from marina.ingestion.providers.base import BaseFootballDataProvider

FBREF_5_MATCHES = {
    "match-1": {
        "match_number": 1,
        "date": "10 Oct 2026",
        "home_team": "FC Goa",
        "away_team": "Chennaiyin FC",
        "venue": "Fatorda Stadium, Goa",
        "is_chennaiyin_home": False,
        "opponent_name": "FC Goa",
        "status": "FINISHED",
        "home_score": 1,
        "away_score": 1,
        "result": "D",
        "chennaiyin_score": 1,
        "opponent_score": 1,
        "possession_pct": 53.0,
        "opponent_possession_pct": 47.0,
        "shots_total": 9,
        "shots_on_target": 3,
        "opponent_shots_total": 17,
        "opponent_shots_on_target": 6,
        "goalkeeper_saves": 5,
        "shots_on_target_faced": 6,
        "clean_sheet": False,
        "formation": "4-3-3",
        "captain": "Mohammad Nawaz",
        "goalkeeper": "Mohammad Nawaz",
        "goalkeeper_minutes": 90,
        "top_scorer": None,
    },
    "match-2": {
        "match_number": 2,
        "date": "17 Oct 2026",
        "home_team": "Bengaluru FC",
        "away_team": "Chennaiyin FC",
        "venue": "Sree Kanteerava, Bengaluru",
        "is_chennaiyin_home": False,
        "opponent_name": "Bengaluru FC",
        "status": "FINISHED",
        "home_score": 2,
        "away_score": 0,
        "result": "L",
        "chennaiyin_score": 0,
        "opponent_score": 2,
        "possession_pct": 53.0,
        "opponent_possession_pct": 47.0,
        "shots_total": 20,
        "shots_on_target": 5,
        "opponent_shots_total": 10,
        "opponent_shots_on_target": 5,
        "goalkeeper_saves": 3,
        "shots_on_target_faced": 5,
        "clean_sheet": False,
        "formation": "4-4-2",
        "captain": "Mohammad Nawaz",
        "goalkeeper": "Mohammad Nawaz",
        "goalkeeper_minutes": 90,
        "top_scorer": None,
    },
    "match-3": {
        "match_number": 3,
        "date": "26 Oct 2026",
        "home_team": "Mohun Bagan SG",
        "away_team": "Chennaiyin FC",
        "venue": "Vivekananda YBK, Kolkata",
        "is_chennaiyin_home": False,
        "opponent_name": "Mohun Bagan SG",
        "status": "FINISHED",
        "home_score": 1,
        "away_score": 0,
        "result": "L",
        "chennaiyin_score": 0,
        "opponent_score": 1,
        "possession_pct": 52.0,
        "opponent_possession_pct": 48.0,
        "shots_total": 25,
        "shots_on_target": 6,
        "opponent_shots_total": 17,
        "opponent_shots_on_target": 7,
        "goalkeeper_saves": 6,
        "shots_on_target_faced": 7,
        "clean_sheet": False,
        "formation": "4-4-2",
        "captain": "Mohammad Nawaz",
        "goalkeeper": "Mohammad Nawaz",
        "goalkeeper_minutes": 90,
        "top_scorer": None,
    },
    "match-4": {
        "match_number": 4,
        "date": "31 Oct 2026",
        "home_team": "Chennaiyin FC",
        "away_team": "Kerala Blasters FC",
        "venue": "JLN Stadium, Chennai",
        "is_chennaiyin_home": True,
        "opponent_name": "Kerala Blasters FC",
        "status": "FINISHED",
        "home_score": 0,
        "away_score": 0,
        "result": "D",
        "chennaiyin_score": 0,
        "opponent_score": 0,
        "possession_pct": 55.0,
        "opponent_possession_pct": 45.0,
        "shots_total": 18,
        "shots_on_target": 5,
        "opponent_shots_total": 9,
        "opponent_shots_on_target": 2,
        "goalkeeper_saves": 2,
        "shots_on_target_faced": 2,
        "clean_sheet": True,
        "formation": "4-1-3-2",
        "captain": "Mohammad Nawaz",
        "goalkeeper": "Mohammad Nawaz",
        "goalkeeper_minutes": 90,
        "top_scorer": None,
    },
    "match-5": {
        "match_number": 5,
        "date": "7 Nov 2026",
        "home_team": "Chennaiyin FC",
        "away_team": "East Bengal FC",
        "venue": "JLN Stadium, Chennai",
        "is_chennaiyin_home": True,
        "opponent_name": "East Bengal FC",
        "status": "FINISHED",
        "home_score": 5,
        "away_score": 3,
        "result": "W",
        "chennaiyin_score": 5,
        "opponent_score": 3,
        "possession_pct": 48.0,
        "opponent_possession_pct": 52.0,
        "shots_total": 24,
        "shots_on_target": 11,
        "opponent_shots_total": 19,
        "opponent_shots_on_target": 5,
        "goalkeeper_saves": 2,
        "shots_on_target_faced": 5,
        "clean_sheet": False,
        "formation": "4-2-3-1",
        "captain": "Mohammad Nawaz",
        "goalkeeper": "Mohammad Nawaz",
        "goalkeeper_minutes": 90,
        "top_scorer": "Irfan Yadwad",
        "top_scorer_goals": 3,
    },
}


class FBrefVerifiedAdapter(BaseFootballDataProvider):
    """Adapter serving the verified FBref 5-match dataset."""

    def __init__(self) -> None:
        super().__init__(
            provider_code="FBREF_VERIFIED",
            provider_name="FBref Official Match Logs (Verified Ground Truth)",
            base_url="https://fbref.com/en/squads/6f0be699/2026-2027/matchlogs",
        )

    async def fetch_match_details(self, fixture_identifier: str) -> Dict[str, Any]:
        match = FBREF_5_MATCHES.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in verified dataset.")
        return {
            "source": self.provider_name,
            "source_url": f"{self.base_url}/schedule/Chennaiyin-Scores-and-Fixtures-Indian-Super-League",
            "fixture_id": fixture_identifier,
            "match_number": match["match_number"],
            "date": match["date"],
            "home_team": match["home_team"],
            "away_team": match["away_team"],
            "venue": match["venue"],
            "status": match["status"],
            "home_score": match["home_score"],
            "away_score": match["away_score"],
            "result": match["result"],
        }

    async def fetch_team_statistics(self, fixture_identifier: str) -> Dict[str, Any]:
        match = FBREF_5_MATCHES.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in verified dataset.")
        return {
            "source": self.provider_name,
            "source_url": f"{self.base_url}/shooting/Chennaiyin-Match-Logs-Indian-Super-League",
            "fixture_id": fixture_identifier,
            "possession_pct": match["possession_pct"],
            "opponent_possession_pct": match["opponent_possession_pct"],
            "shots_total": match["shots_total"],
            "shots_on_target": match["shots_on_target"],
            "opponent_shots_total": match["opponent_shots_total"],
            "opponent_shots_on_target": match["opponent_shots_on_target"],
            "goalkeeper_saves": match["goalkeeper_saves"],
            "shots_on_target_faced": match["shots_on_target_faced"],
            "clean_sheet": match["clean_sheet"],
        }

    async def fetch_lineups(self, fixture_identifier: str) -> Dict[str, Any]:
        match = FBREF_5_MATCHES.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in verified dataset.")
        return {
            "source": self.provider_name,
            "source_url": f"{self.base_url}/misc/Chennaiyin-Match-Logs-Indian-Super-League",
            "fixture_id": fixture_identifier,
            "formation": match["formation"],
            "captain": match["captain"],
            "starting_goalkeeper": match["goalkeeper"],
        }

    async def fetch_events(self, fixture_identifier: str) -> Dict[str, Any]:
        match = FBREF_5_MATCHES.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in verified dataset.")
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
            "goals_scored": match["chennaiyin_score"],
            "goals_conceded": match["opponent_score"],
            "top_scorer": match.get("top_scorer"),
        }

    async def fetch_player_statistics(self, fixture_identifier: str) -> Dict[str, Any]:
        match = FBREF_5_MATCHES.get(fixture_identifier)
        if not match:
            raise KeyError(f"Match {fixture_identifier} not in verified dataset.")
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
            "goalkeeper_appearances": 1,
            "goalkeeper_minutes": match["goalkeeper_minutes"],
            "goalkeeper_saves": match["goalkeeper_saves"],
        }

    async def fetch_spatial_events(self, fixture_identifier: str) -> Dict[str, Any]:
        # Spatial tracking coordinates (x,y) are NOT provided by FBref for Indian Super League
        return {
            "source": self.provider_name,
            "fixture_id": fixture_identifier,
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
            "pass_accuracy_individual": False,  # Not published for ISL
            "shot_coordinates_xy": False,        # Not published for ISL
            "pass_coordinates_xy": False,        # Not published for ISL
            "expected_goals_xg": False,          # Not published for ISL
            "progressive_passes": False,         # Not published for ISL
        }
