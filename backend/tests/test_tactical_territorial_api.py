"""Unit & Integration Tests for Tactical Intelligence and Territorial Dominance APIs."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from marina.models.player import Player


@pytest.mark.asyncio
async def test_territorial_metrics_season_aggregate(client: AsyncClient):
    """Test territorial metrics returns Field Tilt 62.8%, 142 CFC FT passes, 84 Opp, 48 Prog passes, 0.68 Density."""
    response = await client.get("/api/v1/analytics/tactical/territorial")
    assert response.status_code == 200
    data = response.json()

    assert data["field_tilt_pct"] == 62.8
    assert data["field_tilt_status"] == "HIGH"
    assert data["final_third_passes"]["chennaiyin_fc"] == 142
    assert data["final_third_passes"]["opponent"] == 84
    assert data["final_third_passes"]["total"] == 226
    assert data["progressive_passes"]["count"] == 48
    assert data["network_density"]["value"] == 0.68
    assert data["network_density"]["status"] == "Strong structural connectivity"


@pytest.mark.asyncio
async def test_tactical_passing_network_structure(client: AsyncClient):
    """Test passing network returns nodes with actual CFC squad players and valid edges."""
    response = await client.get("/api/v1/analytics/tactical/passing-network")
    assert response.status_code == 200
    data = response.json()

    assert data["nodes_count"] >= 10
    assert data["edges_count"] >= 15
    assert data["network_density"] is not None

    # Verify nodes have real player names from Chennaiyin FC
    node_names = [n["player_name"] for n in data["nodes"]]
    assert any("Nawaz" in name for name in node_names)
    assert any("Talal" in name for name in node_names)
    assert any("Yadwad" in name for name in node_names)


@pytest.mark.asyncio
async def test_tactical_passing_network_player_filter(client: AsyncClient, db_session):
    """Test passing network with a specific player selected highlights their data."""
    # First get the nodes
    resp_all = await client.get("/api/v1/analytics/tactical/passing-network")
    assert resp_all.status_code == 200
    all_data = resp_all.json()
    assert len(all_data["nodes"]) > 0

    first_node = all_data["nodes"][0]
    target_player_id = first_node["player_id"]

    response = await client.get(f"/api/v1/analytics/tactical/passing-network?player_id={target_player_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["nodes_count"] > 0
    if data.get("selected_player"):
        assert data["selected_player"]["player_id"] == target_player_id


@pytest.mark.asyncio
async def test_tactical_shot_map(client: AsyncClient):
    """Test shot map returns verified shots with coordinates and outcomes."""
    response = await client.get("/api/v1/analytics/tactical/shot-map")
    assert response.status_code == 200
    data = response.json()

    assert data["total_shots"] > 0
    assert data["goals"] > 0
    assert data["shots_on_target"] >= data["goals"]
    assert len(data["shots"]) == data["total_shots"]

    first_shot = data["shots"][0]
    assert "x" in first_shot and "y" in first_shot
    assert "outcome" in first_shot
    assert first_shot["team_name"] == "Chennaiyin FC"


@pytest.mark.asyncio
async def test_tactical_defensive_actions(client: AsyncClient):
    """Test defensive actions endpoint returns tackles, interceptions, clearances, blocks, recoveries."""
    response = await client.get("/api/v1/analytics/tactical/defensive-actions")
    assert response.status_code == 200
    data = response.json()

    assert data["total_actions"] > 0
    assert data["tackles"] > 0
    assert data["interceptions"] > 0
    assert data["clearances"] > 0
    assert data["blocks"] > 0
    assert data["recoveries"] > 0
    assert len(data["actions"]) == data["total_actions"]


@pytest.mark.asyncio
async def test_tactical_heatmap_zero_fabrication(client: AsyncClient):
    """Test heatmap returns zero-fabrication message when tracking telemetry is unprovisioned."""
    response = await client.get("/api/v1/analytics/tactical/heatmap")
    assert response.status_code == 200
    data = response.json()

    assert data["data_available"] is False
    assert data["coverage_status"] == "DATA_UNAVAILABLE"
    assert "zero-fabrication" in data["message"].lower() or "not provisioned" in data["message"].lower()
    assert data["zones"] == []
    assert "low" in data["legend"]
    assert "high" in data["legend"]
