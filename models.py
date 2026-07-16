import random
from enum import Enum, auto

class Position(Enum):
    ATTACKER = auto()
    MIDFIELDER = auto()
    DEFENDER = auto()
    GOALKEEPER = auto()

class Player:
    def __init__(self, name : str, position : Position):
        self.name :str = name
        self.position : Position= position
    
    @property
    def overall(self):
        raise NotImplementedError("Method must be implemented in subclass")
class Team:
    def __init__(self, name : str, players : list[Player]):
        self.name : str = name 
        self.players : list[Player] = players
        self.field_players : list[Player] = [field_player for field_player in self.players if isinstance(field_player, FieldPlayer)]
        self.goalkeeper : Player = next((player for player in self.players if isinstance(player, Goalkeeper)),None)

    def get_goalkeeper(self) -> Player:
       return self.goalkeeper

    def get_defender(self) -> Player:
        weights : list[int]= []
        for player in self.field_players:
            if player.position == Position.DEFENDER:
                weights.append(10)
            elif player.position == Position.MIDFIELDER:
                weights.append(4)
            else:
                weights.append(1)

        return random.choices(self.field_players, weights,k=1)[0]
    
    def get_midfielder(self) -> Player:
        weights : list[int] = []
        for player in self.field_players:
            if player.position == Position.DEFENDER:
                weights.append(4)
            elif player.position == Position.MIDFIELDER:
                weights.append(10)
            else:
                weights.append(1)
        return random.choices(self.field_players, weights,k=1)[0]
    
    def get_attacker(self) -> Player:
        weights : list[int] = []
        for player in self.field_players:
            if player.position == Position.DEFENDER:
                weights.append(1)
            elif player.position == Position.MIDFIELDER:
                weights.append(4)
            else:
                weights.append(10)

        return random.choices(self.field_players, weights,k=1)[0]

class FieldPlayer(Player):
    def __init__(self, name : str, position : Position, pace : int, shooting : int, passing : int, dribbling : int, defending : int, physical : int):
        super().__init__(name, position)
        self.pace : int = pace
        self.shooting : int = shooting
        self.passing : int = passing
        self.dribbling : int = dribbling
        self.defending : int = defending
        self.physical : int = physical

    @property
    def overall(self) -> int:
        if self.position == Position.ATTACKER:
            return round((self.pace * 0.3) + (self.shooting * 0.4) + (self.passing * 0.05) + (self.dribbling * 0.15) + (self.defending * 0.0) +(self.physical * 0.1))
        elif self.position == Position.MIDFIELDER:
            return round((self.pace * 0.1) + (self.shooting * 0.1) + (self.passing * 0.3) + (self.dribbling * 0.3)  +  (self.defending * 0.1) + (self.physical * 0.1))
        elif self.position == Position.DEFENDER:
            return round((self.pace * 0.15) + (self.shooting * 0.0) + + (self.passing * 0.1) + (self.dribbling * 0.05)  + (self.defending * 0.4) +(self.physical * 0.3) )
        
class Goalkeeper(Player):
    def __init__(self, name : str, diving : int, handling : int, kicking : int, reflexes : int, speed : int, positioning : int):
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
    



