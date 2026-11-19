"""Tests for Individual Player Statistics Rebuild and Ground Truth Accuracy."""

import pytest
from httpx import AsyncClient, ASGITransport
from marina.main import app
from marina.db.session import AsyncSessionLocal
from marina.services.season_overview_service import SeasonOverviewService
from marina.analytics.player_intelligence import PlayerIntelligenceEngine
from marina.models.player import Player
from sqlalchemy import select


@pytest.mark.asyncio
async def test_all_28_squad_players_returned():
    """Verify that all 28 registered squad players are returned in the player statistics."""
    async with AsyncSessionLocal() as session:
        service = SeasonOverviewService(session)
        stats = await service.get_player_statistics()
        assert len(stats) == 28, f"Expected 28 squad players, got {len(stats)}"
        
        # Verify no duplicate player_ids
        pids = [s.player_id for s in stats]
        assert len(pids) == len(set(pids)), "Duplicate players detected in statistics response"


@pytest.mark.asyncio
async def test_unplayed_squad_members_zero_minutes_and_no_fabrication():
    """Verify unplayed players show 0 appearances, 0 minutes, and None for rate stats."""
    async with AsyncSessionLocal() as session:
        service = SeasonOverviewService(session)
        stats = await service.get_player_statistics()
        
        unplayed_names = [
            "Samik Mitra",
            "Maheson Tongbram Singh",
            "Vignesh D",
            "Harmandeep Singh",
            "Malhar Mohol",
            "Devansh Dabas",
            "Klusner John Manuel Pereira",
            "Vivek S",
        ]
        
        stats_by_name = {s.name: s for s in stats}
        for name in unplayed_names:
            assert name in stats_by_name, f"Expected {name} in statistics"
            p_stat = stats_by_name[name]
            assert p_stat.appearances == 0, f"{name} should have 0 appearances"
            assert p_stat.starts == 0, f"{name} should have 0 starts"
            assert p_stat.minutes_played == 0, f"{name} should have 0 minutes"
            assert p_stat.goals == 0, f"{name} should have 0 goals"
            assert p_stat.assists == 0, f"{name} should have 0 assists"
            assert p_stat.goals_per_90 is None, f"{name} should have None for goals_per_90"
            assert p_stat.assists_per_90 is None, f"{name} should have None for assists_per_90"
            assert p_stat.has_sufficient_minutes is False, f"{name} should have has_sufficient_minutes=False"


@pytest.mark.asyncio
async def test_goalkeeper_specific_statistics():
    """Verify goalkeeper-specific metrics for Mohammad Nawaz and ensure outfield players have None."""
    async with AsyncSessionLocal() as session:
        service = SeasonOverviewService(session)
        stats = await service.get_player_statistics()
        stats_by_name = {s.name: s for s in stats}
        
        nawaz = stats_by_name["Mohammad Nawaz"]
        assert nawaz.appearances == 5
        assert nawaz.starts == 5
        assert nawaz.minutes_played == 450
        assert nawaz.clean_sheets == 1, f"Expected 1 clean sheet for Nawaz, got {nawaz.clean_sheets}"
        assert nawaz.saves == 19, f"Expected 19 saves for Nawaz, got {nawaz.saves}"
        assert nawaz.goals_conceded == 7, f"Expected 7 goals conceded for Nawaz, got {nawaz.goals_conceded}"
        assert nawaz.save_percentage == 73.1, f"Expected 73.1% save percentage, got {nawaz.save_percentage}"
        
        # Verify outfield player does not receive goalkeeper metrics
        yadwad = stats_by_name["Irfan Yadwad"]
        assert yadwad.saves is None
        assert yadwad.goals_conceded is None
        assert yadwad.clean_sheets is None
        assert yadwad.save_percentage is None


@pytest.mark.asyncio
async def test_verified_goalscorers_and_creators():
    """Verify top scorers and creators match official ISL 2026-27 match records."""
    async with AsyncSessionLocal() as session:
        service = SeasonOverviewService(session)
        stats = await service.get_player_statistics()
        stats_by_name = {s.name: s for s in stats}
        
        yadwad = stats_by_name["Irfan Yadwad"]
        assert yadwad.goals == 3
        assert yadwad.assists == 1
        assert yadwad.minutes_played == 406
        assert yadwad.goals_per_90 == 0.67
        
        brison = stats_by_name["Brison Fernandes"]
        assert brison.goals == 2
        assert brison.assists == 0
        assert brison.minutes_played == 272
        assert brison.goals_per_90 == 0.66
        
        tanque = stats_by_name["Ramon Tanque"]
        assert tanque.goals == 1
        assert tanque.assists == 1
        assert tanque.minutes_played == 438
        assert tanque.goals_per_90 == 0.21


@pytest.mark.asyncio
async def test_discipline_and_card_records():
    """Verify disciplinary cards match verified records."""
    async with AsyncSessionLocal() as session:
        service = SeasonOverviewService(session)
        stats = await service.get_player_statistics()
        stats_by_name = {s.name: s for s in stats}
        
        emmanuel = stats_by_name["Emmanuel Imanishimwe"]
        assert emmanuel.yellow_cards == 2
        assert emmanuel.red_cards == 1
        assert emmanuel.appearances == 4
        
        bhutia = stats_by_name["Namgyal Bhutia"]
        assert bhutia.yellow_cards == 1
        assert bhutia.red_cards == 0


@pytest.mark.asyncio
async def test_player_endpoints_via_api():
    """Test /api/v1/players/statistics and filters."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. All players
        res = await client.get("/api/v1/players/statistics")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 28
        
        # 2. Position filter GK
        gk_res = await client.get("/api/v1/players/statistics?position=GK")
        assert gk_res.status_code == 200
        gk_data = gk_res.json()
        assert len(gk_data) == 4  # Nawaz, Mitra, Mohol, Dabas
        for gk in gk_data:
            assert "GOALKEEPER" in gk["position"].upper() or gk["position"].upper() == "GK"
        
        # 3. Search filter
        search_res = await client.get("/api/v1/players/statistics?search=Yadwad")
        assert search_res.status_code == 200
        s_data = search_res.json()
        assert len(s_data) == 1
        assert s_data[0]["name"] == "Irfan Yadwad"
        
        # 4. Sort by goals desc
        sort_res = await client.get("/api/v1/players/statistics?sort_by=goals&order=desc")
        assert sort_res.status_code == 200
        sort_data = sort_res.json()
        assert sort_data[0]["name"] == "Irfan Yadwad"
        assert sort_data[0]["goals"] == 3


@pytest.mark.asyncio
async def test_player_performance_and_compare_api():
    """Test /api/v1/analytics/players/{id}/performance and /analytics/players/compare."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get Yadwad and Tanque IDs
        res = await client.get("/api/v1/players/statistics")
        data = res.json()
        by_name = {p["name"]: p["player_id"] for p in data}
        
        yadwad_id = by_name["Irfan Yadwad"]
        tanque_id = by_name["Ramon Tanque"]
        nawaz_id = by_name["Mohammad Nawaz"]
        dabas_id = by_name["Devansh Dabas"]
        
        # Individual performance for Yadwad
        p_res = await client.get(f"/api/v1/analytics/players/{yadwad_id}/performance")
        assert p_res.status_code == 200
        p_data = p_res.json()
        assert p_data["name"] == "Irfan Yadwad"
        assert p_data["raw_totals"]["goals"] == 3
        assert p_data["per_90"]["has_sufficient_minutes"] is True
        assert p_data["per_90"]["goals_per_90"] == 0.67
        assert "data_provenance" in p_data
        
        # Individual performance for unplayed player (Dabas)
        d_res = await client.get(f"/api/v1/analytics/players/{dabas_id}/performance")
        assert d_res.status_code == 200
        d_data = d_res.json()
        assert d_data["appearances"] == 0
        assert d_data["minutes_played"] == 0
        assert d_data["per_90"]["has_sufficient_minutes"] is False
        assert d_data["per_90"]["goals_per_90"] is None
        
        # Player comparison endpoint is removed
        cmp_res = await client.post(
            "/api/v1/analytics/players/compare",
            json={"player_a_id": yadwad_id, "player_b_id": tanque_id},
        )
        assert cmp_res.status_code in (404, 405)
