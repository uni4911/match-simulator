import pytest
from src.models import League, Team, FieldPlayer, Position, Goalkeeper
from src.engine import MatchEngine
from src.league_engine import LeagueEngine

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
