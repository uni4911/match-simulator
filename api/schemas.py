from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, computed_field
from typing import Optional
from src.models import Team, LeagueTeamStats
from src.engine.engine import Match

class TeamStatsMatchSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    possession_time: float = 0.0
    possession_percentage: float = 50.0
    shots_on_target: int = Field(default=0, ge=0)
    shots_off_target: int = Field(default=0, ge=0)
    total_shots: int = Field(default=0, ge=0)
    fouls: int = Field(default=0, ge=0)
    passes: int = Field(default=0, ge=0)
    goals: int = Field(default=0, ge=0)
    yellow_cards: int = Field(default=0, ge=0)
    red_cards: int = Field(default=0, ge=0)
    corners: int = Field(default=0, ge=0)
    saves: int = Field(default=0, ge=0)

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
    home_team_stats: Optional[TeamStatsMatchSchema] = None
    away_team_stats: Optional[TeamStatsMatchSchema] = None

class MatchPlayerStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    position: str
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    yellow_cards: int = Field(default=0, ge=0, le=2)
    has_red_card: bool
    current_stamina: float = Field(default=1.0, ge=0.0, le=1.0)

class MatchFullStatsSchema(BaseModel):
    home_team_name: str
    away_team_name: str
    home_players: list[MatchPlayerStatsSchema]
    away_players: list[MatchPlayerStatsSchema]
    home_team_stats: Optional[TeamStatsMatchSchema] = None
    away_team_stats: Optional[TeamStatsMatchSchema] = None

class PlayerSeasonStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_name: str
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    position: str
    matches_played: int = Field(default=0, ge=0)
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    yellow_cards: int = Field(default=0, ge=0)
    red_cards: int = Field(default=0, ge=0)
    passes: int = Field(default=0, ge=0)
    clean_sheets: int = Field(default=0, ge=0)

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
    home_team_stats: Optional[TeamStatsMatchSchema] = None
    away_team_stats: Optional[TeamStatsMatchSchema] = None
    events: list[MatchEventSchema] = []
    home_players: list[MatchPlayerStatsSchema] = []
    away_players: list[MatchPlayerStatsSchema] = []

class LeagueTableResponse(BaseModel):
    name: str
    teams: list[str]
    fixtures: list[LeagueMatchSchema]
    table: list[LeagueTeamStatsSchema]
    player_stats: list[PlayerSeasonStatsSchema] = []

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