from __future__ import annotations
from pydantic import BaseModel

class MatchStatusSchema(BaseModel):
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    current_minute: int
    is_finished: bool
    events: list[MatchEventSchema] = []

class MatchEventSchema(BaseModel):
    second: int
    event_type: str
    description: str
    