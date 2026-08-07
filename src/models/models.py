from __future__ import annotations
import random
from enum import Enum, auto
from typing import Optional, Final, TYPE_CHECKING
if TYPE_CHECKING:
    from src.engine.engine import Match


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
    Position.STRIKER: 18,
    Position.CENTRAL_FORWARD: 18,
    Position.LEFT_WING: 8,
    Position.RIGHT_WING: 8,
    Position.CENTRAL_ATTACKING_MIDFIELDER: 5,
    Position.CENTRAL_MIDFIELDER: 2,
    Position.LEFT_MIDFIELDER: 3,
    Position.RIGHT_MIDFIELDER: 3,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER: 1,
    Position.LEFT_WING_BACK: 0,
    Position.RIGHT_WING_BACK: 0,
    Position.LEFT_BACK: 0,
    Position.RIGHT_BACK: 0,
    Position.CENTRE_BACK: 0
}
DEFAULT_ATTACKER_WEIGHT = 1


WINGER_WEIGHTS: Final[dict[Position, int]] = {
    Position.LEFT_WING: 10,
    Position.RIGHT_WING: 10,
    Position.LEFT_MIDFIELDER: 9,
    Position.RIGHT_MIDFIELDER: 9,
    Position.LEFT_WING_BACK: 6,
    Position.RIGHT_WING_BACK: 6,
    Position.STRIKER: 4,
    Position.CENTRAL_FORWARD: 4,
    Position.CENTRAL_ATTACKING_MIDFIELDER: 5,
}
DEFAULT_WINGER_WEIGHT = 1

CAM_WEIGHTS: Final[dict[Position, int]] = {
    Position.CENTRAL_ATTACKING_MIDFIELDER: 10,
    Position.CENTRAL_MIDFIELDER: 8,
    Position.LEFT_MIDFIELDER: 7,
    Position.RIGHT_MIDFIELDER: 7,
    Position.CENTRAL_FORWARD: 6,
    Position.STRIKER: 4,
}
DEFAULT_CAM_WEIGHT = 1


ATTACKING_POSITIONS = set([Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING, Position.CENTRAL_FORWARD])
MIDFIELD_POSITIONS = set([Position.LEFT_MIDFIELDER, Position.RIGHT_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER])
DEFENCE_POSITIONS = set([Position.LEFT_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK, Position.LEFT_WING_BACK, Position.RIGHT_WING_BACK])

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
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]

FORMATION_433_HOLDING = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]

FORMATION_433_ATTACK = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]

FORMATION_433_DEFEND = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]

FORMATION_433_FALSE9 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.LEFT_WING, Position.CENTRAL_FORWARD, Position.RIGHT_WING
]

FORMATION_433_NARROW = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.STRIKER
]

FORMATION_442 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_442_DIAMOND = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.LEFT_MIDFIELDER, Position.RIGHT_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_4231 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.STRIKER
]

FORMATION_4231_NARROW = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER,
    Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER
]

FORMATION_41212 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_41212_WIDE = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.LEFT_MIDFIELDER, Position.RIGHT_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_4312 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_4141 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_DEFENSIVE_MIDFIELDER,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.STRIKER
]

FORMATION_451 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.STRIKER
]

FORMATION_424 = [
    Position.LEFT_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK,
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.STRIKER, Position.RIGHT_WING
]

FORMATION_352 = [
    Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK,
    Position.LEFT_WING_BACK, Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_WING_BACK,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_343 = [
    Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]

FORMATION_3412 = [
    Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER, Position.CENTRAL_FORWARD
]

FORMATION_3421 = [
    Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER,
    Position.STRIKER
]

FORMATION_532 = [
    Position.LEFT_WING_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_WING_BACK,
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.STRIKER, Position.STRIKER
]

FORMATION_541 = [
    Position.LEFT_WING_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_WING_BACK,
    Position.LEFT_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.RIGHT_MIDFIELDER,
    Position.STRIKER
]

FORMATION_523 = [
    Position.LEFT_WING_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.CENTRE_BACK, Position.RIGHT_WING_BACK,
    Position.CENTRAL_MIDFIELDER, Position.CENTRAL_MIDFIELDER,
    Position.LEFT_WING, Position.STRIKER, Position.RIGHT_WING
]

AVAILABLE_FORMATIONS: dict[str, list[Position]] = {
    "4-3-3": FORMATION_433,
    "4-3-3 Holding": FORMATION_433_HOLDING,
    "4-3-3 Attack": FORMATION_433_ATTACK,
    "4-3-3 Defend": FORMATION_433_DEFEND,
    "4-3-3 False 9": FORMATION_433_FALSE9,
    "4-3-3 Narrow": FORMATION_433_NARROW,
    "4-4-2": FORMATION_442,
    "4-4-2 Diamond": FORMATION_442_DIAMOND,
    "4-2-3-1": FORMATION_4231,
    "4-2-3-1 Narrow": FORMATION_4231_NARROW,
    "4-1-2-1-2": FORMATION_41212,
    "4-1-2-1-2 Wide": FORMATION_41212_WIDE,
    "4-3-1-2": FORMATION_4312,
    "4-1-4-1": FORMATION_4141,
    "4-5-1": FORMATION_451,
    "4-2-4": FORMATION_424,
    "3-5-2": FORMATION_352,
    "3-4-3": FORMATION_343,
    "3-4-1-2": FORMATION_3412,
    "3-4-2-1": FORMATION_3421,
    "5-3-2": FORMATION_532,
    "5-4-1": FORMATION_541,
    "5-2-3": FORMATION_523,
}

def get_formation_positions(formation_name: str) -> list[Position]:
    if formation_name in AVAILABLE_FORMATIONS:
        return AVAILABLE_FORMATIONS[formation_name]
    cleaned = formation_name.lower().replace(" ", "").replace("-", "")
    for k, v in AVAILABLE_FORMATIONS.items():
        if k.lower().replace(" ", "").replace("-", "") == cleaned:
            return v
    if formation_name.startswith("4-3-3"):
        return FORMATION_433
    elif formation_name.startswith("4-4-2"):
        return FORMATION_442
    elif formation_name.startswith("4-2-3-1"):
        return FORMATION_4231
    elif formation_name.startswith("3-5-2"):
        return FORMATION_352
    elif formation_name.startswith("5-3-2"):
        return FORMATION_532
    elif formation_name.startswith("3-4-3"):
        return FORMATION_343
    return FORMATION_433

BASE_DRAIN_RATE = 0.0001
class Player:
    def __init__(self, full_name: Optional[str] = None, position: Position = Position.CENTRAL_MIDFIELDER, age: int = 20, nationality: str = "Unknown", height: int = 180, short_name: Optional[str] = None, name: Optional[str] = None):
        resolved_full_name = full_name if full_name is not None else (name if name is not None else "Unknown Player")
        self.full_name: str = resolved_full_name
        self.short_name: str = short_name if short_name is not None else resolved_full_name
        self.position: Position = position
        self.age: int = age
        self.nationality: str = nationality
        self.height: int = height
        self.fitness: float = 1.0
        self.form: float = 1.0

    @property
    def name(self) -> str:
        return self.short_name or self.full_name

    
class Team:
    def __init__(self, name: str, players: list[Player], league: str = "Inne", formation: str = "4-3-3"):
        self.name : str = name 
        self.league : str = league
        self.formation : str = formation
        self.players : list[MatchPlayer] = players
        self.starting_players : list['Player'] = [field_player for field_player in self.players if isinstance(field_player, FieldPlayer)]
        self.goalkeepers : list['Player'] = [player for player in self.players if isinstance(player, Goalkeeper)]
        

class FieldPlayer(Player):
    def __init__(self, full_name: Optional[str] = None, position: Position = Position.CENTRAL_MIDFIELDER, pace: int = 50, shooting: int = 50, passing: int = 50, dribbling: int = 50, defending: int = 50, physical: int = 50, heading: int = 50, height: int = 180, age: int = 20, nationality: str = "Unknown", short_name: Optional[str] = None, name: Optional[str] = None):
        resolved_full_name = full_name if full_name is not None else (name if name is not None else "Unknown Player")
        super().__init__(full_name=resolved_full_name, position=position, age=age, nationality=nationality, height=height, short_name=short_name)
        self.base_pace : int = pace
        self.base_shooting : int = shooting
        self.base_passing : int = passing
        self.base_dribbling : int = dribbling
        self.base_defending : int = defending
        self.base_physical : int = physical
        self.heading: int = heading


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

    def __init__(self, full_name: Optional[str] = None, diving: int = 50, handling: int = 50, kicking: int = 50, reflexes: int = 50, speed: int = 50, positioning: int = 50, age: int = 20, nationality: str = "Unknown", height: int = 188, short_name: Optional[str] = None, name: Optional[str] = None):
        resolved_full_name = full_name if full_name is not None else (name if name is not None else "Unknown Player")
        super().__init__(full_name=resolved_full_name, position=Position.GOALKEEPER, age=age, nationality=nationality, height=height, short_name=short_name)
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
        self.is_starter: bool = False
        self.is_on_field: bool = False



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
    def effective_overall(self) -> float:
        return self.player.overall * (0.80 + 0.20 * self.current_stamina)
    @property 
    def name(self) -> str:
            return self.player.short_name or self.player.full_name
    @property 
    def full_name(self) -> str:
            return self.player.full_name
    @property 
    def short_name(self) -> str:
            return self.player.short_name or self.player.full_name
    @property
    def position(self) -> str:
        return self.assigned_position.name
    @property
    def yellow_cards(self) -> int:
        return self.yellow_card
    @property
    def pace(self) -> int:
        b = getattr(self.player, "base_pace", getattr(self.player, "speed", 50))
        return int(b * self.stat_modifier)
    @property
    def shooting(self) -> int:
        b = getattr(self.player, "base_shooting", 50)
        return int(b * self.stat_modifier)
    @property
    def passing(self) -> int:
        b = getattr(self.player, "base_passing", getattr(self.player, "kicking", 50))
        return int(b * self.stat_modifier)
    @property
    def dribbling(self) -> int:
        b = getattr(self.player, "base_dribbling", 50)
        return int(b * self.stat_modifier)
    @property
    def defending(self) -> int:
        b = getattr(self.player, "base_defending", 50)
        return int(b * self.stat_modifier)
    @property
    def physical(self) -> int:
        b = getattr(self.player, "base_physical", 50)
        return int(b * self.stat_modifier)
    @property
    def heading(self) -> int:
        return int(getattr(self.player, "heading", 50))
    @property
    def height(self) -> int:
        return self.player.height
    @property
    def heading_score(self) -> int:
        return int((self.player.heading * 0.5) + (self.physical * 0.3) + (self.player.height * 0.2))

    @property
    def goalkeeping_score(self) -> int:
        if isinstance(self.player, Goalkeeper):
            return int(self.player.goalkeeping_score * self.stat_modifier)
        return int(50 * self.stat_modifier)

         
    def ball_possession_chance(self, modifier: float) -> float:
        return (self.passing + self.dribbling) * modifier
       
    def ball_take_over_chance(self, modifier: float) -> float:
        return (self.physical + self.defending) * modifier
   

    def drain_stamina(self, seconds: int, is_active: bool = False) -> None:
        multiplier = 2.5 if is_active else 1.0
        physical = getattr(self.player, "base_physical", getattr(self.player, "physical", 50))
        physical_factor: float = 1.0 - (physical / 200)
        drain_amount: float = seconds * BASE_DRAIN_RATE * physical_factor * multiplier
        self.current_stamina = max(0.0, self.current_stamina - drain_amount)
         
class TeamStatsMatch:
    def __init__(self) -> None:
        self.possession_time: float = 0.0
        self.shots_on_target: int = 0
        self.shots_off_target: int = 0
        self.fouls: int = 0
        self.passes: int = 0
        self.goals: int = 0
        self.yellow_cards: int = 0
        self.red_cards: int = 0
        self.corners: int = 0
        self.saves: int = 0

    @property
    def total_shots(self) -> int:
        return self.shots_on_target + self.shots_off_target

    def get_possession_percentage(self, opponent_stats: Optional[TeamStatsMatch] = None) -> float:
        if opponent_stats is None:
            return 50.0
        total_time = self.possession_time + opponent_stats.possession_time
        if total_time <= 0:
            return 50.0
        return round((self.possession_time / total_time) * 100, 1)

    def reset(self) -> None:
        self.possession_time = 0.0
        self.shots_on_target = 0
        self.shots_off_target = 0
        self.fouls = 0
        self.passes = 0
        self.goals = 0
        self.yellow_cards = 0
        self.red_cards = 0
        self.corners = 0
        self.saves = 0

    def to_dict(self, opponent_stats: Optional[TeamStatsMatch] = None) -> dict[str, float | int]:
        return {
            "possession_time": round(self.possession_time, 1),
            "possession_percentage": self.get_possession_percentage(opponent_stats),
            "shots_on_target": self.shots_on_target,
            "shots_off_target": self.shots_off_target,
            "total_shots": self.total_shots,
            "fouls": self.fouls,
            "passes": self.passes,
            "goals": self.goals,
            "yellow_cards": self.yellow_cards,
            "red_cards": self.red_cards,
            "corners": self.corners,
            "saves": self.saves,
        }

class MatchTeam:
    def __init__(self, team: Team, formation: list[Position]):
        self.team: Team = team
        self.formation: list[Position] = formation
        self.form_modifier: float = 1.0
        self.match_players: list[MatchPlayer] = [MatchPlayer(player) for player in self.team.players]
        self.players_on_field: list[MatchPlayer] = self._starting_players()
        self.bench_players: list[MatchPlayer] = self._bench_players()
        for p in self.bench_players:
            p.is_starter = False
            p.is_on_field = False

        self.match_players = self.players_on_field + self.bench_players
        self.substitution_limit: int = 5
        self.played_players: set[MatchPlayer] = set(self.players_on_field)
        self.stats: TeamStatsMatch = TeamStatsMatch()
        self.last_substitution_second: int = -999

    @property
    def starting_goalkeeper(self) -> Goalkeeper:
        gk_mp = next((p for p in self.players_on_field if isinstance(p.player, Goalkeeper) or p.assigned_position == Position.GOALKEEPER), None)
        if gk_mp and isinstance(gk_mp.player, Goalkeeper):
            return gk_mp.player
        return max(self.team.goalkeepers, key=lambda goalkeeper: goalkeeper.overall) if self.team.goalkeepers else Goalkeeper("Default GK")

    @property 
    def bench_goalkeepers(self) -> list[Goalkeeper]:
        return [goalkeeper for goalkeeper in self.team.goalkeepers if goalkeeper != self.starting_goalkeeper]

    @property
    def active_players(self) -> list[MatchPlayer]:
        return [player for player in self.players_on_field if not player.has_red_card and not player.is_forced_off]

    @property 
    def relative_strength_modifier(self) -> float:
        return len(self.active_players)/11

    @property
    def midfield_power(self) -> int:
        midfielders = [player for player in self.active_players if player.player.position in MIDFIELD_POSITIONS ]
        if not midfielders:
            return 1
        total_sum = sum(player.passing + player.dribbling + player.player.overall for player in midfielders)
        avg = total_sum / len(midfielders)
        scaled = int(((avg / 70.0) ** 2.0) * 70.0)
        return max(1, scaled)


    def _bench_players(self) -> list[MatchPlayer]:
            return [player for player in self.match_players if player not in self.players_on_field]

    def _starting_players(self) -> list[MatchPlayer]:
        starting_players: list[MatchPlayer] = []

        def is_gk(p: MatchPlayer) -> bool:
            return isinstance(p.player, Goalkeeper) or p.player.position == Position.GOALKEEPER

        def is_field_player(p: MatchPlayer) -> bool:
            return not is_gk(p)

        def position_suitability(player_pos: Position, target_pos: Position) -> float:
            if player_pos == target_pos:
                return 1.0
            elif target_pos in PREFERRED_FALLBACKS.get(player_pos, []) or player_pos in PREFERRED_FALLBACKS.get(target_pos, []):
                return 0.90
            elif (player_pos in ATTACKING_POSITIONS and target_pos in ATTACKING_POSITIONS) or \
                 (player_pos in MIDFIELD_POSITIONS and target_pos in MIDFIELD_POSITIONS) or \
                 (player_pos in DEFENCE_POSITIONS and target_pos in DEFENCE_POSITIONS):
                return 0.82
            else:
                return 0.65

        gks = [p for p in self.match_players if is_gk(p)]
        if gks:
            best_gk = max(gks, key=lambda p: (p.effective_overall, p.player.overall))
            best_gk.assigned_position = Position.GOALKEEPER
            best_gk.is_starter = True
            best_gk.is_on_field = True
            starting_players.append(best_gk)

        field_candidates = [p for p in self.match_players if is_field_player(p)]

        for position in self.formation:
            available = [p for p in field_candidates if p not in starting_players]
            if not available:
                break
            selected_player = max(available, key=lambda p: (
                p.effective_overall * position_suitability(p.player.position, position),
                p.player.overall
            ))
            selected_player.assigned_position = position
            selected_player.is_starter = True
            selected_player.is_on_field = True
            starting_players.append(selected_player)

        return starting_players
        
    
    def _get_weighted_player(self, weights_dict: dict[Position, int], default_weight: int, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        base_candidates = self.active_players if excluded_player is None else [p for p in self.active_players if p != excluded_player]
        field_candidates = [p for p in base_candidates if not isinstance(p.player, Goalkeeper) and p.assigned_position != Position.GOALKEEPER]
        candidates = field_candidates if field_candidates else base_candidates
        if not candidates:
            return self.active_players[0] if self.active_players else self.players_on_field[0]
        weights: list[int] = [weights_dict.get(player.assigned_position, weights_dict.get(player.player.position, default_weight)) for player in candidates]
        if sum(weights) <= 0:
            weights = [1] * len(candidates)
        return random.choices(candidates, weights, k=1)[0]
             
    def get_goalkeeper(self) -> MatchPlayer:
        return self.starting_goalkeeper
    
    def get_defender(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        return self._get_weighted_player(DEFENDER_WEIGHTS, DEFAULT_DEFENDER_WEIGHT, excluded_player)
    
    def get_midfielder(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        return self._get_weighted_player(MIDFIELDER_WEIGHTS, DEFAULT_MIDFIELDER_WEIGHT, excluded_player)
    
    def get_attacker(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        return self._get_weighted_player(ATTACKER_WEIGHTS, DEFAULT_ATTACKER_WEIGHT, excluded_player)

    def get_winger(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        return self._get_weighted_player(WINGER_WEIGHTS, DEFAULT_WINGER_WEIGHT, excluded_player)

    def get_cam(self, excluded_player: Optional[MatchPlayer] = None) -> MatchPlayer:
        return self._get_weighted_player(CAM_WEIGHTS, DEFAULT_CAM_WEIGHT, excluded_player)

    def has_player(self, player: Player | MatchPlayer) -> bool:
        return any(mp == player or mp.player == player for mp in self.match_players)

    def get_penalty_taker(self) -> MatchPlayer:
        candidates = [p for p in self.active_players if isinstance(p.player, FieldPlayer)] or self.active_players
        top_shooters = sorted(candidates, key=lambda player: player.shooting, reverse=True)[:3]
        weights = [p.shooting for p in top_shooters]
        return random.choices(top_shooters, weights=weights, k=1)[0]

    def get_freekick_taker(self) -> MatchPlayer:
        candidates = [p for p in self.active_players if isinstance(p.player, FieldPlayer)] or self.active_players
        return max(candidates, key=lambda player: player.passing)

    def get_corner_taker(self) -> MatchPlayer:
        candidates = [p for p in self.active_players if isinstance(p.player, FieldPlayer)] or self.active_players
        return max(candidates, key=lambda player: player.passing)
    
    def get_heading_player(self, excluded_player: MatchPlayer|None = None) -> MatchPlayer:
        candidates = [player for player in self.active_players if player != excluded_player and isinstance(player.player, FieldPlayer)]
        if not candidates:
            candidates = [player for player in self.active_players if player != excluded_player]
        if not candidates:
            return self.active_players[0] if self.active_players else self.players_on_field[0]
        weights = [max(1.0, player.heading + ((player.height - 160) * 0.5)) for player in candidates]
        return random.choices(candidates, weights, k=1)[0]
        
        
      
    def update_stamina(self, seconds: int, active_players: Optional[list[MatchPlayer]] = None) -> None:
        if active_players is None:
             active_players = []
        for player in self.active_players:
            is_active = player in active_players
            player.drain_stamina(seconds, is_active=is_active)

    def recover_stamina(self, amount: float = 0.20) -> None:
        for player in self.match_players:
            player.current_stamina = min(1.0, player.current_stamina + amount)

    def make_substitution(self, player_off: MatchPlayer, player_in: MatchPlayer, current_second: int = 0) -> bool:
        if player_in in self.bench_players and player_off in self.players_on_field and not player_off.has_red_card and self.substitution_limit > 0:
            player_in.assigned_position = player_off.assigned_position
            player_in.is_on_field = True
            player_off.is_on_field = False
            self.players_on_field.append(player_in)
            self.players_on_field.remove(player_off)
            self.bench_players.append(player_off)
            self.bench_players.remove(player_in)
            self.played_players.add(player_in)
            self.substitution_limit -= 1
            if current_second > 0:
                self.last_substitution_second = current_second
            return True
        else:
            return False

    def check_and_make_auto_substitution(self, current_second: int = 0) -> Optional[tuple[MatchPlayer, MatchPlayer]]:
        if self.substitution_limit <= 0 or not self.bench_players or not self.active_players:
            return None
    
        injured_on_field = [p for p in self.active_players if p.is_injured]
        if injured_on_field:
            player_off = injured_on_field[0]
        else:
          
            if current_second < 2850:
                return None

            if hasattr(self, 'last_substitution_second') and (current_second - self.last_substitution_second < 300):
                return None

           
            field_players_on_field = [
                p for p in self.active_players 
                if not isinstance(p.player, Goalkeeper) and p.assigned_position != Position.GOALKEEPER
            ]
            if not field_players_on_field:
                return None

            player_off = min(field_players_on_field, key=lambda player: player.current_stamina)
            
            # Progressive 2nd half substitution thresholds to spread subs across 2nd half
            if current_second >= 4300: # ~71+ mins
                stamina_threshold = 0.88
            elif current_second >= 3400: # ~56+ mins
                stamina_threshold = 0.83
            else: # ~47-55 mins
                stamina_threshold = 0.77

            if player_off.current_stamina > stamina_threshold:
                return None

        if isinstance(player_off.player, Goalkeeper) or player_off.assigned_position == Position.GOALKEEPER:
            player_in = next((player for player in self.bench_players if isinstance(player.player, Goalkeeper) or player.player.position == Position.GOALKEEPER), None)
        else:
            player_in = next((player for player in self.bench_players if player.player.position == player_off.assigned_position and not isinstance(player.player, Goalkeeper)), None)
            if player_in is None:
                player_in = next((player for player in self.bench_players if not isinstance(player.player, Goalkeeper) and player.player.position != Position.GOALKEEPER), None)

        if player_in and self.make_substitution(player_off, player_in, current_second):
            return (player_off, player_in)
        return None

    def handle_injury(self, injured_player: MatchPlayer, severity: str = "severe", current_second: int = 0) -> Optional[tuple[MatchPlayer, MatchPlayer]]:
        injured_player.is_injured = True
        injured_player.injury_severity = severity
        if severity == "severe":
            injured_player.is_forced_off = True

        if severity == "severe" and self.substitution_limit > 0 and self.bench_players:
            if isinstance(injured_player.player, Goalkeeper) or injured_player.assigned_position == Position.GOALKEEPER:
                player_in = next((p for p in self.bench_players if isinstance(p.player, Goalkeeper) or p.player.position == Position.GOALKEEPER), None)
                if player_in is None:
                    player_in = self.bench_players[0]
            else:
                player_in = next((p for p in self.bench_players if p.player.position == injured_player.assigned_position and not isinstance(p.player, Goalkeeper) and p.player.position != Position.GOALKEEPER), None)
                if player_in is None:
                    player_in = next((p for p in self.bench_players if not isinstance(p.player, Goalkeeper) and p.player.position != Position.GOALKEEPER), None)
            if player_in and self.make_substitution(injured_player, player_in, current_second):
                return (injured_player, player_in)
        return None

class League:
    def __init__(self, name: str, teams: Optional[list[Team]] = None):
        self.name: str = name 
        self.teams: list[Team] = teams if teams is not None else []
        self.fixtures: list[Match] = []
        self.table: dict[Team, LeagueTeamStats] = {team: LeagueTeamStats(team) for team in self.teams}
        self.player_stats: dict[Player, PlayerSeasonStats] = {}

    def register_match_player_stats(self, match: Match) -> None:
        home_team = match.home_team
        away_team = match.away_team

        for match_team, conceded in [(home_team, match.away_score), (away_team, match.home_score)]:
            clean_sheet = (conceded == 0)
            played = getattr(match_team, "played_players", match_team.players_on_field)
            for mp in played:
                if mp.player not in self.player_stats:
                    self.player_stats[mp.player] = PlayerSeasonStats(mp.player)
                self.player_stats[mp.player].register_match_player(mp, team_conceded_zero=clean_sheet)


class PlayerSeasonStats:
    def __init__(self, player: Player):
        self.player: Player = player
        self.matches_played: int = 0
        self.goals: int = 0
        self.assists: int = 0
        self.yellow_cards: int = 0
        self.red_cards: int = 0
        self.passes: int = 0
        self.clean_sheets: int = 0

    @property
    def player_name(self) -> str:
        return self.player.short_name or self.player.full_name

    @property
    def full_name(self) -> str:
        return self.player.full_name

    @property
    def short_name(self) -> str:
        return self.player.short_name or self.player.full_name

    @property
    def position(self) -> str:
        return self.player.position.name

    def register_match_player(self, match_player: MatchPlayer, team_conceded_zero: bool = False) -> None:
        self.matches_played += 1
        self.goals += match_player.goals
        self.assists += match_player.assists
        self.yellow_cards += match_player.yellow_card
        if match_player.has_red_card:
            self.red_cards += 1
        self.passes += match_player.passes
        if isinstance(self.player, Goalkeeper) and team_conceded_zero:
            self.clean_sheets += 1


class LeagueTeamStats:
    def __init__(self, team: Team):
        self.team: Team = team
        self.goals_scored: int = 0
        self.goals_conceded: int = 0
        self.matches_played: int = 0
        self.wins: int = 0
        self.draws: int = 0
        self.loses: int = 0
        self.recent_results: list[str] = []

    @property
    def points(self) -> int:
        return self.wins * 3 + self.draws * 1

    @property
    def form_modifier(self) -> float:
        if not self.recent_results:
            return 1.0
        last_5 = self.recent_results[-5:]
        pts_map = {'W': 3, 'D': 1, 'L': 0}
        total_pts = sum(pts_map.get(res, 0) for res in last_5)
        max_possible = len(last_5) * 3
        if max_possible == 0:
            return 1.0
        ratio = total_pts / max_possible
        return round(0.975 + (ratio * 0.05), 3)

    @property
    def goals_difference(self) -> int:
        return self.goals_scored - self.goals_conceded
    
    @property
    def team_name(self) -> str:
        return self.team.name

    def register_match_result(self, goals_scored: int, goals_conceded: int) -> None:
        diff = goals_scored - goals_conceded
        self.goals_scored += goals_scored
        self.goals_conceded += goals_conceded
        self.matches_played += 1

        if diff > 0:
            self.wins += 1
            self.recent_results.append('W')
        elif diff < 0:
            self.loses += 1
            self.recent_results.append('L')
        else:
            self.draws += 1
            self.recent_results.append('D')

        if len(self.recent_results) > 5:
            self.recent_results.pop(0)

