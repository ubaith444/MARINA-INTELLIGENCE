"""Common Analytics Utilities, Math Helpers, and Data Coverage Contracts."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
import numpy as np


def safe_divide(
    numerator: Optional[Union[int, float]],
    denominator: Optional[Union[int, float]],
    default: Optional[float] = None,
    round_digits: Optional[int] = 2,
) -> Optional[float]:
    """Safely calculates numerator / denominator preventing ZeroDivisionError and NaN.

    If numerator or denominator is None, or denominator is 0, returns `default` (usually None).
    """
    if numerator is None or denominator is None:
        return default
    try:
        num_f = float(numerator)
        den_f = float(denominator)
        if den_f == 0.0 or np.isnan(num_f) or np.isnan(den_f):
            return default
        res = num_f / den_f
        if round_digits is not None:
            return round(res, round_digits)
        return res
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def calculate_per_90(
    stat_value: Optional[Union[int, float]],
    minutes_played: Optional[int],
    min_minutes_threshold: int = 45,
    round_digits: int = 2,
) -> Optional[float]:
    """Calculates standardized per-90 minute metric: (stat / minutes) * 90.

    If minutes played is below threshold or stat is None, returns None to avoid
    skewed statistics from small sample sizes.
    """
    if stat_value is None or minutes_played is None:
        return None
    if minutes_played < min_minutes_threshold:
        return None
    return safe_divide(stat_value * 90.0, minutes_played, default=None, round_digits=round_digits)


@dataclass
class DataCoverageMetrics:
    """Tracks sample size and metric completeness to prevent misleading conclusions."""
    sample_matches_count: int
    minutes_tracked: int
    data_source_codes: List[str]
    has_event_level_data: bool
    has_tracking_gps_data: bool
    coverage_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_matches_count": self.sample_matches_count,
            "minutes_tracked": self.minutes_tracked,
            "data_source_codes": self.data_source_codes,
            "has_event_level_data": self.has_event_level_data,
            "has_tracking_gps_data": self.has_tracking_gps_data,
            "coverage_notes": self.coverage_notes,
        }
