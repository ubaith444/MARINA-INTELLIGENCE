"""StatsBomb Open Data Adapter for Testing Tactical Event Processing.

STRICT DATA INTEGRITY GUARD:
StatsBomb Open Data is utilized EXCLUSIVELY for developing and verifying
complex event-stream pipelines, spatial coordinates, and tactical models.
It MUST NEVER be associated with or claimed as Chennaiyin FC or ISL match data.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx


class StatsBombOpenDataAdapter:
    """Benchmark adapter consuming open-source StatsBomb JSON for testing event processing."""

    OPEN_DATA_BASE_URL = (
        "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
    )

    def __init__(self, source_code: str = "STATSBOMB_OPEN_DATA") -> None:
        self.source_code = source_code
        self.source_name = "StatsBomb Open Data (Algorithmic Test Benchmark)"

    async def fetch_benchmark_lineup(self, match_id: int = 3788741) -> Dict[str, Any]:
        """Fetches a sample open-data lineup for event engine verification."""
        url = f"{self.OPEN_DATA_BASE_URL}/lineups/{match_id}.json"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(url)
                res.raise_for_status()
                payload = res.json()
        except Exception:
            # Fallback local benchmark fixture
            payload = self._get_fallback_benchmark_lineup()

        return {
            "source_code": self.source_code,
            "source_type": "BENCHMARK_ONLY_NEVER_CFC",
            "benchmark_match_id": match_id,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "lineup_data": payload,
        }

    async def fetch_benchmark_events(self, match_id: int = 3788741) -> Dict[str, Any]:
        """Fetches sample open-data match events for testing spatial pass & shot processors."""
        url = f"{self.OPEN_DATA_BASE_URL}/events/{match_id}.json"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(url)
                res.raise_for_status()
                events = res.json()
        except Exception:
            events = self._get_fallback_benchmark_events()

        return {
            "source_code": self.source_code,
            "source_type": "BENCHMARK_ONLY_NEVER_CFC",
            "benchmark_match_id": match_id,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "events_count": len(events),
            "events": events[:20],  # Sample for pipeline verification
        }

    def _get_fallback_benchmark_lineup(self) -> List[Dict[str, Any]]:
        return [
            {
                "team_id": 769,
                "team_name": "Benchmark XI",
                "lineup": [
                    {"player_id": 1001, "player_name": "Test Goalkeeper", "jersey_number": 1, "country": {"name": "Test"}},
                    {"player_id": 1002, "player_name": "Test Playmaker", "jersey_number": 10, "country": {"name": "Test"}},
                ],
            }
        ]

    def _get_fallback_benchmark_events(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "e812d8a0-2f22-482d-8cb5-992d9bb4e7f1",
                "index": 1,
                "period": 1,
                "timestamp": "00:00:00.000",
                "minute": 0,
                "second": 0,
                "type": {"id": 35, "name": "Starting XI"},
            },
            {
                "id": "f923e9b1-3e33-493e-9dc6-003e0cc5f8a2",
                "index": 2,
                "period": 1,
                "timestamp": "00:00:15.200",
                "minute": 0,
                "second": 15,
                "type": {"id": 30, "name": "Pass"},
                "location": [60.0, 40.0],
                "pass": {"recipient": {"id": 1002, "name": "Test Playmaker"}, "length": 18.5, "angle": 0.35},
            },
        ]
