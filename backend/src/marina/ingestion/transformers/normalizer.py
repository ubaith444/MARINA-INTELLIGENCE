"""Football Data Normalization and Entity Resolution Service."""

import re
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union
from dateutil import parser as date_parser

from marina.models.common import MatchStatus, PlayerPosition, SquadStatus


class FootballNormalizer:
    """Normalizes team names, player identities, match fixtures, dates/timezones, and statistics."""

    # Canonical team registry with aliases
    TEAM_CANONICAL_MAP: Dict[str, Dict[str, str]] = {
        "chennaiyin-fc": {
            "name": "Chennaiyin FC",
            "short_name": "CFC",
            "slug": "chennaiyin-fc",
            "primary_color": "#003399",
            "secondary_color": "#FFFFFF",
        },
        "east-bengal-fc": {
            "name": "East Bengal FC",
            "short_name": "EBFC",
            "slug": "east-bengal-fc",
            "primary_color": "#E30613",
            "secondary_color": "#FEEE00",
        },
        "kerala-blasters-fc": {
            "name": "Kerala Blasters FC",
            "short_name": "KBFC",
            "slug": "kerala-blasters-fc",
            "primary_color": "#FFF200",
            "secondary_color": "#0055B8",
        },
        "mohun-bagan-sg": {
            "name": "Mohun Bagan SG",
            "short_name": "MBSG",
            "slug": "mohun-bagan-sg",
            "primary_color": "#006838",
            "secondary_color": "#800000",
        },
        "mumbai-city-fc": {
            "name": "Mumbai City FC",
            "short_name": "MCFC",
            "slug": "mumbai-city-fc",
            "primary_color": "#6CABDD",
            "secondary_color": "#FFFFFF",
        },
        "bengaluru-fc": {
            "name": "Bengaluru FC",
            "short_name": "BFC",
            "slug": "bengaluru-fc",
            "primary_color": "#003A70",
            "secondary_color": "#D71920",
        },
        "fc-goa": {
            "name": "FC Goa",
            "short_name": "FCG",
            "slug": "fc-goa",
            "primary_color": "#E35205",
            "secondary_color": "#003399",
        },
        "northeast-united-fc": {
            "name": "NorthEast United FC",
            "short_name": "NEUFC",
            "slug": "northeast-united-fc",
            "primary_color": "#DA291C",
            "secondary_color": "#000000",
        },
        "odisha-fc": {
            "name": "Odisha FC",
            "short_name": "OFC",
            "slug": "odisha-fc",
            "primary_color": "#800080",
            "secondary_color": "#000000",
        },
        "jamshedpur-fc": {
            "name": "Jamshedpur FC",
            "short_name": "JFC",
            "slug": "jamshedpur-fc",
            "primary_color": "#002B49",
            "secondary_color": "#C8102E",
        },
        "hyderabad-fc": {
            "name": "Hyderabad FC",
            "short_name": "HFC",
            "slug": "hyderabad-fc",
            "primary_color": "#FFCC00",
            "secondary_color": "#000000",
        },
        "mohammedan-sc": {
            "name": "Mohammedan SC",
            "short_name": "MSC",
            "slug": "mohammedan-sc",
            "primary_color": "#000000",
            "secondary_color": "#FFFFFF",
        },
        "punjab-fc": {
            "name": "Punjab FC",
            "short_name": "PFC",
            "slug": "punjab-fc",
            "primary_color": "#F37021",
            "secondary_color": "#002855",
        },
    }

    # Normalized text mapping -> slug
    TEAM_ALIAS_INDEX: Dict[str, str] = {
        "chennaiyin": "chennaiyin-fc",
        "chennaiyinfc": "chennaiyin-fc",
        "cfc": "chennaiyin-fc",
        "eastbengal": "east-bengal-fc",
        "eastbengalfc": "east-bengal-fc",
        "sceastbengal": "east-bengal-fc",
        "ebfc": "east-bengal-fc",
        "keralablasters": "kerala-blasters-fc",
        "keralablastersfc": "kerala-blasters-fc",
        "kbfc": "kerala-blasters-fc",
        "mohunbagan": "mohun-bagan-sg",
        "mohunbagansg": "mohun-bagan-sg",
        "mohunbagansupergiant": "mohun-bagan-sg",
        "atkmohunbagan": "mohun-bagan-sg",
        "mbsg": "mohun-bagan-sg",
        "mumbaicity": "mumbai-city-fc",
        "mumbaicityfc": "mumbai-city-fc",
        "mcfc": "mumbai-city-fc",
        "bengaluru": "bengaluru-fc",
        "bengalurufc": "bengaluru-fc",
        "bfc": "bengaluru-fc",
        "goa": "fc-goa",
        "fcgoa": "fc-goa",
        "fcg": "fc-goa",
        "northeastunited": "northeast-united-fc",
        "northeastunitedfc": "northeast-united-fc",
        "neufc": "northeast-united-fc",
        "odisha": "odisha-fc",
        "odishafc": "odisha-fc",
        "ofc": "odisha-fc",
        "jamshedpur": "jamshedpur-fc",
        "jamshedpurfc": "jamshedpur-fc",
        "jfc": "jamshedpur-fc",
        "hyderabad": "hyderabad-fc",
        "hyderabadfc": "hyderabad-fc",
        "hfc": "hyderabad-fc",
        "mohammedan": "mohammedan-sc",
        "mohammedansc": "mohammedan-sc",
        "msc": "mohammedan-sc",
        "punjab": "punjab-fc",
        "punjabfc": "punjab-fc",
        "pfc": "punjab-fc",
    }

    POSITION_MAP: Dict[str, PlayerPosition] = {
        "gk": PlayerPosition.GK,
        "goalkeeper": PlayerPosition.GK,
        "cb": PlayerPosition.CB,
        "centre-back": PlayerPosition.CB,
        "centre back": PlayerPosition.CB,
        "defender": PlayerPosition.CB,
        "lb": PlayerPosition.LB,
        "left-back": PlayerPosition.LB,
        "rb": PlayerPosition.RB,
        "right-back": PlayerPosition.RB,
        "lwb": PlayerPosition.LWB,
        "rwb": PlayerPosition.RWB,
        "dm": PlayerPosition.DM,
        "defensive midfielder": PlayerPosition.DM,
        "cm": PlayerPosition.CM,
        "central midfielder": PlayerPosition.CM,
        "midfielder": PlayerPosition.CM,
        "am": PlayerPosition.AM,
        "attacking midfielder": PlayerPosition.AM,
        "lm": PlayerPosition.LM,
        "rm": PlayerPosition.RM,
        "lw": PlayerPosition.LW,
        "left winger": PlayerPosition.LW,
        "rw": PlayerPosition.RW,
        "right winger": PlayerPosition.RW,
        "st": PlayerPosition.ST,
        "striker": PlayerPosition.ST,
        "cf": PlayerPosition.CF,
        "centre forward": PlayerPosition.CF,
        "forward": PlayerPosition.CF,
    }

    @classmethod
    def resolve_team(cls, raw_team_name: str) -> Dict[str, str]:
        """Resolves raw team name or abbreviation to canonical database entity dictionary."""
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", raw_team_name.lower())
        slug = cls.TEAM_ALIAS_INDEX.get(cleaned)
        if slug and slug in cls.TEAM_CANONICAL_MAP:
            return cls.TEAM_CANONICAL_MAP[slug]

        # Fallback slug generation for unmapped clubs
        generated_slug = re.sub(r"[^a-z0-9]+", "-", raw_team_name.lower()).strip("-")
        return {
            "name": raw_team_name.strip(),
            "short_name": raw_team_name.strip()[:4].upper(),
            "slug": generated_slug,
        }

    @classmethod
    def normalize_slug(cls, text: str) -> str:
        """Generates standard lowercase hyphenated URL slug."""
        return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

    @classmethod
    def normalize_datetime(cls, raw_dt: Union[str, datetime, date]) -> datetime:
        """Parses any date/timestamp string and normalizes to UTC datetime."""
        if isinstance(raw_dt, datetime):
            if raw_dt.tzinfo is None:
                return raw_dt.replace(tzinfo=timezone.utc)
            return raw_dt.astimezone(timezone.utc)

        if isinstance(raw_dt, date):
            return datetime(raw_dt.year, raw_dt.month, raw_dt.day, 14, 0, tzinfo=timezone.utc)

        parsed = date_parser.parse(str(raw_dt))
        if parsed.tzinfo is None:
            # If no timezone specified, default to IST (UTC+05:30) as official Indian football time
            ist_tz = timezone(date_parser.tz.gettz("Asia/Kolkata").utcoffset(datetime.now()))
            parsed = parsed.replace(tzinfo=ist_tz)
        return parsed.astimezone(timezone.utc)

    @classmethod
    def normalize_position(cls, raw_pos: Optional[str]) -> PlayerPosition:
        """Normalizes free-text position into standardized PlayerPosition enum."""
        if not raw_pos:
            return PlayerPosition.CM
        cleaned = raw_pos.lower().strip()
        return cls.POSITION_MAP.get(cleaned, PlayerPosition.CM)

    @classmethod
    def normalize_nullable_metric(cls, raw_val: Any, val_type: type = float) -> Optional[Any]:
        """CRITICAL DATA INTEGRITY HELPER:
        Converts empty / unavailable values to None.
        NEVER transforms missing values into 0.
        """
        if raw_val is None:
            return None
        if isinstance(raw_val, str):
            s = raw_val.strip()
            if s in ("", "N/A", "n/a", "-", "null", "None"):
                return None
            try:
                return val_type(s)
            except (ValueError, TypeError):
                return None
        try:
            return val_type(raw_val)
        except (ValueError, TypeError):
            return None
