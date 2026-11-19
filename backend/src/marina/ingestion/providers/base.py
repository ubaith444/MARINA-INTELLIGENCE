"""Provider-Independent Football Data Interface and Contracts.

Defines the core abstract interface for external data providers (API-Football,
Sportmonks, FBref, Manual CSV) with strict metric provenance tracking,
validation hooks, and non-fabrication guarantees.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class MetricCategory(str, Enum):
    MATCH_DETAILS = "Match Details"
    SCORE_OUTCOME = "Score & Outcome"
    TEAM_ATTACKING = "Team Attacking"
    OPPOSITION_COMPARISON = "Opposition Comparison"
    TEAM_PASSING = "Team Passing"
    DEFENSIVE = "Defensive Performance"
    GOALKEEPING = "Goalkeeping"
    LINEUPS_TACTICS = "Lineups & Formations"
    MATCH_EVENTS = "Match Events"
    EVENT_COORDINATES = "Event Spatial Coordinates"
    ADVANCED_TACTICAL = "Advanced Tactical & Expected Metrics"


class ValidationStatus(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    NOT_SUPPORTED = "NOT_SUPPORTED"  # Provider does not offer this tier for ISL
    MISSING = "MISSING"


@dataclass
class ProviderMetricResult:
    """Detailed audit entry for a single requested metric."""
    metric_name: str
    category: MetricCategory
    is_returned: bool
    raw_value: Any
    normalized_value: Any
    source: str
    validation_status: ValidationStatus
    validation_notes: str
    is_critical: bool = False


@dataclass
class MatchCoverageResult:
    """Coverage test outcome for a single completed match fixture."""
    fixture_id: str
    match_number: int
    date: str
    home_team: str
    away_team: str
    provider_name: str
    metrics: Dict[str, ProviderMetricResult] = field(default_factory=dict)
    tested_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def get_summary(self) -> Dict[str, int]:
        total = len(self.metrics)
        passed = sum(1 for m in self.metrics.values() if m.validation_status == ValidationStatus.PASS)
        warned = sum(1 for m in self.metrics.values() if m.validation_status == ValidationStatus.WARN)
        failed = sum(1 for m in self.metrics.values() if m.validation_status == ValidationStatus.FAIL)
        not_supported = sum(1 for m in self.metrics.values() if m.validation_status == ValidationStatus.NOT_SUPPORTED)
        missing = sum(1 for m in self.metrics.values() if m.validation_status == ValidationStatus.MISSING)
        return {
            "total_metrics": total,
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "not_supported": not_supported,
            "missing": missing,
            "coverage_pct": round((passed / (total - not_supported)) * 100, 1) if (total - not_supported) > 0 else 0.0,
        }


class BaseFootballDataProvider(ABC):
    """Abstract provider interface ensuring replaceable adapters with consistent contracts."""

    def __init__(self, provider_code: str, provider_name: str, base_url: str) -> None:
        self.provider_code = provider_code
        self.provider_name = provider_name
        self.base_url = base_url

    @abstractmethod
    async def fetch_match_details(self, fixture_identifier: str) -> Dict[str, Any]:
        """Fetches match metadata: date, venue, opponent, kickoff, match status."""
        pass

    @abstractmethod
    async def fetch_team_statistics(self, fixture_identifier: str) -> Dict[str, Any]:
        """Fetches aggregate team statistics: possession, shots, shots on target, passes."""
        pass

    @abstractmethod
    async def fetch_lineups(self, fixture_identifier: str) -> Dict[str, Any]:
        """Fetches starting XI, substitutes, tactical formations, and captain."""
        pass

    @abstractmethod
    async def fetch_events(self, fixture_identifier: str) -> Dict[str, Any]:
        """Fetches discrete events: goals, cards, substitutions."""
        pass

    @abstractmethod
    async def fetch_player_statistics(self, fixture_identifier: str) -> Dict[str, Any]:
        """Fetches individual player performance statistics."""
        pass

    @abstractmethod
    async def fetch_spatial_events(self, fixture_identifier: str) -> Dict[str, Any]:
        """Fetches event coordinates (x,y) for shots and passes, or returns empty/null."""
        pass

    @abstractmethod
    def get_supported_metrics(self) -> Dict[str, bool]:
        """Returns dictionary of supported vs unsupported metrics for Indian Super League."""
        pass
