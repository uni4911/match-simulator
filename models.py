import random
from enum import Enum, auto

class Team:
    def __init__(self, name, players):
        self.name = name
        self.players = players

    def get_defender(self):
        weights = []
        for player in self.players:
            if player.position == Position.DEFENDER:
                weights.append(10)
            elif player.position == Position.MIDFIELDER:
                weights.append(4)
            else:
                weights.append(1)

        return random.choices(self.players, weights,k=1)[0]
    
    def get_midfielder(self):
        midfielder_list = [player for player in self.players if player.position == "MID"]
        return random.choice(midfielder_list)
    
    def get_attacker(self):
        weights = []
        for player in self.players:
            if player.position == Position.DEFENDER:
                weights.append(1)
            elif player.position == Position.MIDFIELDER:
                weights.append(4)
            else:
                weights.append(10)

        return random.choices(self.players, weights,k=1)[0]

class Player:
    def __init__(self, name, position, skill):
        self.name = name
        self.position = position 
        self.skill = skill

class Position(Enum):
    ATTACKER = auto()
    MIDFIELDER = auto()
    DEFENDER = auto()