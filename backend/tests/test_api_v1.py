"""Automated Tests for API v1 Endpoints and Contracts."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_competition_and_teams(client: AsyncClient):
    """Test full workflow of creating competition, venue, teams, and retrieving them via REST."""
    # 1. Create Competition
    comp_res = await client.post(
        "/api/v1/competitions",
        json={
            "code": "ISL",
            "name": "Indian Super League",
            "country": "India",
            "federation": "AIFF",
            "tier": 1,
            "competition_type": "LEAGUE",
        },
    )
    assert comp_res.status_code == 201
    comp_data = comp_res.json()
    assert comp_data["code"] == "ISL"

    # 2. Create Season
    season_res = await client.post(
        "/api/v1/competitions/seasons",
        json={
            "competition_id": comp_data["id"],
            "name": "2026–27",
            "slug": "isl-2026-27",
            "start_date": "2026-09-15",
            "end_date": "2027-04-20",
            "is_current": True,
            "is_completed": False,
        },
    )
    assert season_res.status_code == 201
    season_data = season_res.json()
    assert season_data["slug"] == "isl-2026-27"

    # 3. Create Stadium Venue
    venue_res = await client.post(
        "/api/v1/teams/venues",
        json={
            "name": "Jawaharlal Nehru Stadium (Marina Arena)",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "India",
            "capacity": 40000,
        },
    )
    assert venue_res.status_code == 201
    venue_data = venue_res.json()

    # 4. Create Chennaiyin FC
    cfc_res = await client.post(
        "/api/v1/teams",
        json={
            "name": "Chennaiyin FC",
            "short_name": "CFC",
            "slug": "chennaiyin-fc",
            "founded_year": 2014,
            "primary_venue_id": venue_data["id"],
            "primary_color": "#003399",
            "secondary_color": "#FFFFFF",
        },
    )
    assert cfc_res.status_code == 201
    cfc_data = cfc_res.json()
    assert cfc_data["short_name"] == "CFC"

    # 5. Create Opponent Team (Kerala Blasters)
    kbfc_res = await client.post(
        "/api/v1/teams",
        json={
            "name": "Kerala Blasters FC",
            "short_name": "KBFC",
            "slug": "kerala-blasters-fc",
            "founded_year": 2014,
        },
    )
    assert kbfc_res.status_code == 201
    kbfc_data = kbfc_res.json()

    # 6. List Teams
    teams_list_res = await client.get("/api/v1/teams")
    assert teams_list_res.status_code == 200
    teams_list = teams_list_res.json()
    assert len(teams_list) >= 2

    # 7. Schedule Match Fixture (Upcoming 2026-27 season)
    match_res = await client.post(
        "/api/v1/matches",
        json={
            "season_id": season_data["id"],
            "home_team_id": cfc_data["id"],
            "away_team_id": kbfc_data["id"],
            "venue_id": venue_data["id"],
            "match_number": 1,
            "scheduled_kickoff": "2026-10-18T19:30:00Z",
            "match_status": "SCHEDULED",
            "home_score": None,
            "away_score": None,
        },
    )
    assert match_res.status_code == 201
    match_data = match_res.json()
    assert match_data["home_score"] is None
    assert match_data["away_score"] is None
    assert match_data["match_status"] == "SCHEDULED"

    # 8. Retrieve Match Detail
    detail_res = await client.get(f"/api/v1/matches/{match_data['id']}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["home_team"]["short_name"] == "CFC"
    assert detail["away_team"]["short_name"] == "KBFC"


@pytest.mark.asyncio
async def test_schedule_match_rejects_fake_scores(client: AsyncClient):
    """Verify that posting non-null scores for a SCHEDULED match via REST returns 400 Bad Request."""
    # Create required parent records
    comp = (await client.post("/api/v1/competitions", json={"code": "ISL", "name": "ISL"})).json()
    season = (await client.post(
        "/api/v1/competitions/seasons",
        json={"competition_id": comp["id"], "name": "2026–27", "slug": "isl-2026-27"},
    )).json()
    t1 = (await client.post("/api/v1/teams", json={"name": "Team A", "short_name": "TA", "slug": "team-a"})).json()
    t2 = (await client.post("/api/v1/teams", json={"name": "Team B", "short_name": "TB", "slug": "team-b"})).json()

    bad_match_res = await client.post(
        "/api/v1/matches",
        json={
            "season_id": season["id"],
            "home_team_id": t1["id"],
            "away_team_id": t2["id"],
            "scheduled_kickoff": "2026-11-01T19:30:00Z",
            "match_status": "SCHEDULED",
            "home_score": 3,  # Invalid for SCHEDULED fixture
            "away_score": 0,
        },
    )
    assert bad_match_res.status_code == 400
    assert "Cannot assign scores to a SCHEDULED fixture" in bad_match_res.json()["detail"]
