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


def test_player_rotation_and_substitutions():
    # Team with 1 GK + 16 Field Players (squad depth allows rotation)
    gk = Goalkeeper("GK Team A", 80, 80, 70, 85, 60, 80)
    field_players = [
        FieldPlayer(f"Starter {i}", Position.CENTRAL_MIDFIELDER, 80, 80, 80, 80, 80, 80, 80, 180) for i in range(10)
    ] + [
        FieldPlayer(f"Backup {i}", Position.CENTRAL_MIDFIELDER, 76, 76, 76, 76, 76, 76, 76, 180) for i in range(6)
    ]
    team_a = Team("Team A", [gk] + field_players)

    gkB = Goalkeeper("GK Team B", 80, 80, 70, 85, 60, 80)
    field_playersB = [
        FieldPlayer(f"Opponent {i}", Position.CENTRAL_MIDFIELDER, 75, 75, 75, 75, 75, 75, 75, 180) for i in range(15)
    ]
    team_b = Team("Team B", [gkB] + field_playersB)

    league = League(name="Rotation Test League", teams=[team_a, team_b])
    engine = LeagueEngine(league, MatchEngine())

    # Simulate 8 matches between Team A and Team B
    starters_per_match = []
    substitutions_made = 0

    for _ in range(8):
        engine.generate_fixture(double_round=False)
        m = league.fixtures[0]
        engine.play_match(m)

        sub_events = [e for e in m.match_events if e.__class__.__name__ == 'Substitution']
        for sub in sub_events:
            # Ensure Goalkeeper was NEVER substituted off
            assert "GK Team A" not in sub.subbed_off, "Goalkeeper should never be substituted for stamina/tactical reasons"
            assert "GK Team B" not in sub.subbed_off, "Goalkeeper should never be substituted for stamina/tactical reasons"

        substitutions_made += len(sub_events)
        starters = [p.player.full_name for p in m.home_team.players_on_field if p.is_starter]
        starters_per_match.append(set(starters))

    # Verify substitutions took place during matches
    assert substitutions_made > 0, "Substitutions should occur during matches"

    # Verify starting lineup rotated across matches (different starting sets across rounds)
    unique_lineups = len(set(frozenset(s) for s in starters_per_match))
    assert unique_lineups > 1, "Starting 11 must rotate across fixtures due to fitness changes"

    # Check that player fitnesses stay within realistic bounds [0.50, 1.00]
    for p in team_a.players:
        assert 0.50 <= p.fitness <= 1.00


