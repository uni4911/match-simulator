from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional
from src.models import Team, LeagueTeamStats
from src.engine import Match

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

class PlayerSeasonStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_name: str
    position: str
    matches_played: int = Field(default=0, ge=0)
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    yellow_cards: int = Field(default=0, ge=0)
    red_cards: int = Field(default=0, ge=0)
    passes: int = Field(default=0, ge=0)
    clean_sheets: int = Field(default=0, ge=0)

class LeagueTableResponse(BaseModel):
    name: str
    teams: list[str]
    fixtures: list[LeagueMatchSchema]
    table: list[LeagueTeamStatsSchema]
    player_stats: list[PlayerSeasonStatsSchema] = []


class LeagueTeamStatsSchema(BaseModel):
        model_config = ConfigDict(from_attributes=True)
        team_name: str
        goals_scored: int 
        goals_conceded: int 
        matches_played: int 
        wins: int 
        draws: int 
        loses: int

        @computed_field
        def points(self) -> int:
            return self.wins * 3 + self.draws * 1
        
        @computed_field
        def goal_difference(self) -> int:
            return self.goals_scored - self.goals_conceded

class LeagueMatchSchema(BaseModel):
    home_team_name: str
    away_team_name: str
    home_score: int
    away_score: int
    is_finished: bool
    round_number: int = 1

class CreateLeagueRequest(BaseModel):
    league_name: str = "Moja liga"
    league_teams: list[str] = Field(min_length=2)
    double_round: bool = False
       
class StartMatchRequest(BaseModel):
    home_team_name: str
    away_team_name: str
    home_formation: str = "4-3-3"
    away_formation: str = "4-3-3"

class PlayLeagueMatch(BaseModel):
    match_index: int

class MatchOptionsResponse(BaseModel):
    teams: list[str]
    formations: list[str]




    