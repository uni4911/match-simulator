from __future__ import annotations
import random 
from src.models import Team, FieldPlayer, Goalkeeper, Player, MatchTeam, MatchPlayer
from enum import Enum, auto
from typing import Optional, Final, Type
from abc import ABC, abstractmethod
from src.commentator import Commentator
from src.events import (MatchEvent, Goal, KickoffEvent, ShotSave, Foul, PenaltyKickGoal, 
                        RedCardFoul, YellowCardFoul, GoalWithAssist, DoubleYellowCard, MatchEndEvent,
                        Substitution, HalfTimeEvent, InjuryEvent)
from src.event_bus import EventBus
import math

STANDARD_MATCH_LENGTH: Final[int] = 5400
PASS_CHANCE:Final[float] = 0.30
ATTACK_CHANCE: Final[float] = 0.70
MIN_SECONDS_PASSESD: Final[int] = 5
MAX_SECONDS_PASSED: Final[int] = 15
GOALKEEPER_SCORE_MODIFIER: Final[int] = 3
SHOT_ON_GOAL_CHANCE: Final[float] = 0.3
FOUL_PUNISHMENTS: Final[str] = ['yellow_card','red_card','normal_foul']
FOUL_WEIGHTS_DURING_MIDPLAY: Final[float] = [9.5,0.5,90]
FOUL_WEIGHTS_DURING_ATTACK: Final[float] = [15,1,84]
FOUL_AFTERMATH_DURING_ATTACK: Final[str] = ['penalty_kick','dangerous_freekick']
FOUL_AFTERMATH_DURING_ATTACK_WEIGHT: Final[int] = [10,90]
FOUL_AFTERMATH_DURING_MIDPLAY: Final[str] = ['freekick']
PENALTY_KICK_MODIFIER: Final[int] = 3
MIDFIELDPLAY_OPTIONS: Final[str] = ['long_shot','pass','shot_inside']
PASS_RECIEVRS = ["attacker", "midfielder", "defender"]
PASS_RECIVERS_WEIGHTS = [50, 35, 15]


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
        exponent: int = 2
        if attack ** exponent + defence ** exponent <= 0:
            return False
        result = random.randint(1, attack ** exponent + defence ** exponent)
        return result <= attack ** exponent
    
    @abstractmethod
    def execute(self, match: Match) -> 'State':
        pass

class KickOff(State):
    def __init__(self, executing_team: MatchTeam, half: int = 1):
        self.executing_team: MatchTeam = executing_team
        self.half: int = half

    def execute(self, match: Match) -> 'State':
        match.player_with_ball = self.executing_team.get_midfielder()
        match.add_event(KickoffEvent(match.current_second, self.executing_team.team.name, half=self.half))
        return MidfieldPlay()
    
class MidfieldPlay(State):
    def execute(self, match: Match) -> 'State':
        attacking_midfielder: MatchPlayer = match.player_with_ball
        defending_midfielder: MatchPlayer = match.defending_team.get_midfielder()

        midfield_control_ratio = match.team_with_ball.midfield_power/match.defending_team.midfield_power

        home_ball_possession_chance: int = int(attacking_midfielder.ball_possession_chance(match.team_with_ball.relative_strength_modifier))
        away_ball_possession_chance: int = int(defending_midfielder.ball_take_over_chance(match.defending_team.relative_strength_modifier))

        winner = self.winner_choose(home_ball_possession_chance, away_ball_possession_chance)
      
        attack_probability = (1 - ATTACK_CHANCE) * midfield_control_ratio

        if winner:
            match.player_with_ball = attacking_midfielder
            if random.random() < 0.15:
                return ShotOnGoal()
        else:
            match.change_posession(match.player_with_ball)
            match.player_with_ball = defending_midfielder
        if random.random() < attack_probability:
            return Attack()
        else:
            return MidfieldPlay()   
class Attack(State):
    def execute(self, match: Match) -> 'State':
        attacking_player: MatchPlayer = match.player_with_ball
        defending_player: MatchPlayer = match.defending_team.get_defender()

        attack_score: int = attacking_player.shooting 
        defence_score: int = defending_player.defending 
        winner: bool = self.winner_choose(attack_score, defence_score)

        if winner:
            if random.random() > PASS_CHANCE:
                pass_recipient_type = random.choices(PASS_RECIEVRS, PASS_RECIVERS_WEIGHTS, k=1)[0]
                if pass_recipient_type == "midfielder":
                    receiver = match.team_with_ball.get_midfielder(excluded_player=match.player_with_ball)
                elif pass_recipient_type == "defender":
                    receiver = match.team_with_ball.get_defender(excluded_player=match.player_with_ball)
                else:
                    receiver = match.team_with_ball.get_attacker(excluded_player=match.player_with_ball)
                match.pass_ball(receiver)
            return random.choices([ShotOnGoal(),AttackFoul(defending_player, match.player_with_ball)])[0]
        else:
            match.change_posession(defending_player)
            return MidfieldPlay()
        
class ShotOnGoal(State):
    def execute(self, match: Match) -> 'State':
        goalkeeper: Goalkeeper = match.defending_team.get_goalkeeper()
        goalkeeper_score: int = int(goalkeeper.goalkeeping_score * GOALKEEPER_SCORE_MODIFIER)
        attack_score: int = match.player_with_ball.shooting 

        winner: bool = self.winner_choose(attack_score, goalkeeper_score)
        
        if random.random() < SHOT_ON_GOAL_CHANCE:
            if winner:
                match.player_with_ball.goals += 1
                if match.potential_assistant:
                    match.add_event(GoalWithAssist(match.current_second, match.player_with_ball.player.name, match.team_with_ball.team.name,match.potential_assistant.player.name))
                    match.potential_assistant.assists += 1
                else:
                    match.add_event(Goal(match.current_second, match.player_with_ball.player.name, match.team_with_ball.team.name))
                match.potential_assistant = None
                if match.team_with_ball == match.home_team:
                    match.home_score += 1
                    return KickOff(match.away_team)
                else:
                    match.away_score += 1
                    return KickOff(match.home_team)
            else:
                match.potential_assistant = None
                return MidfieldPlay()
        else:
            match.potential_assistant = None
            match.add_event(ShotSave(match.current_second,goalkeeper.name,match.team_with_ball.team.name))
            return random.choices([CornerKick(),MidfieldPlay()],[15,85],k=1)[0]


class CornerKick(State):

    def execute(self, match: Match) -> 'State':
        corner_kick_taker = match.team_with_ball.get_corner_taker()
        attacker = match.team_with_ball.get_heading_player(excluded_player=corner_kick_taker)
        defender = match.defending_team.get_heading_player()

        winner = self.winner_choose(attacker.heading_score, defender.heading_score)
        if winner:
            match.player_with_ball = attacker
            match.potential_assistant = corner_kick_taker
            return ShotOnGoal()
        else:
            match.change_posession(defender)
            return MidfieldPlay()


class AttackFoul(State):
    def __init__(self,fouling_player: MatchPlayer, fouled_player: MatchPlayer | None = None):
        self.fouling_player: MatchPlayer = fouling_player
        self.fouled_player: MatchPlayer | None = fouled_player
        
    def execute(self, match: Match) -> 'State':      
        foul_punishment = random.choices(FOUL_PUNISHMENTS, FOUL_WEIGHTS_DURING_ATTACK, k=1)[0]
        foul_aftermath = random.choices(FOUL_AFTERMATH_DURING_ATTACK, FOUL_AFTERMATH_DURING_ATTACK_WEIGHT, k=1)[0]
        
        if foul_punishment == 'yellow_card':
            is_second_yellow = self.fouling_player.receive_card(foul_punishment)
            if is_second_yellow:
                match.add_event(DoubleYellowCard(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath))
            else:
                match.add_event(YellowCardFoul(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath))
        elif foul_punishment == 'red_card':
            self.fouling_player.receive_card(foul_punishment)
            match.add_event(RedCardFoul(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath))
        else:
            match.add_event(Foul(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath))
            
        target = self.fouled_player or match.player_with_ball
        if target is not None:
            match.process_injury_risk(target, foul_punishment=foul_punishment)

        return PenaltyKick() if foul_aftermath == 'penalty_kick' else DangerousFreekick()
class PenaltyKick(State):
    def execute(self, match: Match) -> 'State':
        goalkeeper: Goalkeeper = match.defending_team.get_goalkeeper()
        penalty_taker: MatchPlayer  = match.team_with_ball.get_penalty_taker()
        match.player_with_ball = penalty_taker

        winner = self.winner_choose(penalty_taker.shooting * PENALTY_KICK_MODIFIER, goalkeeper.goalkeeping_score)
        if winner:
            match.add_event(PenaltyKickGoal(match.current_second, penalty_taker.player.name, match.team_with_ball.team.name))
            penalty_taker.goals += 1
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
                    match.potential_assistant = match.player_with_ball
                    match.player_with_ball = match.team_with_ball.get_attacker(excluded_player=freekick_taker)
                    return ShotOnGoal()
                else:
                    return MidfieldPlay()  



EVENT_OR_STATE_DURATIONS: dict[Type[MatchEvent] | Type[State], tuple[int, int]] = {
    KickoffEvent: (15, 30),
    Goal: (30, 60),
    GoalWithAssist: (35, 65),
    PenaltyKickGoal: (45, 90),
    ShotSave: (10, 25),
    Foul: (10, 20),
    YellowCardFoul: (20, 40),
    RedCardFoul: (40, 80),
    DoubleYellowCard: (40, 80),
    InjuryEvent: (20, 40),
    HalfTimeEvent: (30, 60),
    MatchEndEvent: (0, 0), 
    KickOff: (5, 10),          
    MidfieldPlay: (3, 8),      
    Attack: (4, 10),           
    ShotOnGoal: (2, 5),    
    AttackFoul: (2, 5),    
    PenaltyKick: (20, 40),     
    DangerousFreekick: (15, 35),
    Substitution: (30, 45)
}
            
class MatchEngine:
    def __init__(self, commentator: Commentator | None = None, speed_factor: float = 0.1, event_bus: EventBus | None = None):
        self.commentator: Commentator | None = commentator
        self.speed_factor: float = speed_factor
        self.event_bus: EventBus | None = event_bus
        
        
    def play_match(self, match: Match) -> None:
        if self.event_bus is not None and match.event_bus is None:
            match.event_bus = self.event_bus

        first_half_executing_team = match.current_state.executing_team
        added_seconds_1st = random.randint(30, 180)
        added_seconds_2nd = random.randint(60, 300)

        for half in (1, 2):
            match.half = half

            if half == 1:
                target_second = 2700 + added_seconds_1st
            else:
                target_second = 5400 + added_seconds_2nd
                second_half_executing_team = match.home_team if first_half_executing_team == match.away_team else match.away_team
                match.current_state = KickOff(second_half_executing_team, half=2)

            while match.current_second <= target_second:
                for team in [match.home_team, match.away_team]:
                    sub_result = team.check_and_make_auto_substitution()
                    if sub_result is not None:
                        player_off, player_in = sub_result
                        match.add_event(Substitution(match.current_second, team.team.name, player_in.player.name, player_off.player.name))
                    
                    # Check non-contact injury risk for low-stamina active players
                    for player in team.active_players:
                        if player.current_stamina < 0.35 and not player.is_injured:
                            match.process_injury_risk(player, non_contact=True)

                current_events_length = len(match.match_events)
                match.current_state = match.current_state.execute(match)

                if len(match.match_events) > current_events_length:
                    time_range = EVENT_OR_STATE_DURATIONS.get(type(match.match_events[-1]), (5, 15))
                else:
                    time_range = EVENT_OR_STATE_DURATIONS.get(type(match.current_state), (3, 8))
                time_passed = random.randint(*time_range)
                match.current_second += time_passed
                match.home_team.update_stamina(time_passed, [match.player_with_ball])
                match.away_team.update_stamina(time_passed, [match.player_with_ball])
                if self.commentator and match.event_bus is None:
                    self.commentator.comment(match)

            if half == 1:
                match.add_event(HalfTimeEvent(match.current_second, home_score=match.home_score, away_score=match.away_score))
                match.home_team.recover_stamina(0.20)
                match.away_team.recover_stamina(0.20)
                match.current_second = 2700
            else:
                match.add_event(MatchEndEvent(match.current_second))
            if self.commentator and match.event_bus is None:
                self.commentator.comment(match)

            
            

            
class Match:
    def __init__(self, home_team: MatchTeam, away_team: MatchTeam, event_bus: EventBus | None = None):
        self.home_team: MatchTeam = home_team
        self.away_team: MatchTeam = away_team
        self.event_bus: EventBus | None = event_bus
        self.home_score: int = 0
        self.away_score: int = 0
        self.current_state: 'State' = KickOff(random.choice([self.home_team,self.away_team]))
        self.current_second: int = 0
        self.max_second: int = STANDARD_MATCH_LENGTH
        self.player_with_ball: MatchPlayer | None = None
        self.match_events: list[MatchEvent] = [] 
        self.potential_assistant: MatchPlayer| None = None
        self.additional_time: int = 0
        self.half: int = 1

    def add_event(self, event: MatchEvent) -> None:
        self.match_events.append(event)
        if self.event_bus is not None:
            self.event_bus.publish(event)

    def process_injury_risk(self, player: MatchPlayer, foul_punishment: str | None = None, non_contact: bool = False) -> None:
        if player.is_injured or player.is_forced_off:
            return

        if non_contact:
            base_prob = 0.008
        elif foul_punishment == 'red_card':
            base_prob = 0.35
        elif foul_punishment == 'yellow_card':
            base_prob = 0.15
        else:
            base_prob = 0.05

        fatigue_factor = 1.0 + (1.0 - player.current_stamina) * 0.5
        injury_chance = base_prob * fatigue_factor

        if random.random() < injury_chance:
            severity = "severe" if random.random() < 0.30 else "minor"
            player_team = self.home_team if self.home_team.has_player(player.player) else self.away_team

            sub_result = player_team.handle_injury(player, severity=severity)

            self.add_event(InjuryEvent(
                second=self.current_second,
                player=player.player.name,
                team=player_team.team.name,
                severity=severity,
                forced_off=(severity == "severe")
            ))

            if sub_result is not None:
                p_off, p_in = sub_result
                self.add_event(Substitution(self.current_second, player_team.team.name, p_in.player.name, p_off.player.name))


    @property
    def team_with_ball(self) -> Team | None:
        if self.player_with_ball is None:
            return None
        elif self.away_team.has_player(self.player_with_ball):
            return self.away_team
        else:
            return self.home_team
        
    @property
    def defending_team(self) -> MatchTeam | None:
        if self.player_with_ball is None:
            return None
        return self.home_team if self.team_with_ball == self.away_team else self.away_team

    def pass_ball(self, receiver: MatchPlayer) -> None:
        self.potential_assistant = self.player_with_ball
        self.player_with_ball = receiver

    def change_posession(self, new_player: MatchPlayer) -> None:
        self.player_with_ball = new_player
        self.potential_assistant = None
