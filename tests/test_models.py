from src.models import FieldPlayer, Position, Goalkeeper, MatchPlayer, MatchTeam
import pytest



@pytest.mark.parametrize("name , position, pace, shooting, passing, dribbling, defending, physical, overall, heading, height",
    [("Test",Position.STRIKER,90,82,75,75,40,68,82,75,180),
     ("Test",Position.CENTRE_BACK,70,55,65,50,90,85,81,75,180),
     ("Test", Position.CENTRAL_ATTACKING_MIDFIELDER,75,70,85,85,65,55,78,75,180)])

def test_field_player_overall_calculation(name: str,position: Position, pace: int, shooting: int, passing: int, dribbling: int, defending: int, physical: int, overall:int, heading: int, height: int) -> None:
    playerA = FieldPlayer(name,position,pace,shooting,passing,dribbling,defending, physical,heading,height)
    playerA_overall = playerA.overall
    
    assert playerA_overall == overall

@pytest.mark.parametrize("reflexes, positioning, expected_score",[(85,90,87),(80,85,82)])

def test_goalkeeping_score(reflexes: int, positioning: int, expected_score: int):
    player_test = Goalkeeper("Test",0,0,0,reflexes,0,positioning)
    score = player_test.goalkeeping_score

    assert score == expected_score
@pytest.fixture
def fresh_match_player() -> MatchPlayer:
    player = FieldPlayer(
        name="Jan Kowalski", 
        position=Position.STRIKER, 
        pace=80, shooting=85, passing=70, dribbling=75, defending=30, physical=70,heading=70, height=180
    )
    return MatchPlayer(player)

def test_receive_first_yellow_card(fresh_match_player: MatchPlayer):
    fresh_match_player.receive_card('yellow_card')

    assert fresh_match_player.yellow_card == 1
    assert fresh_match_player.has_red_card == False

def test_receive_two_yellow_cards(fresh_match_player: MatchPlayer):
    fresh_match_player.receive_card('yellow_card')
    fresh_match_player.receive_card('yellow_card')

    assert fresh_match_player.yellow_card == 2 
    assert fresh_match_player.has_red_card == True

def test_receive_red_cards(fresh_match_player: MatchPlayer):
    fresh_match_player.receive_card('red_card')

    assert fresh_match_player.yellow_card == 0  
    assert fresh_match_player.has_red_card == True

def test_minor_injury_stat_penalty(fresh_match_player: MatchPlayer):
    base_shooting = fresh_match_player.shooting
    fresh_match_player.is_injured = True
    fresh_match_player.injury_severity = "minor"
    assert fresh_match_player.shooting < base_shooting
    assert fresh_match_player.stat_modifier < 1.0

def test_severe_injury_forced_off(fresh_match_player: MatchPlayer):
    fresh_match_player.is_injured = True
    fresh_match_player.injury_severity = "severe"
    fresh_match_player.is_forced_off = True
    assert fresh_match_player.is_forced_off == True

def test_all_formations_initialization():
    from src.models import AVAILABLE_FORMATIONS, Team
    from src.db.loader import load_file
    players = load_file("data.json", "Python FC")
    team = Team("Python FC", players)

    for name, formation in AVAILABLE_FORMATIONS.items():
        match_team = MatchTeam(team, formation)
        assert len(match_team.players_on_field) == 10
        assert match_team.formation == formation


def test_team_stats_match_defaults_and_total_shots():
    from src.models import TeamStatsMatch
    stats = TeamStatsMatch()
    assert stats.possession_time == 0.0
    assert stats.shots_on_target == 0
    assert stats.shots_off_target == 0
    assert stats.total_shots == 0
    assert stats.fouls == 0
    assert stats.passes == 0
    assert stats.corners == 0
    assert stats.saves == 0

    stats.shots_on_target = 5
    stats.shots_off_target = 3
    assert stats.total_shots == 8


def test_possession_percentage_calculation():
    from src.models import TeamStatsMatch
    home_stats = TeamStatsMatch()
    away_stats = TeamStatsMatch()

    assert home_stats.get_possession_percentage(away_stats) == 50.0

    home_stats.possession_time = 300.0
    away_stats.possession_time = 200.0

    assert home_stats.get_possession_percentage(away_stats) == 60.0
    assert away_stats.get_possession_percentage(home_stats) == 40.0


def test_team_stats_match_reset_and_to_dict():
    from src.models import TeamStatsMatch
    stats = TeamStatsMatch()
    stats.possession_time = 150.0
    stats.shots_on_target = 4
    stats.shots_off_target = 2
    stats.fouls = 3
    stats.passes = 120
    stats.goals = 2

    opponent = TeamStatsMatch()
    opponent.possession_time = 150.0

    d = stats.to_dict(opponent)
    assert d["possession_percentage"] == 50.0
    assert d["shots_on_target"] == 4
    assert d["total_shots"] == 6
    assert d["fouls"] == 3
    assert d["passes"] == 120

    stats.reset()
    assert stats.possession_time == 0.0
    assert stats.shots_on_target == 0
    assert stats.fouls == 0