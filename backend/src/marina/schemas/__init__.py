"""Pydantic v2 Schema Registry for MARINA INTELLIGENCE."""

from marina.schemas.common import (
    BaseSchema,
    HealthResponse,
    PaginatedResponse,
    PaginationParams,
)
from marina.schemas.competition import (
    CompetitionBase,
    CompetitionCreate,
    CompetitionRead,
    SeasonBase,
    SeasonCreate,
    SeasonRead,
)
from marina.schemas.match import (
    LineupRead,
    MatchBase,
    MatchCreate,
    MatchDetailRead,
    MatchEventRead,
    MatchRead,
)
from marina.schemas.player import (
    PlayerBase,
    PlayerCreate,
    PlayerRead,
    SquadRegistrationBase,
    SquadRegistrationCreate,
    SquadRegistrationRead,
)
from marina.schemas.provenance import (
    DataSourceBase,
    DataSourceCreate,
    DataSourceRead,
    ImportHistoryBase,
    ImportHistoryCreate,
    ImportHistoryRead,
)
from marina.schemas.statistics import (
    PlayerMatchStatisticBase,
    PlayerMatchStatisticCreate,
    PlayerMatchStatisticRead,
    TeamMatchStatisticBase,
    TeamMatchStatisticCreate,
    TeamMatchStatisticRead,
)
from marina.schemas.team import (
    TeamBase,
    TeamCreate,
    TeamRead,
    VenueBase,
    VenueCreate,
    VenueRead,
)

__all__ = [
    "BaseSchema",
    "HealthResponse",
    "PaginationParams",
    "PaginatedResponse",
    "CompetitionBase",
    "CompetitionCreate",
    "CompetitionRead",
    "SeasonBase",
    "SeasonCreate",
    "SeasonRead",
    "VenueBase",
    "VenueCreate",
    "VenueRead",
    "TeamBase",
    "TeamCreate",
    "TeamRead",
    "PlayerBase",
    "PlayerCreate",
    "PlayerRead",
    "SquadRegistrationBase",
    "SquadRegistrationCreate",
    "SquadRegistrationRead",
    "MatchBase",
    "MatchCreate",
    "MatchRead",
    "MatchDetailRead",
    "LineupRead",
    "MatchEventRead",
    "TeamMatchStatisticBase",
    "TeamMatchStatisticCreate",
    "TeamMatchStatisticRead",
    "PlayerMatchStatisticBase",
    "PlayerMatchStatisticCreate",
    "PlayerMatchStatisticRead",
    "DataSourceBase",
    "DataSourceCreate",
    "DataSourceRead",
    "ImportHistoryBase",
    "ImportHistoryCreate",
    "ImportHistoryRead",
]
