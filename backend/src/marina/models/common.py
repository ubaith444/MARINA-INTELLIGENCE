"""Common Domain Enums and Type Definitions."""

import enum


class VerificationStatus(str, enum.Enum):
    """Provenance and verification lifecycle for records and statistics."""
    UNVERIFIED = "UNVERIFIED"
    PROVISIONAL = "PROVISIONAL"
    VERIFIED = "VERIFIED"
    OFFICIAL = "OFFICIAL"
    DISPUTED = "DISPUTED"


class MatchStatus(str, enum.Enum):
    """Lifecycle of a football fixture. Supports upcoming and incomplete seasons."""
    SCHEDULED = "SCHEDULED"
    TIMED = "TIMED"
    IN_PLAY = "IN_PLAY"
    PAUSED = "PAUSED"
    FINISHED = "FINISHED"
    POSTPONED = "POSTPONED"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"


class EventType(str, enum.Enum):
    """Categorization of discrete in-match football events."""
    GOAL = "GOAL"
    PENALTY_GOAL = "PENALTY_GOAL"
    OWN_GOAL = "OWN_GOAL"
    SHOT = "SHOT"
    SHOT_ON_TARGET = "SHOT_ON_TARGET"
    SAVE = "SAVE"
    YELLOW_CARD = "YELLOW_CARD"
    RED_CARD = "RED_CARD"
    SECOND_YELLOW = "SECOND_YELLOW"
    SUBSTITUTION = "SUBSTITUTION"
    FOUL = "FOUL"
    OFFSIDE = "OFFSIDE"
    CORNER = "CORNER"
    PENALTY_AWARDED = "PENALTY_AWARDED"
    VAR_DECISION = "VAR_DECISION"


class MatchPeriod(str, enum.Enum):
    """Match segments."""
    PRE_MATCH = "PRE_MATCH"
    FIRST_HALF = "FIRST_HALF"
    HALF_TIME = "HALF_TIME"
    SECOND_HALF = "SECOND_HALF"
    EXTRA_FIRST = "EXTRA_FIRST"
    EXTRA_SECOND = "EXTRA_SECOND"
    PENALTY_SHOOTOUT = "PENALTY_SHOOTOUT"
    FULL_TIME = "FULL_TIME"


class LineupRole(str, enum.Enum):
    """Player match squad roles."""
    STARTER = "STARTER"
    BENCH = "BENCH"
    RESERVE = "RESERVE"


class SquadStatus(str, enum.Enum):
    """Player club registration status for a specific season."""
    FIRST_TEAM = "FIRST_TEAM"
    RESERVES = "RESERVES"
    ACADEMY = "ACADEMY"
    ON_LOAN = "ON_LOAN"
    TRIAL = "TRIAL"
    RELEASED = "RELEASED"


class ProviderType(str, enum.Enum):
    """Types of data sources."""
    OFFICIAL_LEAGUE = "OFFICIAL_LEAGUE"
    CLUB_COMMUNICATIONS = "CLUB_COMMUNICATIONS"
    DATA_PROVIDER = "DATA_PROVIDER"
    FEDERATION = "FEDERATION"
    MANUAL_CURATION = "MANUAL_CURATION"


class BatchStatus(str, enum.Enum):
    """Status of ingestion batches."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class PlayerPosition(str, enum.Enum):
    """Standardized tactical football positions."""
    GK = "GOALKEEPER"
    DEF = "DEFENDER"
    CB = "CENTRE_BACK"
    LB = "LEFT_BACK"
    RB = "RIGHT_BACK"
    LWB = "LEFT_WING_BACK"
    RWB = "RIGHT_WING_BACK"
    DM = "DEFENSIVE_MIDFIELDER"
    CM = "CENTRAL_MIDFIELDER"
    AM = "ATTACKING_MIDFIELDER"
    LM = "LEFT_MIDFIELDER"
    RM = "RIGHT_MIDFIELDER"
    LW = "LEFT_WINGER"
    RW = "RIGHT_WINGER"
    ST = "STRIKER"
    CF = "CENTRE_FORWARD"
