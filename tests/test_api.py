from main import match_options, start_match, match_status, match_tick
from api.schemas import StartMatchRequest

def test_get_match_options():
    data = match_options()
    assert "teams" in data
    assert "formations" in data
    assert len(data["teams"]) >= 2
    assert "4-3-3" in data["formations"]

def test_start_match_and_tick():
    options = match_options()
    teams = options["teams"]

    req = StartMatchRequest(
        home_team_name=teams[0],
        away_team_name=teams[1],
        home_formation="4-4-2",
        away_formation="4-3-3"
    )
    start_data = start_match(req)
    assert start_data["home_team_name"] == teams[0]
    assert start_data["away_team_name"] == teams[1]
    assert start_data["home_score"] == 0
    assert start_data["away_score"] == 0
    assert start_data["current_minute"] == 0
    assert start_data["is_finished"] == False

    tick_data = match_tick()
    assert tick_data["home_team_name"] == teams[0]
    assert tick_data["away_team_name"] == teams[1]

def test_start_match_invalid_team():
    import pytest
    from fastapi import HTTPException

    req = StartMatchRequest(
        home_team_name="NonExistentTeam",
        away_team_name="CF Java"
    )
    with pytest.raises(HTTPException) as exc_info:
        start_match(req)
    assert exc_info.value.status_code == 400

def test_team_stats():
    from main import team_stats
    stats = team_stats()
    assert "home_team_name" in stats
    assert "away_team_name" in stats
    assert "home_players" in stats
    assert "away_players" in stats
    assert len(stats["home_players"]) > 0
    player = stats["home_players"][0]
    assert hasattr(player, "name") or "name" in player
    assert hasattr(player, "yellow_cards") or "yellow_cards" in player
