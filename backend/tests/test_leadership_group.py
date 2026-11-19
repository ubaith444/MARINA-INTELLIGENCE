"""Test Chennaiyin FC Season Leadership Group."""

import pytest
from httpx import ASGITransport, AsyncClient
from marina.main import app


@pytest.mark.anyio
async def test_get_season_leadership_group():
    """Verify the 5-member leadership group for ISL 2026–27."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/teams/leadership-group")
        assert response.status_code == 200
        data = response.json()

        assert data["role_title"] == "Leadership Group"
        assert data["total_members"] == 5
        members = data["members"]
        assert len(members) == 5

        # Verify all 5 player names and positions
        member_map = {m["player_name"]: m for m in members}
        expected_names = [
            "Nuno Reis",
            "P. C. Laldinpuia",
            "Nikola Stojanović",
            "Samik Mitra",
            "Mohammad Nawaz",
        ]
        for name in expected_names:
            assert name in member_map, f"Missing {name} in leadership group"

        # Check positions
        assert member_map["Nuno Reis"]["position"] == "Defender"
        assert member_map["P. C. Laldinpuia"]["position"] == "Defender"
        assert member_map["Nikola Stojanović"]["position"] == "Midfielder"
        assert member_map["Samik Mitra"]["position"] == "Goalkeeper"
        assert member_map["Mohammad Nawaz"]["position"] == "Goalkeeper"

        # Verify role for all 5 is "Leadership Group" and not falsely labeled captain
        for m in members:
            assert m["leadership_role"] == "Leadership Group"
            assert m["is_captain"] is False, f"{m['player_name']} must not be arbitrarily designated captain in the leadership group"

        # Verify a leadership player's profile performance endpoint reflects leadership membership
        nawaz_id = member_map["Mohammad Nawaz"]["player_id"]
        perf_resp = await client.get(f"/api/v1/analytics/players/{nawaz_id}/performance")
        if perf_resp.status_code == 200:
            perf_data = perf_resp.json()
            assert perf_data.get("is_leadership_group") is True
            assert perf_data.get("leadership_role") == "Leadership Group"
