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


