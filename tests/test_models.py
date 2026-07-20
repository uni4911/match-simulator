from models import FieldPlayer, Position, Goalkeeper
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