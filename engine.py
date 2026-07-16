import random 
from models import Team, FieldPlayer, Goalkeeper
from enum import Enum, auto
from typing import Optional

class MatchState(Enum):
    KICK_OFF = auto()
    MIDFIELD_PLAY = auto()
    HOME_ATTACK = auto()
    AWAY_ATTACK = auto()
    SHOT_ON_GOAL = auto()
    MATCH_END = auto()

class Match:
    def __init__(self, home_team: Team, away_team: Team):
        self.home_team : Team = home_team
        self.away_team :Team = away_team
        self.home_score : int = 0
        self.away_score : int = 0
        self.current_state : MatchState = MatchState.KICK_OFF
        self.current_minute :int = 0
        self.max_minute :int = 90
        self.player_with_ball :FieldPlayer | None = None

    def resolve_kick_off(self) -> None:
        self.current_state = MatchState.MIDFIELD_PLAY

    def resolve_midfield_play(self) -> bool | None:
        home_midfielder = self.home_team.get_midfielder()
        away_midfielder = self.away_team.get_midfielder()

        home_ball_possession_chance = home_midfielder.passing * home_midfielder.dribbling * random.randint(1,10)
        away_ball_possession_chance = away_midfielder.defending * away_midfielder.physical * random.randint(1,10)

        if home_ball_possession_chance > away_ball_possession_chance:
            self.player_with_ball = home_midfielder
            self.current_state = MatchState.HOME_ATTACK
        elif home_ball_possession_chance < away_ball_possession_chance:
            self.player_with_ball = away_midfielder
            self.current_state = MatchState.AWAY_ATTACK
        else:
            return None
    
    def resolve_attack(self, attacking_team : Team, defending_team: Team) -> bool:
        attacking_player = self.player_with_ball
        defending_player = defending_team.get_defender()

        attack_score = attacking_player.shooting * random.randint(1,10)
        defence_score = defending_player.defending * random.randint(1,10)

        if attack_score > defence_score:
            if random.random() > 0.30:
                new_attacking_player = attacking_team.get_attacker()
                self.player_with_ball = new_attacking_player
            self.current_state = MatchState.SHOT_ON_GOAL
            return True
        else:
            self.current_state = MatchState.MIDFIELD_PLAY
            return False
    
    def resolve_shot_on_goal(self,attacking_team :Team,defending_team :Team) -> bool | None:
        goalkeeper = defending_team.get_goalkeeper()
        goalkeeper_score = ((goalkeeper.reflexes * 0.6) + (goalkeeper.positioning*0.4)) * random.randint(1,10)
        attack_score = self.player_with_ball.shooting * random.randint(1,10)

        self.player_with_ball = None

        if attack_score > goalkeeper_score:
            self.current_state = MatchState.KICK_OFF
            return True
        else:
            self.current_state = MatchState.MIDFIELD_PLAY
            return False
        
    def play_match(self) -> None:
        while self.current_minute <= self.max_minute:

            match self.current_state:
                case MatchState.KICK_OFF:
                    self.resolve_kick_off()
                    self.current_minute += 1
                case MatchState.MIDFIELD_PLAY:
                    self.resolve_midfield_play()
                    self.current_minute += 3
                case MatchState.HOME_ATTACK:
                    self.resolve_attack(self.home_team,self.away_team)
                    self.current_minute += 1
                case MatchState.AWAY_ATTACK:
                    self.resolve_attack(self.away_team,self.home_team)
                    self.current_minute += 1
                case MatchState.SHOT_ON_GOAL:
                    shooter = self.player_with_ball
                    if shooter in self.home_team.players:
                        attacking_team = self.home_team
                        defending_team = self.away_team
                    else:
                        attacking_team = self.away_team
                        defending_team = self.home_team
                    
                    is_goal = self.resolve_shot_on_goal(attacking_team,defending_team)

                    if is_goal:
                        if attacking_team == self.home_team:
                            self.home_score +=1
                        else:
                            self.away_score +=1 
                    self.current_minute += 1
        
        self.current_state = MatchState.MATCH_END

    def show_score(self) -> None:
        print(f"{self.home_team.name}: {self.home_score}")
        print(f"{self.away_team.name}: {self.away_score}")