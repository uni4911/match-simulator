from __future__ import annotations
import random 
from src.models import Team, FieldPlayer, Goalkeeper, Player, MatchTeam, MatchPlayer, TeamStatsMatch, DEFENCE_POSITIONS
from enum import Enum, auto
from typing import Optional, Final, Type
from abc import ABC, abstractmethod
from src.events.commentator import Commentator
from src.events.events import (MatchEvent, Goal, KickoffEvent, ShotSave, Foul, PenaltyKickGoal, 
                        RedCardFoul, YellowCardFoul, GoalWithAssist, DoubleYellowCard, MatchEndEvent,
                        Substitution, HalfTimeEvent, InjuryEvent, LongShotGoal, LongShotEvent,
                        WingPlayEvent, BuildUpEvent, InterceptionEvent, PossessionTimeEvent,
                        PassEvent, ShotOffTargetEvent, CornerKickEvent)
from src.events.event_bus import EventBus
from src.events.stats_tracker import MatchStatsTracker
import math

STANDARD_MATCH_LENGTH: Final[int] = 5400
PASS_CHANCE: Final[float] = 0.30
ATTACK_CHANCE: Final[float] = 0.70
MIN_SECONDS_PASSED: Final[int] = 5
MIN_SECONDS_PASSESD: Final[int] = MIN_SECONDS_PASSED
MAX_SECONDS_PASSED: Final[int] = 15
GOALKEEPER_SCORE_MODIFIER: Final[float] = 1.85
SHOT_ON_GOAL_CHANCE: Final[float] = 0.3
FOUL_PUNISHMENTS: Final[list[str]] = ['yellow_card', 'red_card', 'normal_foul']
FOUL_WEIGHTS_DURING_MIDPLAY: Final[list[float]] = [6.0, 0.1, 93.9]
FOUL_WEIGHTS_DURING_ATTACK: Final[list[float]] = [10.0, 0.2, 89.8]
FOUL_AFTERMATH_DURING_ATTACK: Final[list[str]] = ['penalty_kick', 'dangerous_freekick']
FOUL_AFTERMATH_DURING_ATTACK_WEIGHT: Final[list[int]] = [10, 90]
FOUL_AFTERMATH_DURING_MIDPLAY: Final[list[str]] = ['freekick']
PENALTY_KICK_MODIFIER: Final[int] = 3
MIDFIELDPLAY_OPTIONS: Final[list[str]] = ['long_shot', 'pass', 'shot_inside']
PASS_RECEIVERS = ["attacker", "winger", "cam", "midfielder"]
PASS_RECIEVRS = PASS_RECEIVERS
PASS_RECEIVERS_WEIGHTS = [50, 22, 18, 10]
PASS_RECIVERS_WEIGHTS = PASS_RECEIVERS_WEIGHTS


class MatchState(Enum):
    KICK_OFF = auto()
    MIDFIELD_PLAY = auto()
    BUILD_UP = auto()
    WING_ATTACK = auto()
    HOME_ATTACK = auto()
    AWAY_ATTACK = auto()
    LONG_SHOT = auto()
    SHOT_ON_GOAL = auto()
    MATCH_END = auto()

class State(ABC):

    @staticmethod
    def winner_choose(attack: float, defence: float, attack_boost: float = 1.0, defence_boost: float = 1.0) -> bool:
        exponent: float = 2.6
        atk_val = float(attack) * attack_boost
        def_val = float(defence) * defence_boost
        if atk_val <= 0:
            return False
        if def_val <= 0:
            return True
        val_a = atk_val ** exponent
        val_d = def_val ** exponent
        total = val_a + val_d
        return random.random() < (val_a / total)
    
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

        atk_mid_power = (match.team_with_ball.midfield_power / 70.0) if match.team_with_ball else 1.0
        def_mid_power = (match.defending_team.midfield_power / 70.0) if match.defending_team else 1.0

        home_ball_possession_chance: int = int(attacking_midfielder.ball_possession_chance(atk_mid_power))
        away_ball_possession_chance: int = int(defending_midfielder.ball_take_over_chance(def_mid_power))

        atk_boost = match.get_team_boost(match.team_with_ball)
        def_boost = match.get_team_boost(match.defending_team)
        winner = self.winner_choose(home_ball_possession_chance, away_ball_possession_chance, attack_boost=atk_boost, defence_boost=def_boost)

        if winner:
            match.player_with_ball = attacking_midfielder
            for _ in range(random.randint(1, 3)):
                receiver = match.team_with_ball.get_midfielder(excluded_player=match.player_with_ball)
                match.pass_ball(receiver)

            quality_factor = min(1.3, max(0.7, atk_mid_power))
            roll = random.random()
            if roll < 0.03:
                return LongShot()
            elif roll < 0.03 + 0.22 * quality_factor:
                return WingAttack()
            elif roll < 0.03 + (0.22 + 0.43) * quality_factor:
                return BuildUp()
            elif roll < 0.85:
                return MidfieldPlay()
            else:
                return Attack()
        else:
            if random.random() < 0.05:
                return AttackFoul(defending_midfielder, attacking_midfielder)
            else:
                match.add_event(InterceptionEvent(match.current_second, defending_midfielder.player.name, match.defending_team.team.name))
                match.change_posession(defending_midfielder)
                return MidfieldPlay()

class BuildUp(State):
    def execute(self, match: Match) -> 'State':
        num_passes = random.randint(2, 4)
        for _ in range(num_passes):
            pass_recipient_type = random.choices(["defender", "midfielder", "winger", "cam"], [20, 50, 15, 15], k=1)[0]
            if pass_recipient_type == "defender":
                receiver = match.team_with_ball.get_defender(excluded_player=match.player_with_ball)
            elif pass_recipient_type == "winger":
                receiver = match.team_with_ball.get_winger(excluded_player=match.player_with_ball)
            elif pass_recipient_type == "cam":
                receiver = match.team_with_ball.get_cam(excluded_player=match.player_with_ball)
            else:
                receiver = match.team_with_ball.get_midfielder(excluded_player=match.player_with_ball)
            match.pass_ball(receiver)

        passer = match.player_with_ball

        if random.random() < 0.30:
            match.add_event(BuildUpEvent(match.current_second, match.team_with_ball.team.name, passer.player.name))

        quality_factor = min(1.3, max(0.7, (match.team_with_ball.midfield_power / 70.0) if match.team_with_ball else 1.0))
        roll = random.random()
        if roll < 0.25 * quality_factor:
            return Attack()
        elif roll < (0.25 + 0.30) * quality_factor:
            return WingAttack()
        elif roll < 0.80:
            return MidfieldPlay()
        else:
            interceptor = match.defending_team.get_defender()
            if random.random() < 0.05:
                return AttackFoul(interceptor, passer)
            else:
                match.add_event(InterceptionEvent(match.current_second, interceptor.player.name, match.defending_team.team.name))
                match.change_posession(interceptor)
                return MidfieldPlay()

class WingAttack(State):
    def execute(self, match: Match) -> 'State':
        winger = match.team_with_ball.get_winger()
        fullback = match.defending_team.get_defender()
        match.player_with_ball = winger

        atk_boost = match.get_team_boost(match.team_with_ball)
        def_boost = match.get_team_boost(match.defending_team)
        winner = self.winner_choose(winger.dribbling, fullback.defending, attack_boost=atk_boost, defence_boost=def_boost)

        if winner:
            roll = random.random()
            if roll < 0.50:
                match.add_event(WingPlayEvent(match.current_second, winger.player.name, match.team_with_ball.team.name, "cross"))
                receiver = match.team_with_ball.get_attacker(excluded_player=winger)
                match.pass_ball(receiver)
                if random.random() < 0.45:
                    return ShotOnGoal()
                else:
                    return random.choices([CornerKick(), MidfieldPlay()], [25, 75], k=1)[0]
            elif roll < 0.78:
                match.add_event(WingPlayEvent(match.current_second, winger.player.name, match.team_with_ball.team.name, "cut_inside"))
                return ShotOnGoal()
            else:
                receiver = match.team_with_ball.get_cam(excluded_player=winger)
                match.pass_ball(receiver)
                return BuildUp()
        else:
            if random.random() < 0.05:
                return AttackFoul(fullback, winger)
            else:
                match.add_event(InterceptionEvent(match.current_second, fullback.player.name, match.defending_team.team.name))
                match.change_posession(fullback)
                return MidfieldPlay()

class LongShot(State):
    def execute(self, match: Match) -> 'State':
        shooter = match.player_with_ball
        goalkeeper = match.defending_team.get_goalkeeper()

        attack_score = int((shooter.shooting * 0.75) + (shooter.dribbling * 0.25))
        goalkeeper_score = int(goalkeeper.goalkeeping_score * GOALKEEPER_SCORE_MODIFIER)

        atk_boost = match.get_team_boost(match.team_with_ball)
        def_boost = match.get_team_boost(match.defending_team)
        winner = self.winner_choose(attack_score, goalkeeper_score, attack_boost=atk_boost, defence_boost=def_boost)

        if random.random() < 0.35:
            if winner:
                shooter.goals += 1
                if match.potential_assistant:
                    match.add_event(LongShotGoal(match.current_second, shooter.player.name, match.team_with_ball.team.name, match.potential_assistant.player.name))
                    match.potential_assistant.assists += 1
                else:
                    match.add_event(LongShotGoal(match.current_second, shooter.player.name, match.team_with_ball.team.name, assistant=""))
                match.potential_assistant = None
                if match.team_with_ball == match.home_team:
                    match.home_score += 1
                    return KickOff(match.away_team)
                else:
                    match.away_score += 1
                    return KickOff(match.home_team)
            else:
                match.potential_assistant = None
                match.add_event(LongShotEvent(match.current_second, shooter.player.name, match.team_with_ball.team.name, "saved"))
                return random.choices([CornerKick(), MidfieldPlay()], [20, 80], k=1)[0]
        else:
            match.potential_assistant = None
            match.add_event(LongShotEvent(match.current_second, shooter.player.name, match.team_with_ball.team.name, "missed"))
            return MidfieldPlay()

class Attack(State):
    def execute(self, match: Match) -> 'State':
        if match.player_with_ball.assigned_position in DEFENCE_POSITIONS:
            receiver = match.team_with_ball.get_attacker(excluded_player=match.player_with_ball)
            match.pass_ball(receiver)

        attacking_player: MatchPlayer = match.player_with_ball
        defending_player: MatchPlayer = match.defending_team.get_defender()

        attack_score: int = int(attacking_player.shooting * 0.6 + attacking_player.dribbling * 0.4)
        defence_score: int = int(defending_player.defending * 0.7 + defending_player.physical * 0.3)
        atk_boost = match.get_team_boost(match.team_with_ball)
        def_boost = match.get_team_boost(match.defending_team)
        winner: bool = self.winner_choose(attack_score, defence_score, attack_boost=atk_boost, defence_boost=def_boost)

        if winner:
            roll = random.random()
            if roll < 0.40:
                pass_recipient_type = random.choices(PASS_RECEIVERS, PASS_RECEIVERS_WEIGHTS, k=1)[0]
                if pass_recipient_type == "winger":
                    receiver = match.team_with_ball.get_winger(excluded_player=match.player_with_ball)
                elif pass_recipient_type == "cam":
                    receiver = match.team_with_ball.get_cam(excluded_player=match.player_with_ball)
                elif pass_recipient_type == "midfielder":
                    receiver = match.team_with_ball.get_midfielder(excluded_player=match.player_with_ball)
                elif pass_recipient_type == "defender":
                    receiver = match.team_with_ball.get_defender(excluded_player=match.player_with_ball)
                else:
                    receiver = match.team_with_ball.get_attacker(excluded_player=match.player_with_ball)
                match.pass_ball(receiver)
                return random.choices([ShotOnGoal(), AttackFoul(defending_player, match.player_with_ball)], [85, 15])[0]
            elif roll < 0.82:
                return random.choices([ShotOnGoal(), AttackFoul(defending_player, match.player_with_ball)], [85, 15])[0]
            else:
                receiver = match.team_with_ball.get_midfielder(excluded_player=match.player_with_ball)
                match.pass_ball(receiver)
                return BuildUp()
        else:
            if random.random() < 0.05:
                return AttackFoul(defending_player, attacking_player)
            else:
                match.add_event(InterceptionEvent(match.current_second, defending_player.player.name, match.defending_team.team.name))
                match.change_posession(defending_player)
                return MidfieldPlay()

        
class ShotOnGoal(State):
    def execute(self, match: Match) -> 'State':
        goalkeeper: Goalkeeper = match.defending_team.get_goalkeeper()
        goalkeeper_score: int = int(goalkeeper.goalkeeping_score * GOALKEEPER_SCORE_MODIFIER)
        attack_score: int = match.player_with_ball.shooting 

        atk_boost = match.get_team_boost(match.team_with_ball)
        def_boost = match.get_team_boost(match.defending_team)
        winner: bool = self.winner_choose(attack_score, goalkeeper_score, attack_boost=atk_boost, defence_boost=def_boost)
        
        roll = random.random()
        if roll < 0.36:
            if winner:
                match.player_with_ball.goals += 1
                if match.potential_assistant:
                    match.add_event(GoalWithAssist(match.current_second, match.player_with_ball.player.name, match.team_with_ball.team.name, match.potential_assistant.player.name))
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
                match.add_event(ShotSave(match.current_second, goalkeeper.name, match.team_with_ball.team.name))
                return random.choices([CornerKick(), MidfieldPlay()], [15, 85], k=1)[0]
        elif roll < 0.72:
            if match.team_with_ball:
                match.add_event(ShotOffTargetEvent(match.current_second, match.player_with_ball.player.name, match.team_with_ball.team.name))
            match.potential_assistant = None
            return MidfieldPlay()
        else:
            match.potential_assistant = None
            return random.choices([CornerKick(), MidfieldPlay()], [20, 80], k=1)[0]


class CornerKick(State):

    def execute(self, match: Match) -> 'State':
        corner_kick_taker = match.team_with_ball.get_corner_taker()
        if match.team_with_ball:
            match.add_event(CornerKickEvent(match.current_second, match.team_with_ball.team.name, corner_kick_taker.player.name))
        attacker = match.team_with_ball.get_heading_player(excluded_player=corner_kick_taker)
        defender = match.defending_team.get_heading_player()

        atk_boost = match.get_team_boost(match.team_with_ball)
        def_boost = match.get_team_boost(match.defending_team)
        winner = self.winner_choose(attacker.heading_score, defender.heading_score, attack_boost=atk_boost, defence_boost=def_boost)
        if winner:
            match.pass_ball(attacker)
            match.potential_assistant = corner_kick_taker
            return ShotOnGoal()
        else:
            match.change_posession(defender)
            return MidfieldPlay()


class AttackFoul(State):
    def __init__(self, fouling_player: MatchPlayer, fouled_player: MatchPlayer | None = None):
        self.fouling_player: MatchPlayer = fouling_player
        self.fouled_player: MatchPlayer | None = fouled_player
        
    def execute(self, match: Match) -> 'State':      
        foul_punishment = random.choices(FOUL_PUNISHMENTS, FOUL_WEIGHTS_DURING_ATTACK, k=1)[0]
        foul_aftermath = random.choices(FOUL_AFTERMATH_DURING_ATTACK, FOUL_AFTERMATH_DURING_ATTACK_WEIGHT, k=1)[0]
        
        fouling_team = match.home_team if match.home_team.has_player(self.fouling_player) else match.away_team
        team_name = fouling_team.team.name if fouling_team else ""

        if foul_punishment == 'yellow_card':
            is_second_yellow = self.fouling_player.receive_card(foul_punishment)
            if is_second_yellow:
                match.add_event(DoubleYellowCard(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath, team=team_name))
            else:
                match.add_event(YellowCardFoul(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath, team=team_name))
        elif foul_punishment == 'red_card':
            self.fouling_player.receive_card(foul_punishment)
            match.add_event(RedCardFoul(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath, team=team_name))
        else:
            match.add_event(Foul(match.current_second, self.fouling_player.player.name, foul_punishment, foul_aftermath, team=team_name))
            
        target = self.fouled_player or match.player_with_ball
        if target is not None:
            match.process_injury_risk(target, foul_punishment=foul_punishment)

        return PenaltyKick() if foul_aftermath == 'penalty_kick' else DangerousFreekick()


class PenaltyKick(State):
    def execute(self, match: Match) -> 'State':
        goalkeeper: Goalkeeper = match.defending_team.get_goalkeeper()
        penalty_taker: MatchPlayer = match.team_with_ball.get_penalty_taker()
        match.player_with_ball = penalty_taker

        atk_boost = match.get_team_boost(match.team_with_ball)
        def_boost = match.get_team_boost(match.defending_team)
        winner = self.winner_choose(penalty_taker.shooting * PENALTY_KICK_MODIFIER, goalkeeper.goalkeeping_score, attack_boost=atk_boost, defence_boost=def_boost)
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
            match.add_event(ShotSave(match.current_second, goalkeeper.name, match.team_with_ball.team.name))
            return random.choices([MidfieldPlay(), Attack()], [80, 20], k=1)[0]


class DangerousFreekick(State):
    def execute(self, match: Match) -> 'State':
        freekick_taker: FieldPlayer = match.team_with_ball.get_freekick_taker()
        match.player_with_ball = freekick_taker
        shoot_or_cross: str = random.choices(['shoot', 'cross'], [25, 75], k=1)[0]

        if shoot_or_cross == 'shoot':
            return ShotOnGoal()
        else:
            receiver = match.team_with_ball.get_attacker(excluded_player=freekick_taker)
            match.pass_ball(receiver)
            if random.random() < 0.60:
                return ShotOnGoal()
            else:
                return MidfieldPlay()  


EVENT_OR_STATE_DURATIONS: dict[Type[MatchEvent] | Type[State], tuple[int, int]] = {
    KickoffEvent: (15, 30),
    Goal: (30, 60),
    GoalWithAssist: (35, 65),
    LongShotGoal: (35, 65),
    PenaltyKickGoal: (45, 90),
    ShotSave: (10, 25),
    LongShotEvent: (8, 18),
    WingPlayEvent: (10, 20),
    BuildUpEvent: (10, 20),
    InterceptionEvent: (5, 12),
    Foul: (10, 20),
    YellowCardFoul: (20, 40),
    RedCardFoul: (40, 80),
    DoubleYellowCard: (40, 80),
    InjuryEvent: (20, 40),
    HalfTimeEvent: (30, 60),
    MatchEndEvent: (0, 0), 
    KickOff: (5, 10),          
    MidfieldPlay: (12, 20),
    BuildUp: (14, 24),
    WingAttack: (10, 18),
    LongShot: (4, 8),      
    Attack: (8, 16),           
    ShotOnGoal: (3, 6),    
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
                    sub_result = team.check_and_make_auto_substitution(match.current_second)
                    if sub_result is not None:
                        player_off, player_in = sub_result
                        match.add_event(Substitution(match.current_second, team.team.name, player_in.player.name, player_off.player.name))
                    
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
                match.advance_time(time_passed)
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
        self._event_bus: EventBus = event_bus if event_bus is not None else EventBus()
        self.stats_tracker: MatchStatsTracker = MatchStatsTracker(self, event_bus=self._event_bus)
        self.home_score: int = 0
        self.away_score: int = 0
        self.current_state: 'State' = KickOff(random.choice([self.home_team, self.away_team]))
        self.current_second: int = 0
        self.max_second: int = STANDARD_MATCH_LENGTH
        self.player_with_ball: MatchPlayer | None = None
        self.match_events: list[MatchEvent] = [] 
        self.potential_assistant: MatchPlayer | None = None
        self.additional_time: int = 0
        self.half: int = 1

    @property
    def event_bus(self) -> EventBus | None:
        return self._event_bus

    @event_bus.setter
    def event_bus(self, bus: EventBus | None) -> None:
        if bus is None or bus is self._event_bus:
            return
        self._event_bus = bus
        if hasattr(self, 'stats_tracker') and self.stats_tracker is not None:
            self.stats_tracker.subscribe_to(self._event_bus)

    def get_home_boost(self, team: MatchTeam | None) -> float:
        return 1.05 if team is not None and team == self.home_team else 1.0

    def get_team_boost(self, team: MatchTeam | None) -> float:
        if team is None:
            return 1.0
        home_factor = 1.05 if team == self.home_team else 1.0
        form_factor = getattr(team, 'form_modifier', 1.0)
        return home_factor * form_factor

    def advance_time(self, seconds: int) -> None:
        self.current_second += seconds
        active_players = [self.player_with_ball] if self.player_with_ball else []
        self.home_team.update_stamina(seconds, active_players)
        self.away_team.update_stamina(seconds, active_players)
        if self.team_with_ball:
            self.add_event(PossessionTimeEvent(self.current_second, self.team_with_ball.team.name, seconds))

    def add_event(self, event: MatchEvent) -> None:
        self.match_events.append(event)
        if self._event_bus is not None:
            self._event_bus.publish(event)

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
            player_team = self.home_team if self.home_team.has_player(player) else self.away_team

            sub_result = player_team.handle_injury(player, severity=severity, current_second=self.current_second)

            self.add_event(InjuryEvent(
                second=self.current_second,
                player=player.player.name,
                team=player_team.team.name,
                severity=severity,
                forced_off=(severity == "severe")
            ))

            if sub_result is not None:
                p_off, p_in = sub_result
                self.add_event(Substitution(self.current_second, player_team.team.name, p_in.player.name, p_off.player.name, reason="injury"))

    @property
    def team_with_ball(self) -> MatchTeam | None:
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
        if self.player_with_ball and self.player_with_ball != receiver:
            self.player_with_ball.passes += 1
            if self.team_with_ball:
                self.add_event(PassEvent(self.current_second, self.team_with_ball.team.name, self.player_with_ball.player.name, receiver.player.name))
        self.potential_assistant = self.player_with_ball
        self.player_with_ball = receiver

    def change_posession(self, new_player: MatchPlayer) -> None:
        self.player_with_ball = new_player
        self.potential_assistant = None
