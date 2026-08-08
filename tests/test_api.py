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

def test_league_endpoints():
    from main import league_start, league_table, play_league_match, match_options
    from api.schemas import CreateLeagueRequest, PlayLeagueMatch

    options = match_options()
    teams = options["teams"]
    assert len(teams) >= 2

    create_req = CreateLeagueRequest(
        league_name="Testowa Liga",
        league_teams=teams[:3] if len(teams) >= 3 else teams,
        double_round=False
    )
    start_resp = league_start(create_req)
    assert start_resp["name"] == "Testowa Liga"
    assert len(start_resp["table"]) == len(create_req.league_teams)
    assert len(start_resp["fixtures"]) > 0

    table_resp = league_table()
    assert table_resp["name"] == "Testowa Liga"
    assert hasattr(table_resp["table"][0], "form")
    assert hasattr(table_resp["table"][0], "recent_results")

    play_req = PlayLeagueMatch(match_index=0)
    match_resp = play_league_match(play_req)
    assert match_resp["fixtures"][0]["is_finished"] == True
    assert "player_stats" in match_resp
    assert len(match_resp["player_stats"]) > 0
    # Check that teams involved in the played match have form updated
    played_teams_forms = [getattr(t, "form", None) for t in match_resp["table"] if getattr(t, "matches_played", 0) > 0]
    assert len(played_teams_forms) > 0
    assert len(played_teams_forms[0]) > 0

    from main import get_league_player_stats, start_league_match_live
    player_stats_resp = get_league_player_stats("goals")
    assert len(player_stats_resp) > 0

    live_req = PlayLeagueMatch(match_index=1)
    live_resp = start_league_match_live(live_req)
    assert "home_team_name" in live_resp
    assert "away_team_name" in live_resp
