from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class MatchEventSchema(BaseModel):
    second: int
    event_type: str
    description: str

class MatchStatusSchema(BaseModel):
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    current_minute: int
    is_finished: bool
    events: list[MatchEventSchema] = []

class StartMatchRequest(BaseModel):
    home_team_name: str
    away_team_name: str
    home_formation: Optional[str] = "4-3-3"
    away_formation: Optional[str] = "4-3-3"

class MatchOptionsResponse(BaseModel):
    teams: list[str]
    formations: list[str]

    