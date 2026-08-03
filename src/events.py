from dataclasses import dataclass
from typing import Optional
@dataclass(frozen=True)
class MatchEvent:
    second: int

@dataclass(frozen=True)
class KickoffEvent(MatchEvent):
    executing_team: str
    half: int = 1

@dataclass(frozen=True)
class Goal(MatchEvent):
    goalscorer: str
    team: str

@dataclass(frozen=True)
class GoalWithAssist(Goal):
    assistant: str
@dataclass(frozen=True)
class ShotSave(MatchEvent):
    goalkeeper: str
    team: str

@dataclass(frozen=True)
class Foul(MatchEvent):
    fouling_player: str
    punishment: str
    foul_aftermath: str

@dataclass(frozen=True)
class PenaltyKickGoal(Goal):
    pass

@dataclass(frozen=True)
class YellowCardFoul(Foul):
    pass
@dataclass(frozen=True)
class RedCardFoul(Foul):
    pass
@dataclass(frozen=True)
class DoubleYellowCard(Foul):
    pass
@dataclass(frozen=True)
class MatchEndEvent(MatchEvent):
    pass
@dataclass(frozen=True)
class Substitution(MatchEvent):
    team: str
    subbed_in: str
    subbed_off: str
@dataclass(frozen=True)
class CornerKickEvent(MatchEvent):
    executing_team: str
    taker: str

@dataclass(frozen=True)
class HalfTimeEvent(MatchEvent):
    home_score: int = 0
    away_score: int = 0

@dataclass(frozen=True)
class InjuryEvent(MatchEvent):
    player: str
    team: str
    severity: str = "minor"
    forced_off: bool = False

    @property
    def injuried_player(self) -> str:
        return self.player

@dataclass(frozen=True)
class LongShotGoal(GoalWithAssist):
    pass

@dataclass(frozen=True)
class LongShotEvent(MatchEvent):
    shooter: str
    team: str
    outcome: str

@dataclass(frozen=True)
class WingPlayEvent(MatchEvent):
    winger: str
    team: str
    action_type: str

@dataclass(frozen=True)
class BuildUpEvent(MatchEvent):
    team: str
    passer: str

@dataclass(frozen=True)
class InterceptionEvent(MatchEvent):
    interceptor: str
    team: str


