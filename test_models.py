from models import FieldPlayer, Position
import pytest

@pytest.mark.parametrize("name , position, pace, shooting, passing, dribbling, defending, physical, overall",
    [("Test",Position.ATTACKER,90,82,75,75,40,68,82),
     ("Test",Position.DEFENDER,70,55,65,50,90,85,81),
     ("Test", Position.MIDFIELDER,75,70,85,85,65,55,78)])

def test_field_player_overall_calculation(name: str,position: Position, pace: int, shooting: int, passing: int, dribbling: int, defending: int, physical: int, overall:int) -> None:
    playerA = FieldPlayer(name,position,pace,shooting,passing,dribbling,defending, physical)
    playerA_overall = playerA.overall
    
    assert playerA_overall == overall


