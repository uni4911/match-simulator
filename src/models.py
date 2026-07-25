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

PREFERRED_FALLBACKS: dict[Position, list[Position]] = {

    Position.GOALKEEPER: [],
    
    Position.CENTRE_BACK: [
        Position.LEFT_BACK, Position.RIGHT_BACK, 
        Position.CENTRAL_DEFENSIVE_MIDFIELDER
    ],
    Position.LEFT_BACK: [
        Position.LEFT_WING_BACK, Position.CENTRE_BACK, 
        Position.LEFT_MIDFIELDER
    ],
    Position.RIGHT_BACK: [
        Position.RIGHT_WING_BACK, Position.CENTRE_BACK, 
        Position.RIGHT_MIDFIELDER
    ],
    Position.LEFT_WING_BACK: [
        Position.LEFT_BACK, Position.LEFT_MIDFIELDER, 
        Position.LEFT_WING
    ],
    Position.RIGHT_WING_BACK: [
        Position.RIGHT_BACK, Position.RIGHT_MIDFIELDER, 
        Position.RIGHT_WING
    ],

    Position.CENTRAL_DEFENSIVE_MIDFIELDER: [
        Position.CENTRAL_MIDFIELDER, Position.CENTRE_BACK, 
        Position.CENTRAL_ATTACKING_MIDFIELDER
    ],
    Position.CENTRAL_MIDFIELDER: [
        Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER, 
        Position.LEFT_MIDFIELDER, Position.RIGHT_MIDFIELDER
    ],
    Position.CENTRAL_ATTACKING_MIDFIELDER: [
        Position.CENTRAL_MIDFIELDER, Position.CENTRAL_FORWARD, 
        Position.STRIKER
    ],
    Position.LEFT_MIDFIELDER: [
        Position.LEFT_WING, Position.LEFT_WING_BACK, 
        Position.CENTRAL_MIDFIELDER
    ],
    Position.RIGHT_MIDFIELDER: [
        Position.RIGHT_WING, Position.RIGHT_WING_BACK, 
        Position.CENTRAL_MIDFIELDER
    ],

    Position.LEFT_WING: [
        Position.RIGHT_WING, Position.LEFT_MIDFIELDER, 
        Position.STRIKER, Position.CENTRAL_FORWARD
    ],
    Position.RIGHT_WING: [
        Position.LEFT_WING, Position.RIGHT_MIDFIELDER, 
        Position.STRIKER, Position.CENTRAL_FORWARD
    ],
    Position.CENTRAL_FORWARD: [
        Position.STRIKER, Position.CENTRAL_ATTACKING_MIDFIELDER, 
        Position.LEFT_WING, Position.RIGHT_WING
    ],
    Position.STRIKER: [
        Position.CENTRAL_FORWARD, Position.CENTRAL_ATTACKING_MIDFIELDER, 
        Position.LEFT_WING, Position.RIGHT_WING
    ]
}

FORMATION_433 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]


class Player:
    def __init__(self, name: str, position: Position):
        self.name :str = name
        self.position : Position= position
    
class Team:
    def __init__(self, name: str, players: list[Player]):
        self.name : str = name 
        self.players : list[MatchPlayer] = players
        if len([player for player in self.players if isinstance(player, Goalkeeper)]) != 1:
            raise ValueError("Choose only one goalkeeper")
        self.starting_players : list['Player'] = [field_player for field_player in self.players if isinstance(field_player, FieldPlayer)]
        self.goalkeepers : list['Player'] = [player for player in self.players if isinstance(player, Goalkeeper)]
        

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

class MatchPlayer:
    def __init__(self, player: 'Player'):
        self.player: 'Player' = player
        self.goals: int = 0
        self.assists: int = 0
        self.yellow_card: int = 0
        self.has_red_card: bool = False
        self.passes: int =0

    def receive_card(self, card_type: str) -> bool:
        if card_type == 'yellow_card':
            self.yellow_card += 1
        if self.yellow_card == 2 or card_type == 'red_card':
            self.has_red_card = True
            return True
        if self.yellow_card == 1:
            return False
        return False


    def ball_possession_chance(self, modifier: float) -> float:
                return (self.player.passing + self.player.dribbling) * modifier
   
    def ball_take_over_chance(self, modifier: float) -> float:
                return (self.player.physical + self.player.defending) * modifier
        

class MatchTeam:
    def __init__(self, team: Team, formation: list[Position]):
        self.team: Team = team
        self.formation: list[Position] = formation
        self.match_players: list[MatchPlayer] = [MatchPlayer(player) for player in self.team.players]

    @property
    def starting_goalkeeper(self) -> Goalkeeper:
        return max(self.team.goalkeepers, key=lambda goalkeeper: goalkeeper.overall) 
    
    @property
    def starting_players(self) -> list[MatchPlayer]:

        starting_players: list[MatchPlayer] = []

        for position in self.formation:
            selected_player: 'Player' | None = None
            players_on_position: list[Player] = [player for player in self.match_players if player.player.position == position and player not in starting_players]
            if players_on_position:
                selected_player = sorted(players_on_position, key=lambda player: player.player.overall, reverse=True)[0]
            else:
                for fallback_position in PREFERRED_FALLBACKS[position]:
                    players_on_position: list[Player] = [player for player in self.match_players if player.player.position == fallback_position and player not in starting_players]
                    if players_on_position:
                        selected_player = sorted(players_on_position, key=lambda player: player.player.overall, reverse=True)[0]
                        break
            if selected_player is None:
                selected_player = sorted([p for p in self.match_players if isinstance(p.player, FieldPlayer) and p not in starting_players],key=lambda player: player.player.overall,reverse=True)[0]
        
            starting_players.append(selected_player)

        return starting_players

    @property 
    def bench_goalkeepers(self) -> list[Goalkeeper]:
        return [goalkeeper for goalkeeper in self.team.goalkeepers if goalkeeper != self.starting_goalkeeper]
    
    @property
    def bench_players(self) -> list[MatchPlayer]:
        return [player for player in self.team.players if player not in self.starting_players]

    @property
    def active_players(self) -> list[MatchPlayer]:
        return [player for player in self.starting_players if player.has_red_card is False]

    @property 
    def relative_strength_modifier(self) -> float:
        return len(self.active_players)/10

    def get_goalkeeper(self) -> MatchPlayer:
           return self.starting_goalkeeper
    
    def _get_weighted_player(self, weights_dict: dict[Position, int], default_weight: int) -> 'Player':
        weights: list[int] = [weights_dict.get(player.player.position, default_weight) for player in self.active_players]          
        return random.choices(self.active_players, weights,k=1)[0]
    
    def get_defender(self) -> 'Player':
        return  self._get_weighted_player(DEFENDER_WEIGHTS, DEFAULT_DEFENDER_WEIGHT)
    
    def get_midfielder(self) -> 'Player':
        return self._get_weighted_player(MIDFIELDER_WEIGHTS, DEFAULT_MIDFIELDER_WEIGHT)
    
    def get_attacker(self) -> 'Player':
            return self._get_weighted_player(ATTACKER_WEIGHTS, DEFAULT_ATTACKER_WEIGHT)

    def has_player(self, player: Player) -> bool:
        return player in self.match_players

    def get_penalty_taker(self) -> 'Player':
        return max(self.active_players, key=lambda player: player.player.shooting)

    def get_freekick_taker(self) -> 'Player':
        return max(self.active_players, key=lambda player: player.player.passing)

    

  