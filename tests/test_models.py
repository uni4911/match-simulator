from src.models import FieldPlayer, Position, Goalkeeper, MatchPlayer, MatchTeam
import pytest



@pytest.mark.parametrize("name , position, pace, shooting, passing, dribbling, defending, physical, overall",
    [("Test",Position.STRIKER,90,82,75,75,40,68,82),
     ("Test",Position.CENTRE_BACK,70,55,65,50,90,85,81),
     ("Test", Position.CENTRAL_ATTACKING_MIDFIELDER,75,70,85,85,65,55,78)])

def test_field_player_overall_calculation(name: str,position: Position, pace: int, shooting: int, passing: int, dribbling: int, defending: int, physical: int, overall:int) -> None:
    playerA = FieldPlayer(name,position,pace,shooting,passing,dribbling,defending, physical)
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
        pace=80, shooting=85, passing=70, dribbling=75, defending=30, physical=70
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