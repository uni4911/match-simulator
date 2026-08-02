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
    Position.CENTRAL_ATTACKING_MIDFIELDER: 8,
    Position.CENTRAL_MIDFIELDER: 6,
    Position.LEFT_MIDFIELDER: 6,
    Position.RIGHT_MIDFIELDER: 6,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER: 4,
    Position.LEFT_WING_BACK: 3,
    Position.RIGHT_WING_BACK: 3,
    Position.LEFT_BACK: 2,
    Position.RIGHT_BACK: 2,
    Position.CENTRE_BACK: 2
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

FORMATION_442 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_4231 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.STRIKER
]

FORMATION_352 = [
    Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK,
    Position.LEFT_WING_BACK, Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_WING_BACK,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_41212 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_532 = [
    Position.LEFT_WING_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_WING_BACK,
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.STRIKER, Position.STRIKER
]

FORMATION_343 = [
    Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]

AVAILABLE_FORMATIONS: dict[str, list[Position]] = {
    "4-3-3": FORMATION_433,
    "4-4-2": FORMATION_442,
    "4-2-3-1": FORMATION_4231,
    "3-5-2": FORMATION_352,
    "4-1-2-1-2": FORMATION_41212,
    "5-3-2": FORMATION_532,
    "3-4-3": FORMATION_343,
}

BASE_DRAIN_RATE = 0.0001
class Player:
    def __init__(self, name: str, position: Position):
        self.name :str = name
        self.position : Position= position
        self.fitness: float = 1.0
    
class Team:
    def __init__(self, name: str, players: list[Player]):
        self.name : str = name 
        self.players : list[MatchPlayer] = players
        self.starting_players : list['Player'] = [field_player for field_player in self.players if isinstance(field_player, FieldPlayer)]
        self.goalkeepers : list['Player'] = [player for player in self.players if isinstance(player, Goalkeeper)]
        

class FieldPlayer(Player):
    def __init__(self, name: str, position: Position, pace: int, shooting: int, passing: int, dribbling: int, defending: int, physical: int, heading: int, height: int):
        super().__init__(name, position)
        self.base_pace : int = pace
        self.base_shooting : int = shooting
        self.base_passing : int = passing
        self.base_dribbling : int = dribbling
        self.base_defending : int = defending
        self.base_physical : int = physical
        self.heading: int = heading
        self.height: int = height


    @property
    def overall(self) -> int:
        if self.position in ATTACKING_POSITIONS:
            return round((self.base_pace * 0.3) + (self.base_shooting * 0.4) + (self.base_passing * 0.05) + (self.base_dribbling * 0.15) + (self.base_defending * 0.0) +(self.base_physical * 0.1))
        elif self.position in MIDFIELD_POSITIONS:
            return round((self.base_pace * 0.1) + (self.base_shooting * 0.1) + (self.base_passing * 0.3) + (self.base_dribbling * 0.3)  +  (self.base_defending * 0.1) + (self.base_physical * 0.1))
        elif self.position in DEFENCE_POSITIONS:
            return round((self.base_pace * 0.15) + (self.base_shooting * 0.0) + (self.base_passing * 0.1) + (self.base_dribbling * 0.05)  + (self.base_defending * 0.4) + (self.base_physical * 0.3) )
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
        self.passes: int = 0
        self.current_stamina: float = self.player.fitness
        self.assigned_position: Position = player.position
        self.is_injured: bool = False
        self.injury_severity: str = "none"  
        self.is_forced_off: bool = False

    @property
    def is_injuried(self) -> bool:
        return self.is_injured

    @is_injuried.setter
    def is_injuried(self, value: bool) -> None:
        self.is_injured = value


    def receive_card(self, card_type: str) -> bool:
        if card_type == 'yellow_card':
            self.yellow_card += 1
        if self.yellow_card == 2 or card_type == 'red_card':
            self.has_red_card = True
            return True
        if self.yellow_card == 1:
            return False
        return False

    @property
    def position_penalty(self) -> float:
        if (self.assigned_position == self.player.position) or (self.assigned_position == Position.GOALKEEPER):
            return 1.0
        elif self.assigned_position in PREFERRED_FALLBACKS.get(self.player.position, []):
            return 0.9
        else:
            return 0.7    
        
    @property
    def stat_modifier(self) -> float:
        base_mod = (0.5 + 0.5 * self.current_stamina) * self.position_penalty
        if self.is_injured and self.injury_severity == "minor":
            base_mod *= 0.80 
        return base_mod
    @property 
    def name(self) -> str:
            return self.player.name
    @property
    def position(self) -> str:
        return self.assigned_position.name
    @property
    def yellow_cards(self) -> int:
        return self.yellow_card
    @property
    def pace(self) -> int:
        return int(self.player.base_pace * self.stat_modifier)
    @property
    def shooting(self) -> int:
        return int(self.player.base_shooting * self.stat_modifier)
    @property
    def passing(self) -> int:
        return int(self.player.base_passing * self.stat_modifier)
    @property
    def dribbling(self) -> int:
        return int(self.player.base_dribbling * self.stat_modifier)
    @property
    def defending(self) -> int:
        return int(self.player.base_defending * self.stat_modifier)
    @property
    def physical(self) -> int:
        return int(self.player.base_physical * self.stat_modifier)
    @property
    def heading(self) -> int:
        return int(self.player.heading)
    @property
    def height(self) -> int:
        return self.player.height
    @property
    def heading_score(self) -> int:
        return int((self.player.heading * 0.5) + (self.physical * 0.3) + (self.player.height * 0.2))

         
    def ball_possession_chance(self, modifier: float) -> float:
        return (self.passing + self.dribbling) * modifier
       
    def ball_take_over_chance(self, modifier: float) -> float:
        return (self.physical + self.defending) * modifier
   

    def drain_stamina(self, seconds: int, is_active: bool = False) -> None:
        multiplier = 2.5 if is_active else 1.0
        physical_factor: float = 1.0 -(self.player.base_physical/200)
        drain_amount:float = seconds * BASE_DRAIN_RATE * physical_factor * multiplier
        self.current_stamina = max(0.0,self.current_stamina - drain_amount)
         
class MatchTeam:
    def __init__(self, team: Team, formation: list[Position]):
        self.team: Team = team
        self.formation: list[Position] = formation
        self.match_players: list[MatchPlayer] = [MatchPlayer(player) for player in self.team.players]
        self.players_on_field: list[MatchPlayer] = self._starting_players()
        self.bench_players: list[MatchPlayer] = self._bench_players()
        self.substitution_limit: int = 5

    @property
    def starting_goalkeeper(self) -> Goalkeeper:
        return max(self.team.goalkeepers, key=lambda goalkeeper: goalkeeper.overall) 

    @property 
    def bench_goalkeepers(self) -> list[Goalkeeper]:
        return [goalkeeper for goalkeeper in self.team.goalkeepers if goalkeeper != self.starting_goalkeeper]

    @property
    def active_players(self) -> list[MatchPlayer]:
        return [player for player in self.players_on_field if not player.has_red_card and not player.is_forced_off]

    @property 
    def relative_strength_modifier(self) -> float:
        return len(self.active_players)/10

    @property
    def midfield_power(self) -> int:
        midfielders = [player for player in self.active_players if player.player.position in MIDFIELD_POSITIONS ]
        if not midfielders:
            return 1
        total_sum = sum(player.passing + player.dribbling + player.player.overall for player in midfielders)
        return total_sum // len(midfielders)

    def _bench_players(self) -> list[MatchPlayer]:
            return [player for player in self.match_players if player not in self.players_on_field]

    def _starting_players(self) -> list[MatchPlayer]:
    
            starting_players: list[MatchPlayer] = []
            for position in self.formation:
                selected_player: MatchPlayer | None = None
                players_on_position: list[MatchPlayer] = [player for player in self.match_players if player.player.position == position and player not in starting_players]
                if players_on_position:
                    selected_player = sorted(players_on_position, key=lambda player: player.player.overall, reverse=True)[0]
                else:
                    for fallback_position in PREFERRED_FALLBACKS[position]:
                        players_on_position: list[MatchPlayer] = [player for player in self.match_players if player.player.position == fallback_position and player not in starting_players]
                        if players_on_position:
                            selected_player = sorted(players_on_position, key=lambda player: player.player.overall, reverse=True)[0]
                            break
                if selected_player is None:
                    selected_player = sorted([p for p in self.match_players if isinstance(p.player, FieldPlayer) and p not in starting_players],key=lambda player: player.player.overall,reverse=True)[0]
                selected_player.assigned_position = position
                starting_players.append(selected_player)    
    
            return starting_players
        
    
    def _get_weighted_player(self, weights_dict: dict[Position, int], default_weight: int, excluded_player: Optional[MatchPlayer] = None) -> 'Player':
        if excluded_player is None:
            weights: list[int] = [weights_dict.get(player.player.position, default_weight) for player in self.active_players]          
            return random.choices(self.active_players, weights,k=1)[0]
        else:
            filtered_players: list[MatchPlayer] = [player for player in self.active_players if player != excluded_player]
            weights: list[int] = [weights_dict.get(player.player.position, default_weight) for player in filtered_players]          
            return random.choices(filtered_players, weights,k=1)[0]
             
    def get_goalkeeper(self) -> MatchPlayer:
               return self.starting_goalkeeper
    
    def get_defender(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        return  self._get_weighted_player(DEFENDER_WEIGHTS, DEFAULT_DEFENDER_WEIGHT, excluded_player)
    
    def get_midfielder(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        return self._get_weighted_player(MIDFIELDER_WEIGHTS, DEFAULT_MIDFIELDER_WEIGHT, excluded_player)
    
    def get_attacker(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
            return self._get_weighted_player(ATTACKER_WEIGHTS, DEFAULT_ATTACKER_WEIGHT, excluded_player)

    def has_player(self, player: Player) -> bool:
        return player in self.match_players

    def get_penalty_taker(self) ->  MatchPlayer:
        return max(self.active_players, key=lambda player: player.shooting)

    def get_freekick_taker(self) -> MatchPlayer:
        return max(self.active_players, key=lambda player: player.passing)

    def get_corner_taker(self) -> MatchPlayer:
        return max(self.active_players, key=lambda player: player.passing)
    
    def get_heading_player(self, excluded_player: MatchPlayer|None = None) -> MatchPlayer:
        candidates = [player for player in self.active_players if player != excluded_player]
        weights = [player.heading + ((player.height - 160) * 0.5) for player in candidates]
        return random.choices(candidates, weights,k=1)[0]
        
        
      
    def update_stamina(self, seconds: int, active_players: Optional[list[MatchPlayer]] = None) -> None:
        if active_players is None:
             active_players = []
        for player in self.active_players:
            is_active = player in active_players
            player.drain_stamina(seconds, is_active=is_active)

    def recover_stamina(self, amount: float = 0.20) -> None:
        for player in self.match_players:
            player.current_stamina = min(1.0, player.current_stamina + amount)

    def make_substitution(self, player_off: MatchPlayer, player_in: MatchPlayer) -> bool:
        if player_in in self.bench_players and player_off in self.players_on_field and not player_off.has_red_card and self.substitution_limit > 0:
            player_in.assigned_position = player_off.assigned_position
            self.players_on_field.append(player_in)
            self.players_on_field.remove(player_off)
            self.bench_players.append(player_off)
            self.bench_players.remove(player_in)
            self.substitution_limit -= 1
            return True
        else:
            return False

    def check_and_make_auto_substitution(self) -> Optional[tuple[MatchPlayer, MatchPlayer]]:
        if self.substitution_limit <= 0 or not self.bench_players:
            return None
    
        injured_on_field = [p for p in self.active_players if p.is_injured]
        if injured_on_field:
            player_off = injured_on_field[0]
        else:
            player_off = min(self.active_players, key=lambda player: player.current_stamina)
            if player_off.current_stamina > 0.75:
                return None

        player_in = next((player for player in self.bench_players if player.player.position == player_off.assigned_position), None)
        if player_in is None:
            player_in = next((player for player in self.bench_players if not isinstance(player.player, Goalkeeper)), None)
        if player_in and self.make_substitution(player_off, player_in):
            return (player_off, player_in)
        return None

    def handle_injury(self, injured_player: MatchPlayer, severity: str = "severe") -> Optional[tuple[MatchPlayer, MatchPlayer]]:
        injured_player.is_injured = True
        injured_player.injury_severity = severity
        if severity == "severe":
            injured_player.is_forced_off = True

        if severity == "severe" and self.substitution_limit > 0 and self.bench_players:
            player_in = next((p for p in self.bench_players if p.player.position == injured_player.assigned_position), None)
            if player_in is None:
                player_in = next((p for p in self.bench_players if not isinstance(p.player, Goalkeeper)), None)
            if player_in and self.make_substitution(injured_player, player_in):
                return (injured_player, player_in)
        return None

    

  