from __future__ import annotations
import random
from enum import Enum, auto
from typing import Optional, Final

class Position(Enum):
    GOALKEEPER = auto()
    LEFT_BACK = auto()
    CENTRE_BACK = auto()
    RIGHT_BACK = auto()
    LEFT_WING_BACK = auto()
    RIGHT_WING_BACK = auto()
    CENTRAL_DEFENSIVE_MIDFIELDER = auto()
    CENTRAL_MIDFIELDER = auto()
    CENTRAL_ATTACKING_MIDFIELDER = auto()
    LEFT_MIDFIELDER = auto()
    RIGHT_MIDFIELDER = auto()
    LEFT_WING = auto()
    CENTRAL_FORWARD = auto()
    RIGHT_WING = auto()
    STRIKER = auto()

DEFENDER_WEIGHTS : Final[dict[Position, int]] = { 
    Position.LEFT_BACK: 10,
    Position.CENTRE_BACK: 10,
    Position.RIGHT_BACK: 10,
    Position.LEFT_WING_BACK: 10,
    Position.RIGHT_WING_BACK: 10,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER: 10,
    Position.CENTRAL_MIDFIELDER: 4,
    Position.CENTRAL_ATTACKING_MIDFIELDER: 4,
    Position.LEFT_MIDFIELDER: 4,
    Position.RIGHT_MIDFIELDER: 4
}
DEFAULT_DEFENDER_WEIGHT = 1

MIDFIELDER_WEIGHTS: Final[dict[Position, int]] = {
    Position.CENTRAL_DEFENSIVE_MIDFIELDER: 10,
    Position.CENTRAL_MIDFIELDER: 10,
    Position.CENTRAL_ATTACKING_MIDFIELDER: 10,
    Position.LEFT_MIDFIELDER: 10,
    Position.RIGHT_MIDFIELDER: 10,
    Position.LEFT_BACK: 4,
    Position.CENTRE_BACK: 4,
    Position.RIGHT_BACK: 4,
    Position.LEFT_WING_BACK: 4,
    Position.RIGHT_WING_BACK: 4
    
}
DEFAULT_MIDFIELDER_WEIGHT = 1

ATTACKER_WEIGHTS: Final[dict[Position, int]] = {
    Position.LEFT_WING: 10,
    Position.CENTRAL_FORWARD: 10,
    Position.RIGHT_WING: 10,
    Position.STRIKER: 10,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER: 4,
    Position.CENTRAL_MIDFIELDER: 4,
    Position.CENTRAL_ATTACKING_MIDFIELDER: 4,
    Position.LEFT_MIDFIELDER: 4,
    Position.RIGHT_MIDFIELDER: 4
}
DEFAULT_ATTACKER_WEIGHT = 1

ATTACKING_POSITIONS = [Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING, Position.CENTRAL_FORWARD]
MIDFIELD_POSITIONS = [Position.LEFT_MIDFIELDER, Position.RIGHT_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER]
DEFENCE_POSITIONS = [Position.LEFT_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK, Position.LEFT_WING_BACK, Position.RIGHT_WING_BACK]
class Player:
    def __init__(self, name: str, position: Position):
        self.name :str = name
        self.position : Position= position
    

class Team:
    def __init__(self, name: str, players: list[Player]):
        self.name : str = name 
        self.players : list[Player] = players
        if len([player for player in self.players if isinstance(player, Goalkeeper)]) != 1:
            raise ValueError("Choose only one goalkeeper")
        self.field_players : list[Player] = [field_player for field_player in self.players if isinstance(field_player, FieldPlayer)]
        self.goalkeeper : Player = next((player for player in self.players if isinstance(player, Goalkeeper)),None) 
        
    def get_goalkeeper(self) -> 'Player':
       return self.goalkeeper

    def _get_weighted_player(self, weights_dict: dict[Position, int], default_weight: int) -> 'Player':
        weights: list[int] = [weights_dict.get(player.position, default_weight) for player in self.field_players]          
        return random.choices(self.field_players, weights,k=1)[0]
    
    def get_defender(self) -> 'Player':
        return  self._get_weighted_player(DEFENDER_WEIGHTS, DEFAULT_DEFENDER_WEIGHT)
    
    def get_midfielder(self) -> 'Player':
        return self._get_weighted_player(MIDFIELDER_WEIGHTS, DEFAULT_MIDFIELDER_WEIGHT)
    
    def get_attacker(self) -> 'Player':
         return self._get_weighted_player(ATTACKER_WEIGHTS, DEFAULT_ATTACKER_WEIGHT)

    def has_player(self, player: Player) -> bool:
        return player in self.players

    def get_penalty_taker(self) -> 'Player':
        return max(self.field_players, key=lambda player: player.shooting)

    def get_freekick_taker(self) -> 'Player':
        return max(self.field_players, key=lambda player: player.passing)


class FieldPlayer(Player):
    def __init__(self, name: str, position: Position, pace: int, shooting: int, passing: int, dribbling: int, defending: int, physical: int):
        super().__init__(name, position)
        self.pace : int = pace
        self.shooting : int = shooting
        self.passing : int = passing
        self.dribbling : int = dribbling
        self.defending : int = defending
        self.physical : int = physical

    @property
    def overall(self) -> int:
        if self.position in ATTACKING_POSITIONS:
            return round((self.pace * 0.3) + (self.shooting * 0.4) + (self.passing * 0.05) + (self.dribbling * 0.15) + (self.defending * 0.0) +(self.physical * 0.1))
        elif self.position in MIDFIELD_POSITIONS:
            return round((self.pace * 0.1) + (self.shooting * 0.1) + (self.passing * 0.3) + (self.dribbling * 0.3)  +  (self.defending * 0.1) + (self.physical * 0.1))
        elif self.position in DEFENCE_POSITIONS:
            return round((self.pace * 0.15) + (self.shooting * 0.0) + (self.passing * 0.1) + (self.dribbling * 0.05)  + (self.defending * 0.4) + (self.physical * 0.3) )
        else:
            raise ValueError("Position doesnt exist")
    @property
    def ball_possession_chance(self) -> int:
        return self.passing + self.dribbling
    @property
    def ball_take_over_chance(self) -> int:
        return self.physical + self.defending
class Goalkeeper(Player):

    REFLEX_MODIFIER: Final[float] = 0.6
    POSITION_MODIFIER: Final[float] = 0.4

    def __init__(self, name: str, diving: int, handling: int, kicking: int, reflexes: int, speed: int, positioning: int):
        super().__init__(name, Position.GOALKEEPER)
        self.diving : int = diving
        self.handling : int = handling
        self.kicking : int = kicking
        self.reflexes : int = reflexes
        self.speed : int = speed
        self.positioning : int = positioning

    @property
    def overall(self) -> int:
        return round((self.diving * 0.2) + (self.handling * 0.1) + (self.kicking *0.05) + (self.reflexes *0.35) + (self.speed *0.05) + (self.positioning * 0.25))
    
    @property
    def goalkeeping_score(self) -> int:
        return round(((self.reflexes * Goalkeeper.REFLEX_MODIFIER) + (self.positioning * Goalkeeper.POSITION_MODIFIER)))


