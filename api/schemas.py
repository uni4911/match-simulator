from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
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

class MatchPlayerStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    position: str
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default= 0, ge=0)
    yellow_cards: int = Field(default=0,ge=0, le=2)
    has_red_card: bool
    current_stamina: float = Field(default=1.0, ge=0.0, le=1.0)

class MatchFullStatsSchema(BaseModel):
    home_team_name: str
    away_team_name: str
    home_players: list[MatchPlayerStatsSchema]
    away_players: list[MatchPlayerStatsSchema]


class StartMatchRequest(BaseModel):
    home_team_name: str
    away_team_name: str
    home_formation: Optional[str] = "4-3-3"
    away_formation: Optional[str] = "4-3-3"

class MatchOptionsResponse(BaseModel):
    teams: list[str]
    formations: list[str]



    