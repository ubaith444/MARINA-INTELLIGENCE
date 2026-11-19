"""API v1 Router Aggregator."""

from fastapi import APIRouter

from marina.api.v1 import (
    analytics,
    competitions,
    fixtures,
    health,
    matches,
    players,
    provenance,
    season_analytics,
    squads,
    statistics,
    sync,
    teams,
)

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(competitions.router)
api_v1_router.include_router(competitions.seasons_router)
api_v1_router.include_router(teams.router)
api_v1_router.include_router(players.router)
api_v1_router.include_router(squads.router)
api_v1_router.include_router(fixtures.router)
api_v1_router.include_router(matches.router)
api_v1_router.include_router(statistics.router)
api_v1_router.include_router(provenance.router)
api_v1_router.include_router(provenance.data_sources_router)
api_v1_router.include_router(analytics.router)
api_v1_router.include_router(season_analytics.router)
api_v1_router.include_router(sync.router)
