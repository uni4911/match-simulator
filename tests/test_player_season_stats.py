import pytest
from src.models import (FieldPlayer, Goalkeeper, Position, MatchPlayer, 
                        MatchTeam, Team, League, PlayerSeasonStats)
from src.engine.engine import Match, MatchEngine
from src.engine.league_engine import LeagueEngine


def test_player_season_stats_accumulation():
    player = FieldPlayer("Jan Kowalski", Position.STRIKER, 80, 80, 70, 75, 40, 70, 75, 180)
    season_stats = PlayerSeasonStats(player)

    mp = MatchPlayer(player)
    mp.goals = 2
    mp.assists = 1
    mp.receive_card('yellow_card')
    mp.passes = 15

    season_stats.register_match_player(mp, team_conceded_zero=False)

    assert season_stats.matches_played == 1
    assert season_stats.goals == 2
    assert season_stats.assists == 1
    assert season_stats.yellow_cards == 1
    assert season_stats.red_cards == 0
    assert season_stats.passes == 15
    assert season_stats.player_name == "Jan Kowalski"
    assert season_stats.position == "STRIKER"

    # Second match
    mp2 = MatchPlayer(player)
    mp2.goals = 1
    mp2.receive_card('yellow_card')
    mp2.receive_card('yellow_card')  # Red card
    season_stats.register_match_player(mp2, team_conceded_zero=False)

    assert season_stats.matches_played == 2
    assert season_stats.goals == 3
    assert season_stats.yellow_cards == 3
    assert season_stats.red_cards == 1


def test_goalkeeper_clean_sheet_tracking():
    gk = Goalkeeper("Wojciech Szczęsny", 85, 80, 75, 88, 50, 84)
    season_stats = PlayerSeasonStats(gk)

    mp = MatchPlayer(gk)
    season_stats.register_match_player(mp, team_conceded_zero=True)
    assert season_stats.clean_sheets == 1

    season_stats.register_match_player(mp, team_conceded_zero=False)
    assert season_stats.clean_sheets == 1


def test_league_engine_player_stats_integration():
    from src.db.loader import load_all_teams
    loaded_teams = load_all_teams("data.json")
    teams = list(loaded_teams.values())[:2]

    league = League("Test League", teams)
    for team_obj in teams:
        league.table[team_obj] = __import__("src.models", fromlist=["LeagueTeamStats"]).LeagueTeamStats(team_obj)

    league_engine = LeagueEngine(league, MatchEngine())
    league_engine.generate_fixture(double_round=False)

    match = league.fixtures[0]
    league_engine.play_match(match)

    assert len(league.player_stats) > 0
    top_scorers = league_engine.get_top_scorers()
    assert len(top_scorers) > 0
    assert top_scorers[0].matches_played == 1
    
    top_ratings = league_engine.get_top_ratings()
    assert len(top_ratings) > 0
    assert top_ratings[0].average_rating >= 1.0

    top_motm = league_engine.get_top_motm()
    assert len(top_motm) > 0
    # There should be exactly 1 MOTM from the played match
    motm_total = sum(p.motm_awards for p in league.player_stats.values())
    assert motm_total == 1


def test_player_season_stats_rating_and_motm_accumulation():
    player = FieldPlayer("Robert Lewandowski", Position.STRIKER, 85, 91, 78, 86, 44, 82, 78, 185)
    season_stats = PlayerSeasonStats(player)

    mp1 = MatchPlayer(player)
    mp1.rating = 8.5
    season_stats.register_match_player(mp1, is_motm=True)

    assert season_stats.matches_played == 1
    assert season_stats.average_rating == 8.5
    assert season_stats.motm_awards == 1

    mp2 = MatchPlayer(player)
    mp2.rating = 6.5
    season_stats.register_match_player(mp2, is_motm=False)

    assert season_stats.matches_played == 2
    assert season_stats.average_rating == 7.5
    assert season_stats.motm_awards == 1

