import pytest
from src.models import League, Team, FieldPlayer, Position, Goalkeeper
from src.engine.engine import MatchEngine
from src.engine.league_engine import LeagueEngine

def create_dummy_team(name: str) -> Team:
    gk = Goalkeeper(f"GK {name}", 80, 80, 70, 85, 60, 80)
    field_players = [
        FieldPlayer(f"P {name} {i}", Position.STRIKER, 75, 70, 75, 75, 70, 75, 70, 180)
        for i in range(10)
    ]
    return Team(name, [gk] + field_players)

def test_fixture_generation_even_teams():
    teams = [create_dummy_team(f"Team {i}") for i in range(20)]
    league = League(name="Even League", teams=teams)
    engine = LeagueEngine(league, MatchEngine())
    engine.generate_fixture(double_round=True)
    
    # 20 teams -> 19 rounds per leg * 10 matches per round = 190 matches per leg -> 380 total matches
    assert len(league.fixtures) == 380
    
    # Each team should be present in 38 matches
    team_match_counts = {t.name: 0 for t in teams}
    for m in league.fixtures:
        team_match_counts[m.home_team.team.name] += 1
        team_match_counts[m.away_team.team.name] += 1
    
    for team_name, count in team_match_counts.items():
        assert count == 38

def test_fixture_generation_odd_teams():
    teams = [create_dummy_team(f"Team {i}") for i in range(19)]
    league = League(name="Odd League", teams=teams)
    engine = LeagueEngine(league, MatchEngine())
    engine.generate_fixture(double_round=True)
    
    # 19 teams -> 19 rounds per leg * 9 matches per round = 171 matches per leg -> 342 total matches
    assert len(league.fixtures) == 342
    
    # Each team should play 18 matches per leg (36 total)
    team_match_counts = {t.name: 0 for t in teams}
    for m in league.fixtures:
        team_match_counts[m.home_team.team.name] += 1
        team_match_counts[m.away_team.team.name] += 1
    
    for team_name, count in team_match_counts.items():
        assert count == 36

def test_fixture_generation_randomness():
    teams = [create_dummy_team(f"Team {i}") for i in range(10)]
    
    league1 = League(name="League 1", teams=list(teams))
    engine1 = LeagueEngine(league1, MatchEngine())
    engine1.generate_fixture(double_round=True)
    
    league2 = League(name="League 2", teams=list(teams))
    engine2 = LeagueEngine(league2, MatchEngine())
    engine2.generate_fixture(double_round=True)
    
    # Compare fixture pairings order between the two generated leagues
    pairings1 = [(m.home_team.team.name, m.away_team.team.name) for m in league1.fixtures]
    pairings2 = [(m.home_team.team.name, m.away_team.team.name) for m in league2.fixtures]
    
    # Assert that the fixtures are not identical in sequence
    assert pairings1 != pairings2

