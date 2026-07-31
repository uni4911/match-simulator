from unittest.mock import MagicMock
from src.engine import MatchEngine, Match
from src.models import (
    FieldPlayer, Goalkeeper, Position, Team, MatchTeam, FORMATION_433
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

    assert drain_active > drain_passive

    assert pytest.approx(drain_active, rel=1e-5) == drain_passive * 2.5