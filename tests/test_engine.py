from unittest.mock import MagicMock
from src.engine import MatchEngine, Match
from src.models import (
    FieldPlayer, Goalkeeper, Position, Team, MatchTeam, MatchPlayer, FORMATION_433
)
from src.commentator import Commentator
import pytest
from src.events import MatchEndEvent

@pytest.fixture
def sample_home_team() -> MatchTeam:
    
    gk = Goalkeeper(
        name="Bramkarz Dom", 
        diving=80, handling=80, kicking=70, 
        reflexes=85, speed=60, positioning=80
    )
    
    field_players = [
        FieldPlayer(
            name=f"Gracz Dom {i}",
            position=pos,
            pace=75, shooting=70, passing=75, 
            dribbling=75, defending=70, physical=75, heading=70, height=180
        )
        for i, pos in enumerate(FORMATION_433)
    ]

    team = Team(name="Gospodarze FC", players=[gk] + field_players)
    return MatchTeam(team=team, formation=FORMATION_433)

@pytest.fixture
def sample_away_team() -> MatchTeam:
    
    gk = Goalkeeper(
        name="Bramkarz Wyjazd", 
        diving=80, handling=80, kicking=70, 
        reflexes=85, speed=60, positioning=80
    )
    
    field_players = [
        FieldPlayer(
            name=f"Gracz Wyjazd {i}",
            position=pos,
            pace=75, shooting=70, passing=75, 
            dribbling=75, defending=70, physical=75, heading=70, height=180
        )
        for i, pos in enumerate(FORMATION_433)
    ]

    team = Team(name="Wyjazd FC", players=[gk] + field_players)
    return MatchTeam(team=team, formation=FORMATION_433)


def test_play_match_adds_match_end_event(sample_home_team: MatchTeam, sample_away_team: MatchTeam):
    mock_commentator = MagicMock()
    home_team = sample_home_team
    away_team = sample_away_team

    match = Match(home_team, away_team)
    engine = MatchEngine(mock_commentator, 0.1)
    engine.play_match(match)

    assert isinstance(match.match_events[-1], MatchEndEvent)
    assert match.current_second >= match.max_second

def test_team_active_players_decreases_after_red_card(sample_home_team):
    test_player = sample_home_team.players_on_field[0]
    test_player.receive_card('red_card')

    assert len(sample_home_team.active_players) == 9
    
    assert test_player not in sample_home_team.active_players

def test_cannot_substitute_red_carded_player(sample_home_team):
    test_player = sample_home_team.players_on_field[0]
    test_player.receive_card('red_card')

    assert not sample_home_team.make_substitution(test_player, sample_home_team.bench_players[0])
    assert not sample_home_team.make_substitution(sample_home_team.active_players[1], test_player)

def test_substitution_limit_exceeded(sample_home_team):
    sample_home_team.substitution_limit = 0
    test_player = sample_home_team.players_on_field[0]

    assert not sample_home_team.make_substitution(test_player, sample_home_team.bench_players[0])

def test_stamina_does_not_drop_below_zero(sample_home_team):
    sample_home_team.update_stamina(100000)

    assert sample_home_team.active_players[0].current_stamina == 0.0

def test_active_player_drains_more_stamina(sample_home_team: MatchTeam):
    active_player = sample_home_team.active_players[0]
    passive_player = sample_home_team.active_players[1]

    active_player.player.base_physical = 75
    passive_player.player.base_physical = 75

    initial_stamina_active = active_player.current_stamina
    initial_stamina_passive = passive_player.current_stamina
  
    seconds_passed = 100
    sample_home_team.update_stamina(seconds_passed, [active_player])

    drain_active = initial_stamina_active - active_player.current_stamina
    drain_passive = initial_stamina_passive - passive_player.current_stamina

    assert pytest.approx(drain_active, rel=1e-5) == drain_passive * 2.5

def test_handle_injury_forced_substitution(sample_home_team: MatchTeam):
    bench_fp = FieldPlayer("Rezerwowy 1", Position.CENTRE_BACK, 70, 70, 70, 70, 70, 70, 70, 180)
    bench_mp = MatchPlayer(bench_fp)
    sample_home_team.match_players.append(bench_mp)
    sample_home_team.bench_players.append(bench_mp)

    injured_player = sample_home_team.players_on_field[0]
    initial_on_field = len(sample_home_team.players_on_field)
    
    sub_res = sample_home_team.handle_injury(injured_player, severity="severe")
    
    assert sub_res is not None
    p_off, p_in = sub_res
    assert p_off == injured_player
    assert p_in in sample_home_team.players_on_field
    assert injured_player not in sample_home_team.players_on_field
    assert len(sample_home_team.players_on_field) == initial_on_field

def test_handle_injury_reduces_active_players_when_no_subs(sample_home_team: MatchTeam):
    sample_home_team.substitution_limit = 0
    injured_player = sample_home_team.players_on_field[0]
    initial_active = len(sample_home_team.active_players)

    sub_res = sample_home_team.handle_injury(injured_player, severity="severe")

    assert sub_res is None
    assert injured_player.is_forced_off == True
    assert len(sample_home_team.active_players) == initial_active - 1

def test_process_injury_risk_adds_injury_event(sample_home_team: MatchTeam, sample_away_team: MatchTeam):
    from src.events import InjuryEvent
    match = Match(sample_home_team, sample_away_team)
    target_player = sample_home_team.players_on_field[0]

    # Force 100% injury chance by mocking random
    import unittest.mock as mock
    with mock.patch("random.random", return_value=0.0001):
        match.process_injury_risk(target_player, foul_punishment="red_card")

    injury_events = [e for e in match.match_events if isinstance(e, InjuryEvent)]
    assert len(injury_events) == 1
    assert injury_events[0].player == target_player.player.name

def test_match_team_get_winger_and_get_cam(sample_home_team: MatchTeam):
    winger = sample_home_team.get_winger()
    cam = sample_home_team.get_cam()
    assert winger is not None
    assert cam is not None
    assert winger in sample_home_team.active_players
    assert cam in sample_home_team.active_players

def test_new_match_states_execution(sample_home_team: MatchTeam, sample_away_team: MatchTeam):
    from src.engine import BuildUp, WingAttack, LongShot
    match = Match(sample_home_team, sample_away_team)
    match.player_with_ball = sample_home_team.active_players[0]

    buildup_state = BuildUp()
    next_state = buildup_state.execute(match)
    assert next_state is not None

    wing_state = WingAttack()
    next_state_wing = wing_state.execute(match)
    assert next_state_wing is not None

    long_shot_state = LongShot()
    next_state_ls = long_shot_state.execute(match)
    assert next_state_ls is not None


def test_play_match_tracks_team_stats(sample_home_team: MatchTeam, sample_away_team: MatchTeam):
    mock_commentator = MagicMock()
    match = Match(sample_home_team, sample_away_team)
    engine = MatchEngine(mock_commentator, 0.1)
    engine.play_match(match)

    home_stats = sample_home_team.stats
    away_stats = sample_away_team.stats

    total_possession = home_stats.possession_time + away_stats.possession_time
    assert total_possession > 0
    assert pytest.approx(home_stats.get_possession_percentage(away_stats) + away_stats.get_possession_percentage(home_stats), abs=0.2) == 100.0
    assert home_stats.passes >= 0
    assert away_stats.passes >= 0