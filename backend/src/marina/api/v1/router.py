"""API v1 Router Aggregator."""

from fastapi import APIRouter

from marina.api.v1 import (
    competitions,
    health,
    matches,
    players,
    provenance,
    statistics,
    teams,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(competitions.router)
api_v1_router.include_router(teams.router)
api_v1_router.include_router(players.router)
api_v1_router.include_router(matches.router)
api_v1_router.include_router(statistics.router)
api_v1_router.include_router(provenance.router)
