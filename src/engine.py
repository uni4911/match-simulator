from __future__ import annotations
import random 
from src.models import Team, FieldPlayer, Goalkeeper, Player
from enum import Enum, auto
from typing import Optional, Final
from abc import ABC, abstractmethod
from src.commentator import Commentator
from src.events import MatchEvent, Goal, KickoffEvent, ShotSave, FoulDuringAttack, PenaltyKickGoal

STANDARD_MATCH_LENGTH: Final[int] = 5400
PASS_CHANCE:Final[float] = 0.30
ATTACK_CHANCE: Final[float] = 0.70
MIN_SECONDS_PASSESD: Final[int] = 5
MAX_SECONDS_PASSED: Final[int] = 15
GOALKEEPER_SCORE_MODIFIER: Final[int] = 4
SHOT_ON_GOAL_CHANCE: Final[float] = 0.3
FOUL_PUNISHMENTS: Final[str] = ['yellow_card','red_card','normal_foul']
FOUL_WEIGHTS_DURING_MIDPLAY: Final[float] = [9.5,0.5,90]
FOUL_WEIGHTS_DURING_ATTACK: Final[float] = [15,1,84]
FOUL_AFTERMATH_DURING_ATTACK: Final[str] = ['penalty_kick','dangerous_freekick']
FOUL_AFTERMATH_DURING_ATTACK_WEIGHT: Final[int] = [10,90]
FOUL_AFTERMATH_DURING_MIDPLAY: Final[str] = ['freekick']
PENALTY_KICK_MODIFIER: Final[int] = 3

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
    def __init__(self, executing_team: Team):
        self.executing_team: Team = executing_team

    def execute(self, match: Match) -> 'State':
        match.player_with_ball = self.executing_team.get_midfielder()
        if match.current_second > 0:
            match.match_events.append(KickoffEvent(match.current_second,self.executing_team.name))
        return MidfieldPlay()
    
class MidfieldPlay(State):
    def execute(self, match: Match) -> 'State':
        attacking_midfielder: FieldPlayer = match.player_with_ball
        defending_midfielder: FieldPlayer = match.defending_team.get_midfielder()

        home_ball_possession_chance: int = attacking_midfielder.ball_possession_chance
        away_ball_possession_chance: int = defending_midfielder.ball_take_over_chance

        winner = self.winner_choose(home_ball_possession_chance, away_ball_possession_chance)
        match.current_second += random.randint(MIN_SECONDS_PASSESD, MAX_SECONDS_PASSED)
        if winner:
            match.player_with_ball = attacking_midfielder
        else:
            match.player_with_ball = defending_midfielder
        if random.random() > ATTACK_CHANCE:
            return Attack()
        else:
            return MidfieldPlay()   
class Attack(State):
    def execute(self, match: Match) -> 'State':
        attacking_player: FieldPlayer = match.player_with_ball
        defending_player: FieldPlayer = match.defending_team.get_defender()

        attack_score: int = attacking_player.shooting 
        defence_score: int = defending_player.defending 
        winner: bool = self.winner_choose(attack_score, defence_score)
        match.current_second += random.randint(MIN_SECONDS_PASSESD, MAX_SECONDS_PASSED)
        if winner:
            if random.random() > PASS_CHANCE:
                new_attacking_player: Player = match.team_with_ball.get_attacker()
                match.player_with_ball = new_attacking_player
            return random.choices([ShotOnGoal(),AttackFoul(defending_player)])[0]
        else:
            return MidfieldPlay()
        
class ShotOnGoal(State):
    def execute(self, match: Match) -> 'State':
        goalkeeper: Goalkeeper = match.defending_team.get_goalkeeper()
        goalkeeper_score: int = int(goalkeeper.goalkeeping_score * GOALKEEPER_SCORE_MODIFIER)
        attack_score: int = match.player_with_ball.shooting 

        winner: bool = self.winner_choose(attack_score, goalkeeper_score)
        match.current_second += random.randint(MIN_SECONDS_PASSESD, MAX_SECONDS_PASSED)
        if random.random() < SHOT_ON_GOAL_CHANCE:
            if winner:
                match.match_events.append(Goal(match.current_second, match.player_with_ball.name, match.team_with_ball.name))
                if match.team_with_ball == match.home_team:
                    match.home_score += 1
                    return KickOff(match.away_team)
                else:
                    match.away_score += 1
                    return KickOff(match.home_team)
            else:
                return MidfieldPlay()
        else:
            match.match_events.append(ShotSave(match.current_second,goalkeeper.name,match.team_with_ball.name))
            return MidfieldPlay()
        
class AttackFoul(State):
    def __init__(self,fouling_player: 'Player'):
        self.fouling_player: 'Player' = fouling_player
        
    def execute(self, match: Match) -> 'State':      
        foul_punishment = random.choices(FOUL_PUNISHMENTS,FOUL_WEIGHTS_DURING_ATTACK,k=1)[0]
        foul_aftermath = random.choices(FOUL_AFTERMATH_DURING_ATTACK,FOUL_AFTERMATH_DURING_ATTACK_WEIGHT,k=1)[0]
        match.match_events.append(FoulDuringAttack(match.current_second,self.fouling_player.name,foul_punishment, foul_aftermath))
        return PenaltyKick() if foul_aftermath == 'penalty_kick' else DangerousFreekick()

class PenaltyKick(State):
    def execute(self, match: Match) -> 'State':
        goalkeeper: Goalkeeper = match.defending_team.get_goalkeeper()
        penalty_taker: FieldPlayer  = match.team_with_ball.get_penalty_taker()

        winner = self.winner_choose(penalty_taker.shooting * PENALTY_KICK_MODIFIER, goalkeeper.goalkeeping_score)
        if winner:
            match.match_events.append(PenaltyKickGoal(match.current_second, match.player_with_ball.name, match.team_with_ball.name))
            if match.team_with_ball == match.home_team:
                match.home_score += 1
                return KickOff(match.away_team)
            else:
                match.away_score += 1
                return KickOff(match.home_team)
        else:
            return random.choices([MidfieldPlay(),Attack()],[80,20],k=1)[0]

class DangerousFreekick(State):
        
        def execute(self, match: Match) -> 'State':
            freekick_taker: FieldPlayer = match.team_with_ball.get_freekick_taker()
            match.player_with_ball = freekick_taker
            shoot_or_cross: 'State' = random.choices(['shoot','cross'],[25,75],k=1)[0]

            if shoot_or_cross == 'shoot':
                return ShotOnGoal()
            else:
                if random.random() > PASS_CHANCE:
                    match.player_with_ball = match.team_with_ball.get_attacker()
                    return ShotOnGoal()
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
        self.current_state : 'State' = KickOff(random.choice([self.home_team,self.away_team]))
        self.current_second :int = 0
        self.max_second :int = STANDARD_MATCH_LENGTH
        self.player_with_ball :FieldPlayer | None = None
        self.match_events: list[MatchEvent] = [] 

    @property
    def team_with_ball(self) -> Team | None:
        if self.player_with_ball is None:
            return None
        elif self.away_team.has_player(self.player_with_ball):
            return self.away_team
        else:
            return self.home_team
        
    @property
    def defending_team(self) -> Team | None:
        if self.player_with_ball is None:
            return None
        return self.home_team if self.team_with_ball == self.away_team else self.away_team

    
