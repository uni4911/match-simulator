from __future__ import annotations
import random 
from src.models import Team, FieldPlayer
from enum import Enum, auto
from typing import Optional, Final
from abc import ABC, abstractmethod
from src.commentator import Commentator

STANDARD_MATCH_LENGTH: Final[int] = 5400
PASS_CHANCE:Final[float] = 0.30
ATTACK_CHANCE: Final[float] = 0.70
MIN_SECONDS_PASSESD: Final[int] = 5
MAX_SECONDS_PASSED: Final[int] = 15
GOALKEEPER_SCORE_MODIFIER: Final[int] = 4
SHOT_ON_GOAL_CHANCE: Final[float] = 0.3

class MatchState(Enum):
    KICK_OFF = auto()
    MIDFIELD_PLAY = auto()
    HOME_ATTACK = auto()
    AWAY_ATTACK = auto()
    SHOT_ON_GOAL = auto()
    MATCH_END = auto()

class State(ABC):

    @staticmethod
    def winner_choose(attack: int, defence: int) -> bool:
        if attack + defence <= 0:
            return False
        result = random.randint(1, attack + defence)
        return result <= attack
    
    @abstractmethod
    def execute(self, match: Match) -> 'State':
        pass

class KickOff(State):
    def execute(self, match: Match) -> 'State':
        match.current_second += random.randint(MIN_SECONDS_PASSESD, MAX_SECONDS_PASSED)
        match.match_events.append(f"{match.current_second // 60} minute: Match started!")
        return MidfieldPlay()
    
class MidfieldPlay(State):
    def execute(self, match: Match) -> 'State':
        home_midfielder = match.home_team.get_midfielder()
        away_midfielder = match.away_team.get_midfielder()

        home_ball_possession_chance = home_midfielder.ball_possession_chance
        away_ball_possession_chance = away_midfielder.ball_take_over_chance

        winner = self.winner_choose(home_ball_possession_chance, away_ball_possession_chance)
        match.current_second += random.randint(MIN_SECONDS_PASSESD, MAX_SECONDS_PASSED)
        if random.random() > ATTACK_CHANCE:
            if winner:
                match.player_with_ball = home_midfielder
            else:
                match.player_with_ball = away_midfielder
            return Attack()
        else:
            return MidfieldPlay()
     
class Attack(State):
    def execute(self, match: Match) -> 'State':
        attacking_player = match.player_with_ball
        defending_player = match.away_team.get_defender() if attacking_player in match.home_team.players else match.home_team.get_defender()

        attack_score = attacking_player.shooting 
        defence_score = defending_player.defending 
        winner = self.winner_choose(attack_score, defence_score)
        match.current_second += random.randint(MIN_SECONDS_PASSESD, MAX_SECONDS_PASSED)
        if winner:
            if random.random() > PASS_CHANCE:
                new_attacking_player = match.away_team.get_attacker() if attacking_player in match.away_team.players else match.home_team.get_attacker()
                match.player_with_ball = new_attacking_player
            return ShotOnGoal()
        else:
            return MidfieldPlay()
        
class ShotOnGoal(State):
    def execute(self, match: Match) -> 'State':
        goalkeeper = match.away_team.get_goalkeeper() if match.player_with_ball in match.home_team.players else match.home_team.get_goalkeeper()
        goalkeeper_score = int(goalkeeper.goalkeeping_score * GOALKEEPER_SCORE_MODIFIER)
        attack_score = match.player_with_ball.shooting 

        winner = self.winner_choose(attack_score, goalkeeper_score)
        match.current_second += random.randint(MIN_SECONDS_PASSESD, MAX_SECONDS_PASSED)
        if random.random() < SHOT_ON_GOAL_CHANCE:
            if winner:
                if match.player_with_ball in match.home_team.players:
                    match.match_events.append(f"{match.current_second // 60} minute: {match.player_with_ball.name} gets a goal!")
                    match.home_score += 1
                else:
                    match.match_events.append(f"{match.current_second // 60} minute: {match.player_with_ball.name} gets a goal!")
                    match.away_score += 1
                return KickOff()
            else:
                return MidfieldPlay()
        else:
            return MidfieldPlay()
        
        
class MatchEngine:
    def __init__(self, commentator: Commentator):
        self.commentator: Commentator = commentator
        pass
        
    def play_match(self, match: Match) -> None:
        while match.current_second <= match.max_second:
            match.current_state = match.current_state.execute(match)
            self.commentator.comment(match)
class Match:
    def __init__(self, home_team: Team, away_team: Team):
        self.home_team : Team = home_team
        self.away_team :Team = away_team
        self.home_score : int = 0
        self.away_score : int = 0
        self.current_state : 'State' = KickOff()
        self.current_second :int = 0
        self.max_second :int = STANDARD_MATCH_LENGTH
        self.player_with_ball :FieldPlayer | None = None
        self.match_events: list[str] = [] 
    
