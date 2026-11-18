"""Automated Tests for Health and Diagnostics."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_200(client: AsyncClient):
    """Verify that /api/v1/health returns HTTP 200 and matches the HealthResponse contract."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] in ("healthy", "degraded")
    assert "database" in data
    assert data["focus_club"] == "Chennaiyin FC"
    assert data["focus_season"] == "2026–27"
    assert data["focus_competition"] == "Indian Super League"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_metadata(client: AsyncClient):
    """Verify platform metadata at root."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "MARINA INTELLIGENCE"
    assert data["status"] == "operational"
    assert data["docs_url"] == "/docs"
