import os
import json
import asyncio
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.db.loader import load_all_teams
from src.db.migrate import run_migration
from src.models import AVAILABLE_FORMATIONS, FORMATION_433, League, PlayerSeasonStats
from src.engine.league_engine import LeagueEngine
from src.events.event_bus import EventBus
from src.engine.engine import MatchTeam, Match, MatchEngine, EVENT_OR_STATE_DURATIONS
from src.events.commentator import Commentator
from api.schemas import (MatchStatusSchema, StartMatchRequest, MatchOptionsResponse, MatchFullStatsSchema, 
                         MatchPlayerStatsSchema, LeagueTableResponse, CreateLeagueRequest, LeagueTeamStats,
                         PlayLeagueMatch, PlayerSeasonStatsSchema)

try:
    run_migration()
except Exception as e:
    print(f"Błąd podczas migracji bazy danych: {e}")

json_filename = "data.json"
try:
    loaded_teams = load_all_teams(json_filename)
except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku '{json_filename}' w katalogu 'data/'.")
    loaded_teams = {}
except Exception as e:
    print(f"Błąd podczas ładowania drużyn: {e}")
    loaded_teams = {}

team_names = list(loaded_teams.keys())
if len(team_names) >= 2:
    home_team_obj = loaded_teams[team_names[0]]
    away_team_obj = loaded_teams[team_names[1]]
elif len(team_names) == 1:
    home_team_obj = loaded_teams[team_names[0]]
    away_team_obj = loaded_teams[team_names[0]]
else:
    home_team_obj = None
    away_team_obj = None

event_bus = EventBus()
commentator = Commentator(event_bus=event_bus)

if home_team_obj and away_team_obj:
    match_home = MatchTeam(home_team_obj, FORMATION_433)
    match_away = MatchTeam(away_team_obj, FORMATION_433)
    match = Match(match_home, match_away, event_bus=event_bus)
else:
    match = None

engine = MatchEngine(commentator=commentator, speed_factor=0.1, event_bus=event_bus)
league: League | None = None
league_engine: LeagueEngine | None = None

IMPORTANT_EVENT_NAMES = {
    'Goal', 'GoalWithAssist', 'PenaltyKickGoal', 'LongShotGoal',
    'ShotSave', 'LongShotEvent',
    'Foul', 'YellowCardFoul', 'RedCardFoul', 'DoubleYellowCard',
    'Substitution', 'InjuryEvent', 'CornerKickEvent',
    'KickoffEvent', 'HalfTimeEvent', 'MatchEndEvent'
}

def get_match_status_report():
    if not match:
        return {
            'home_team_name': 'Brak drużyny',
            'away_team_name': 'Brak drużyny',
            'home_score': 0,
            'away_score': 0,
            'current_minute': 0,
            'is_finished': True,
            'events': []
        }

    api_events = []
    print(f"DEBUG SCORE: Home={match.home_score}, Away={match.away_score}")

    for event in match.match_events:
        event_name = type(event).__name__
        if event_name not in IMPORTANT_EVENT_NAMES:
            continue
        description = commentator.get_comment_text(event) or f"Zdarzenie: {event_name}"

        event_dict = {'second': event.second, 'event_type': event_name, 'description': description}
        api_events.append(event_dict)

    return {
        'home_team_name': match.home_team.team.name,
        'away_team_name': match.away_team.team.name,
        'home_score': match.home_score,
        'away_score': match.away_score,
        'current_minute': match.current_second // 60,
        'is_finished': match.current_second >= 5400,
        'events': api_events,
        'home_team_stats': match.home_team.stats.to_dict(match.away_team.stats),
        'away_team_stats': match.away_team.stats.to_dict(match.home_team.stats)
    }


async def match_event_generator():
    global match, league
    while match and match.current_second < 5400:
        prev_event_count = len(match.match_events)
        match.current_state = match.current_state.execute(match)
        if len(match.match_events) > prev_event_count:
            key = type(match.match_events[-1])
        else:
            key = type(match.current_state)
        time_range = EVENT_OR_STATE_DURATIONS.get(key, (3, 8))
        time_passed = random.randint(*time_range)
        match.advance_time(time_passed)
        report = get_match_status_report()
        data_json = json.dumps(report)

        yield f"data: {data_json}\n\n"

        await asyncio.sleep(0.1)

    if match and match.current_second >= 5400:
        if league and hasattr(match, "league_index") and not getattr(match, "is_finished", False):
            setattr(match, "is_finished", True)
            home_team = match.home_team
            away_team = match.away_team
            home_stats = league.table.get(home_team.team)
            away_stats = league.table.get(away_team.team)
            if home_stats and away_stats:
                home_stats.register_match_result(match.home_score, match.away_score)
                away_stats.register_match_result(match.away_score, match.home_score)
            league.register_match_player_stats(match)

        report = get_match_status_report()
        data_json = json.dumps(report)
        yield f"data: {data_json}\n\n"

async def get_players_stats():
    global match

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/match/options", response_model=MatchOptionsResponse)
def match_options():
    teams_list = []
    teams_detailed = []
    leagues_set = set()

    for team_name, team_obj in loaded_teams.items():
        teams_list.append(team_name)
        lg = getattr(team_obj, "league", "Inne") or "Inne"
        teams_detailed.append({"name": team_name, "league": lg})
        leagues_set.add(lg)

    return {
        "teams": teams_list,
        "teams_detailed": teams_detailed,
        "leagues": sorted(list(leagues_set)),
        "formations": list(AVAILABLE_FORMATIONS.keys())
    }

@app.post("/match/start", response_model=MatchStatusSchema)
def start_match(req: StartMatchRequest):
    global match, event_bus, commentator, engine
    if req.home_team_name not in loaded_teams:
        raise HTTPException(status_code=400, detail=f"Nie znaleziono drużyny: {req.home_team_name}")
    if req.away_team_name not in loaded_teams:
        raise HTTPException(status_code=400, detail=f"Nie znaleziono drużyny: {req.away_team_name}")

    home_form = AVAILABLE_FORMATIONS.get(req.home_formation, FORMATION_433)
    away_form = AVAILABLE_FORMATIONS.get(req.away_formation, FORMATION_433)

    home_match_team = MatchTeam(loaded_teams[req.home_team_name], home_form)
    away_match_team = MatchTeam(loaded_teams[req.away_team_name], away_form)

    event_bus = EventBus()
    commentator = Commentator(event_bus=event_bus)
    match = Match(home_match_team, away_match_team, event_bus=event_bus)
    engine = MatchEngine(commentator=commentator, speed_factor=0.1, event_bus=event_bus)

    return get_match_status_report()

@app.get("/match/status", response_model=MatchStatusSchema)
def match_status():
    return get_match_status_report()

@app.get("/match/stats",response_model=MatchFullStatsSchema)
def team_stats():
    global match
    if match is None:
        raise HTTPException(status_code=404, detail="Match not started")
    teams_stats = {'home_team_name': match.home_team.team.name,
                   'away_team_name': match.away_team.team.name,
                   'home_players': match.home_team.match_players,
                   'away_players': match.away_team.match_players,
                   'home_team_stats': match.home_team.stats.to_dict(match.away_team.stats),
                   'away_team_stats': match.away_team.stats.to_dict(match.home_team.stats)}
    
    return teams_stats


@app.post("/match/tick", response_model=MatchStatusSchema)
def match_tick():
    global match
    if not match:
        raise HTTPException(status_code=400, detail="Brak aktywnego meczu")
    match.current_state = match.current_state.execute(match)
    match.advance_time(15)
    return get_match_status_report()

@app.get("/")
def read_root():
    return FileResponse("static/index.html")


@app.get("/match/stream")
async def stream_match():
    if not match:
        raise HTTPException(status_code=400,detail="Brak aktywnego meczu")
    return StreamingResponse(match_event_generator(),media_type="text/event-stream")

def _get_league_response(league_obj):
    num_teams = len(league_obj.teams)
    matches_per_round = max(1, num_teams // 2)

    fixtures_data = []
    for idx, m in enumerate(league_obj.fixtures):
        r_num = (idx // matches_per_round) + 1
        is_fin = getattr(m, "is_finished", False)
        
        home_t_stats = None
        away_t_stats = None
        events_list = []
        home_players_list = []
        away_players_list = []

        if is_fin and hasattr(m, "home_team") and hasattr(m.home_team, "stats"):
            home_t_stats = m.home_team.stats.to_dict(m.away_team.stats)
            away_t_stats = m.away_team.stats.to_dict(m.home_team.stats)
            for ev in getattr(m, "match_events", []):
                ev_name = type(ev).__name__
                if ev_name in IMPORTANT_EVENT_NAMES:
                    desc = commentator.get_comment_text(ev) or f"Zdarzenie: {ev_name}"
                    events_list.append({'second': ev.second, 'event_type': ev_name, 'description': desc})
            if hasattr(m.home_team, "match_players"):
                home_players_list = [p for p in m.home_team.match_players]
            if hasattr(m.away_team, "match_players"):
                away_players_list = [p for p in m.away_team.match_players]

        fixtures_data.append({
            "home_team_name": getattr(m.home_team, "team", m.home_team).name,
            "away_team_name": getattr(m.away_team, "team", m.away_team).name,
            "home_score": m.home_score,
            "away_score": m.away_score,
            "is_finished": is_fin,
            "round_number": r_num,
            "home_team_stats": home_t_stats,
            "away_team_stats": away_t_stats,
            "events": events_list,
            "home_players": home_players_list,
            "away_players": away_players_list
        })

    # Ensure all players from league teams are tracked in player_stats
    for team_obj in league_obj.teams:
        for player in team_obj.players:
            if player not in league_obj.player_stats:
                league_obj.player_stats[player] = PlayerSeasonStats(player)

    player_stats_sorted = sorted(league_obj.player_stats.values(), key=lambda s: s.goals, reverse=True)
    return {
        "name": league_obj.name,
        "teams": [t.name for t in league_obj.teams],
        "fixtures": fixtures_data,
        "table": list(league_obj.table.values()),
        "player_stats": player_stats_sorted
    }

@app.post("/league/start", response_model=LeagueTableResponse)
def league_start(req: CreateLeagueRequest):
    global league, league_engine

    if len(req.league_teams) > 64:
        raise HTTPException(400, detail="Maksymalna liczba drużyn w jednej lidze to 64. Wybierz mniejszą liczbę drużyn.")

    for team in req.league_teams:
        if team not in loaded_teams:
            raise HTTPException(400, f"Nie znaleziono drużyny {team}")

    selected_teams = [loaded_teams[name] for name in req.league_teams]

    league = League(name=req.league_name, teams=selected_teams)
    for team_obj in selected_teams:
        league.table[team_obj] = LeagueTeamStats(team_obj)
    league_engine = LeagueEngine(league, engine)
    league_engine.generate_fixture(req.double_round)

    return _get_league_response(league)


@app.get("/league/table", response_model=LeagueTableResponse)
def league_table():
    if league is None:
        raise HTTPException(400, "Liga nie została jeszcze utworzona")
    
    return _get_league_response(league)

@app.post("/league/match/status", response_model=LeagueTableResponse)
def play_league_match(req: PlayLeagueMatch):
    if league is None or league_engine is None:
        raise HTTPException(400, "Liga nie została utworzona")
    if req.match_index < 0 or req.match_index >= len(league.fixtures):
        raise HTTPException(400, detail="Nieprawidłowy indeks meczu")

    selected_match = league.fixtures[req.match_index]
    if not getattr(selected_match, "is_finished", False):
        league_engine.play_match(selected_match)
        setattr(selected_match, "is_finished", True)

    return _get_league_response(league)

@app.get("/league/player-stats", response_model=list[PlayerSeasonStatsSchema])
def get_league_player_stats(sort_by: str = "goals"):
    if league is None:
        raise HTTPException(400, "Liga nie została utworzona")
    if league_engine is None:
        return list(league.player_stats.values())
    return league_engine.get_sorted_player_stats(sort_by=sort_by)

@app.post("/league/match/live_start", response_model=MatchStatusSchema)
def start_league_match_live(req: PlayLeagueMatch):
    global match, event_bus, commentator, engine, league
    if league is None or league_engine is None:
        raise HTTPException(400, "Liga nie została utworzona")
    if req.match_index < 0 or req.match_index >= len(league.fixtures):
        raise HTTPException(400, detail="Nieprawidłowy indeks meczu")

    selected_match = league.fixtures[req.match_index]
    if getattr(selected_match, "is_finished", False):
        raise HTTPException(400, detail="Mecz został już rozegrany")

    event_bus = EventBus()
    commentator = Commentator(event_bus=event_bus)
    selected_match.event_bus = event_bus
    selected_match.league_index = req.match_index

    match = selected_match
    engine = MatchEngine(commentator=commentator, speed_factor=0.1, event_bus=event_bus)

    return get_match_status_report()

app.mount("/static", StaticFiles(directory="static"), name="static")
