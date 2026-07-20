from __future__ import annotations
import random 
from models import Team, FieldPlayer, Goalkeeper
from enum import Enum, auto
from typing import Optional, Final

STANDARD_MATCH_LENGTH: Final[int] = 90
PASS_CHANCE:Final[float] = 0.30
DEFAULT_MINUTE_MODIFIER: Final[int]  = 1
MIDFIELD_PLAY_MINUTE_MODIFIER: Final[int] = 3

class MatchState(Enum):
    KICK_OFF = auto()
    MIDFIELD_PLAY = auto()
    HOME_ATTACK = auto()
    AWAY_ATTACK = auto()
    SHOT_ON_GOAL = auto()
    MATCH_END = auto()

class MatchEngine:
    def __init__(self):
        pass
    
    def _winner_choose(self, attack: int, defence: int) -> bool:
        if attack + defence <= 0:
            return False
        result = random.randint(1, attack + defence)
        return result <= attack


    def resolve_kick_off(self, match : Match) -> None:
        match.current_state = MatchState.MIDFIELD_PLAY

    def resolve_midfield_play(self, match: Match)  -> None:
        home_midfielder = match.home_team.get_midfielder()
        away_midfielder = match.away_team.get_midfielder()

        home_ball_possession_chance = home_midfielder.ball_possession_chance
        away_ball_possession_chance = away_midfielder.ball_take_over_chance

        winner = self._winner_choose(home_ball_possession_chance, away_ball_possession_chance)

        if winner:
            match.player_with_ball = home_midfielder
            match.current_state = MatchState.HOME_ATTACK
        else:
            match.player_with_ball = away_midfielder
            match.current_state = MatchState.AWAY_ATTACK
        
    
    def resolve_attack(self, attacking_team: Team, defending_team: Team, match: Match) -> bool:
        attacking_player = match.player_with_ball
        defending_player = defending_team.get_defender()

        attack_score = attacking_player.shooting 
        defence_score = defending_player.defending 
        winner = self._winner_choose(attack_score, defence_score)

        if winner:
            if random.random() > PASS_CHANCE:
                new_attacking_player = attacking_team.get_attacker()
                match.player_with_ball = new_attacking_player
            match.current_state = MatchState.SHOT_ON_GOAL
            return True
        else:
            match.current_state = MatchState.MIDFIELD_PLAY
            return False
    
    def resolve_shot_on_goal(self,attacking_team: Team, defending_team: Team, match: Match) -> bool | None:
        goalkeeper = defending_team.get_goalkeeper()
        goalkeeper_score = goalkeeper.goalkeeping_score
        attack_score = match.player_with_ball.shooting 

        winner = self._winner_choose(attack_score, goalkeeper_score)

        if winner:
            match.current_state = MatchState.KICK_OFF
            return True
        else:
            match.current_state = MatchState.MIDFIELD_PLAY
            return False
        
    def play_match(self, match : Match) -> None:
        while match.current_minute <= match.max_minute:

            match match.current_state:
                case MatchState.KICK_OFF:
                    self.resolve_kick_off(match)
                    match.current_minute += DEFAULT_MINUTE_MODIFIER
                case MatchState.MIDFIELD_PLAY:
                    self.resolve_midfield_play(match)
                    match.current_minute += MIDFIELD_PLAY_MINUTE_MODIFIER
                case MatchState.HOME_ATTACK:
                    self.resolve_attack(match.home_team, match.away_team,match)
                    match.current_minute += DEFAULT_MINUTE_MODIFIER
                case MatchState.AWAY_ATTACK:
                    self.resolve_attack(match.away_team, match.home_team,match)
                    match.current_minute += DEFAULT_MINUTE_MODIFIER
                case MatchState.SHOT_ON_GOAL:
                    shooter = match.player_with_ball
                    if shooter in match.home_team.players:
                        attacking_team = match.home_team
                        defending_team = match.away_team
                    else:
                        attacking_team = match.away_team
                        defending_team = match.home_team
                    
                    is_goal = self.resolve_shot_on_goal(attacking_team, defending_team, match)

                    if is_goal:
                        if attacking_team == match.home_team:
                            match.home_score += 1
                        else:
                            match.away_score += 1 
                    match.current_minute += DEFAULT_MINUTE_MODIFIER
        
        match.current_state = MatchState.MATCH_END

class Match:
    def __init__(self, home_team: Team, away_team: Team):
        self.home_team : Team = home_team
        self.away_team :Team = away_team
        self.home_score : int = 0
        self.away_score : int = 0
        self.current_state : MatchState = MatchState.KICK_OFF
        self.current_minute :int = 0
        self.max_minute :int = STANDARD_MATCH_LENGTH
        self.player_with_ball :FieldPlayer | None = None
