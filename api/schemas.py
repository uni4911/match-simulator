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
    average_rating: float = Field(default=6.0, ge=1.0, le=10.0)

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
    man_of_the_match: Optional[MatchPlayerStatsSchema] = None

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
    is_starter: bool = False
    is_on_field: bool = False
    is_injured: bool = False
    rating: float = Field(default=6.0, ge=1.0, le=10.0)
    minutes_played: int = Field(default=0, ge=0)
    age: int = Field(default=20, ge=15, le=50)
    nationality: str = "Unknown"
    height: int = Field(default=180, ge=140, le=220)
    overall: int = Field(default=50, ge=1, le=99)
    team_name: Optional[str] = None

class MatchFullStatsSchema(BaseModel):
    home_team_name: str
    away_team_name: str
    home_players: list[MatchPlayerStatsSchema]
    away_players: list[MatchPlayerStatsSchema]
    home_team_stats: Optional[TeamStatsMatchSchema] = None
    away_team_stats: Optional[TeamStatsMatchSchema] = None
    man_of_the_match: Optional[MatchPlayerStatsSchema] = None

class PlayerSeasonStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_name: str
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    team_name: Optional[str] = None
    position: str
    matches_played: int = Field(default=0, ge=0)
    minutes_played: int = Field(default=0, ge=0)
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    yellow_cards: int = Field(default=0, ge=0)
    red_cards: int = Field(default=0, ge=0)
    passes: int = Field(default=0, ge=0)
    clean_sheets: int = Field(default=0, ge=0)
    average_rating: float = Field(default=0.0, ge=0.0, le=10.0)
    motm_awards: int = Field(default=0, ge=0)
    age: int = Field(default=20, ge=15, le=50)
    nationality: str = "Unknown"
    height: int = Field(default=180, ge=140, le=220)
    overall: int = Field(default=50, ge=1, le=99)
    fitness: float = Field(default=1.0, ge=0.0, le=1.0)
    form: float = Field(default=1.0, ge=0.0, le=2.0)
    attributes: dict[str, int] = Field(default_factory=dict)

class PlayerMatchLogSchema(BaseModel):
    round_number: int = 1
    home_team_name: str
    away_team_name: str
    home_score: int = 0
    away_score: int = 0
    is_home: bool = True
    opponent_name: str
    result: str = "-"
    is_finished: bool = False
    played_in_match: bool = False
    is_starter: bool = False
    is_on_field: bool = False
    was_subbed_in: bool = False
    was_subbed_off: bool = False
    minutes_played: int = 0
    rating: float = 6.0
    goals: int = 0
    assists: int = 0
    passes: int = 0
    yellow_cards: int = 0
    has_red_card: bool = False
    is_injured: bool = False
    is_motm: bool = False
    fixture_index: Optional[int] = None

class PlayerProfileResponse(BaseModel):
    player_name: str
    full_name: str
    short_name: str
    team_name: str
    position: str
    age: int
    nationality: str
    height: int
    overall: int
    fitness: float
    form: float
    is_goalkeeper: bool
    attributes: dict[str, int] = Field(default_factory=dict)
    season_stats: PlayerSeasonStatsSchema
    match_history: list[PlayerMatchLogSchema] = []

class LeagueTeamStatsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    team_name: str
    goals_scored: int 
    goals_conceded: int 
    matches_played: int 
    wins: int 
    draws: int 
    loses: int
    recent_results: list[str] = Field(default_factory=list)

    @computed_field
    def points(self) -> int:
        return self.wins * 3 + self.draws * 1
    
    @computed_field
    def goal_difference(self) -> int:
        return self.goals_scored - self.goals_conceded

    @computed_field
    def form(self) -> list[str]:
        return self.recent_results

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
    man_of_the_match: Optional[MatchPlayerStatsSchema] = None

class LeagueTableResponse(BaseModel):
    name: str
    teams: list[str]
    fixtures: list[LeagueMatchSchema]
    table: list[LeagueTeamStatsSchema]
    player_stats: list[PlayerSeasonStatsSchema] = []

class CreateLeagueRequest(BaseModel):
    league_name: str = "Moja liga"
    league_teams: list[str] = Field(min_length=2, max_length=64)
    double_round: bool = False
       
class StartMatchRequest(BaseModel):
    home_team_name: str
    away_team_name: str
    home_formation: str = "4-3-3"
    away_formation: str = "4-3-3"

class PlayLeagueMatch(BaseModel):
    match_index: int

class TeamDetailSchema(BaseModel):
    name: str
    league: str = "Inne"

class MatchOptionsResponse(BaseModel):
    teams: list[str]
    teams_detailed: list[TeamDetailSchema] = []
    leagues: list[str] = []
    formations: list[str]

class TotwPlayerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    player_name: str
    full_name: Optional[str] = None
    short_name: Optional[str] = None
    team_name: str
    position: str
    slot_position: str
    slot_id: str = "SLOT"
    slot_name: str = "Pozycja"
    grid_row: int = 0
    grid_col: int = 0
    category: str = "MID"
    rating: float = Field(default=6.0, ge=1.0, le=10.0)
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    passes: int = Field(default=0, ge=0)
    yellow_cards: int = Field(default=0, ge=0)
    has_red_card: bool = False
    clean_sheet: bool = False
    clean_sheets: int = Field(default=0, ge=0)
    is_motm: bool = False
    overall: int = Field(default=50, ge=1, le=99)
    age: int = Field(default=20, ge=15, le=50)
    nationality: str = "Unknown"
    minutes_played: int = Field(default=0, ge=0)
    matches_played: int = Field(default=1, ge=0)
    is_bench: bool = False
    is_mvp: bool = False

class TeamOfTheWeekResponse(BaseModel):
    round_number: int
    total_rounds: int
    formation: str = "4-3-3"
    available_formations: list[str] = []
    is_round_finished: bool = False
    matches_played_in_round: int = 0
    total_matches_in_round: int = 0
    starting_xi: list[TotwPlayerSchema] = []
    bench: list[TotwPlayerSchema] = []
    mvp: Optional[TotwPlayerSchema] = None
    top_scorer: Optional[TotwPlayerSchema] = None
    top_assister: Optional[TotwPlayerSchema] = None
    top_goalkeeper: Optional[TotwPlayerSchema] = None
    best_team_name: Optional[str] = None
    average_rating: float = 0.0

class TeamOfTheSeasonResponse(BaseModel):
    league_name: str
    total_rounds: int
    rounds_played: int
    formation: str = "4-3-3"
    available_formations: list[str] = []
    is_season_finished: bool = False
    starting_xi: list[TotwPlayerSchema] = []
    bench: list[TotwPlayerSchema] = []
    mvp: Optional[TotwPlayerSchema] = None
    top_scorer: Optional[TotwPlayerSchema] = None
    top_assister: Optional[TotwPlayerSchema] = None
    top_goalkeeper: Optional[TotwPlayerSchema] = None
    best_team_name: Optional[str] = None
    average_rating: float = 0.0