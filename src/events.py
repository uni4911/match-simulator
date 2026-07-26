from dataclasses import dataclass

@dataclass(frozen=True)
class MatchEvent:
    second: int

@dataclass(frozen=True)
class KickoffEvent(MatchEvent):
    executing_team: str

@dataclass(frozen=True)
class Goal(MatchEvent):
    goalscorer: str
    team: str

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