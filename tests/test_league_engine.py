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


def test_card_suspension_forces_bench_rotation():
    gk = Goalkeeper("GK Team", 80, 80, 70, 85, 60, 80)
    star = FieldPlayer("Star Striker", Position.CENTRAL_FORWARD, 90, 90, 85, 85, 40, 85, 80, 185)
    backup = FieldPlayer("Backup Striker", Position.CENTRAL_FORWARD, 80, 80, 75, 75, 40, 75, 75, 180)
    other_fps = [
        FieldPlayer(f"Field {i}", pos, 75, 75, 75, 75, 75, 75, 75, 180)
        for i, pos in enumerate([
            Position.CENTRE_BACK, Position.CENTRE_BACK, Position.LEFT_BACK, Position.RIGHT_BACK,
            Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
            Position.LEFT_WING, Position.RIGHT_WING
        ])
    ]
    bench_extra = [
        FieldPlayer("Extra Sub 1", Position.CENTRE_BACK, 70, 70, 70, 70, 70, 70, 70, 180),
        FieldPlayer("Extra Sub 2", Position.CENTRAL_MIDFIELDER, 70, 70, 70, 70, 70, 70, 70, 180)
    ]
    team = Team("Suspension FC", [gk, star, backup] + other_fps + bench_extra)

    opp_gk = Goalkeeper("Opp GK", 80, 80, 70, 85, 60, 80)
    opp_fps = [FieldPlayer(f"Opp {i}", pos, 75, 75, 75, 75, 75, 75, 75, 180) for i, pos in enumerate(Position)]
    opp_team = Team("Opponent FC", [opp_gk] + opp_fps)

    league = League(name="Suspension League", teams=[team, opp_team])
    engine = LeagueEngine(league, MatchEngine())
    engine.generate_fixture(double_round=False)

    # Manually trigger a 1-match suspension on star player (e.g. red card)
    star.suspension_matches_remaining = 1
    assert star.is_suspended is True

    # Play match while star is suspended
    match = league.fixtures[0]
    engine.play_match(match)

    susp_match_team = match.home_team if match.home_team.team.name == "Suspension FC" else match.away_team
    starters = [p.player.full_name for p in susp_match_team.match_players if p.is_starter]
    # Star should NOT have started, and Backup should have started
    assert "Star Striker" not in starters
    assert "Backup Striker" in starters
    
    # After match, suspension should be cleared
    assert star.suspension_matches_remaining == 0
    assert star.is_suspended is False



