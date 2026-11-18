"""Common Pydantic Schemas, Enums, and Pagination Contracts."""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with standard Pydantic v2 configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class HealthResponse(BaseModel):
    """Health check payload contract."""
    status: str = Field(default="healthy", description="Application status")
    database: str = Field(description="Database connectivity status: connected or unreachable")
    app_env: str = Field(description="Current application environment")
    version: str = Field(description="Marina Intelligence platform version")
    timestamp: datetime = Field(description="ISO-8601 server timestamp")
    focus_club: str = Field(default="Chennaiyin FC", description="Anchor club focus")
    focus_season: str = Field(default="2026–27", description="Anchor season focus")
    focus_competition: str = Field(default="Indian Super League", description="Anchor competition focus")


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    limit: int = Field(default=50, ge=1, le=100, description="Items per page")
    offset: int = Field(default=0, ge=0, description="Items to skip")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Standard generic envelope for paginated collections."""
    items: List[T]
    total: int
    limit: int
    offset: int
