import pytest
from fastapi import HTTPException
from src.models import (FieldPlayer, Goalkeeper, Position, MatchPlayer, 
                        PlayerSeasonStats, Team, FORMATION_433, MatchTeam,
                        get_formation_positions)
from src.engine.engine import Match, MatchEngine
from src.engine.league_engine import LeagueEngine
from src.models import League
from main import get_player_profile, league_start, match_options, play_league_match, _find_player_in_all_teams
from api.schemas import CreateLeagueRequest, PlayLeagueMatch

def test_match_player_minutes_and_bio():
    player = FieldPlayer(
        full_name="Jan Kowalski",
        short_name="Kowalski",
        position=Position.STRIKER,
        pace=85,
        shooting=88,
        passing=75,
        dribbling=82,
        defending=40,
        physical=78,
        heading=80,
        age=25,
        nationality="Poland",
        height=184,
        overall=84
    )
    mp = MatchPlayer(player)
    assert mp.minutes_played == 0
    assert mp.age == 25
    assert mp.nationality == "Poland"
    assert mp.height == 184
    assert mp.overall > 50

    # Advance stamina / seconds
    mp.seconds_played = 2700 # 45 minutes
    assert mp.minutes_played == 45

    mp.seconds_played = 5400 # 90 minutes
    assert mp.minutes_played == 90

def test_player_season_stats_minutes_and_attributes():
    player = FieldPlayer(
        full_name="Piotr Zielinski",
        short_name="Zielinski",
        position=Position.CENTRAL_MIDFIELDER,
        pace=78,
        shooting=80,
        passing=86,
        dribbling=85,
        defending=65,
        physical=70,
        heading=60,
        age=29,
        nationality="Poland",
        height=180
    )
    season_stats = PlayerSeasonStats(player, team_name="Inter")
    assert season_stats.minutes_played == 0
    assert season_stats.age == 29
    assert season_stats.nationality == "Poland"
    assert "pace" in season_stats.attributes
    assert season_stats.attributes["passing"] == 86

    mp = MatchPlayer(player)
    mp.seconds_played = 3600 # 60 minutes
    mp.goals = 1
    mp.assists = 1

    season_stats.register_match_player(mp)
    assert season_stats.matches_played == 1
    assert season_stats.minutes_played == 60
    assert season_stats.goals == 1
    assert season_stats.assists == 1

def test_goalkeeper_season_stats():
    gk = Goalkeeper(
        full_name="Wojciech Szczesny",
        short_name="Szczesny",
        diving=84,
        handling=82,
        kicking=75,
        reflexes=86,
        speed=50,
        positioning=85,
        age=34,
        nationality="Poland",
        height=195
    )
    season_stats = PlayerSeasonStats(gk, team_name="Barcelona")
    assert season_stats.is_goalkeeper == True
    assert "diving" in season_stats.attributes
    assert season_stats.attributes["reflexes"] == 86

def test_find_player_in_all_teams():
    p, team = _find_player_in_all_teams("Bramkarz")
    assert p is not None
    assert team is not None

def test_get_player_profile_endpoint():
    options = match_options()
    teams = options["teams"]
    assert len(teams) >= 2

    # Start a league to generate fixtures
    create_req = CreateLeagueRequest(
        league_name="Profil Liga Test",
        league_teams=teams[:3] if len(teams) >= 3 else teams,
        double_round=False
    )
    league_start(create_req)

    # Play first match
    play_league_match(PlayLeagueMatch(match_index=0))

    # Find a player in first team
    from main import league
    assert league is not None
    first_team = league.teams[0]
    sample_player = getattr(first_team.players[0], "player", first_team.players[0])

    profile = get_player_profile(sample_player.name, first_team.name)
    assert profile.player_name == sample_player.name
    assert profile.team_name == first_team.name
    assert profile.position == sample_player.position.name
    assert profile.age == sample_player.age
    assert profile.nationality == sample_player.nationality
    assert profile.height == sample_player.height
    assert profile.overall > 0
    assert len(profile.attributes) > 0
    assert len(profile.match_history) > 0

    # Verify match history log fields
    first_log = profile.match_history[0]
    assert first_log.round_number >= 1
    assert first_log.home_team_name != ""
    assert first_log.away_team_name != ""
    assert first_log.result in ["W", "D", "L", "-"]

def test_get_player_profile_invalid_name():
    with pytest.raises(HTTPException) as exc_info:
        get_player_profile("NonExistentPlayerXYZ12345")
    assert exc_info.value.status_code == 404
