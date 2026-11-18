"""Automated Tests for OpenAPI Documentation and Schema Generation."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_openapi_json_schema(client: AsyncClient):
    """Verify that OpenAPI schema is properly generated at /api/v1/openapi.json."""
    response = await client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    assert schema["info"]["title"] == "MARINA INTELLIGENCE"
    assert "paths" in schema

    # Verify key paths exist in OpenAPI documentation
    paths = schema["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/competitions" in paths
    assert "/api/v1/teams" in paths
    assert "/api/v1/players" in paths
    assert "/api/v1/matches" in paths
    assert "/api/v1/statistics/teams" in paths
    assert "/api/v1/statistics/players" in paths
    assert "/api/v1/provenance/sources" in paths


@pytest.mark.asyncio
async def test_swagger_ui_endpoint(client: AsyncClient):
    """Verify Swagger UI docs endpoint loads."""
    response = await client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
