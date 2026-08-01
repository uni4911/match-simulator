import os
import json
import asyncio
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.loader import load_all_teams
from src.models import AVAILABLE_FORMATIONS, FORMATION_433
from src.event_bus import EventBus
from src.engine import MatchTeam, Match, MatchEngine, EVENT_OR_STATE_DURATIONS
from src.commentator import Commentator
from api.schemas import MatchStatusSchema, StartMatchRequest, MatchOptionsResponse


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
        'events': api_events
    }

async def match_event_generator():
    global match
    while match and match.current_second < 5400 :
        prev_event_count = len(match.match_events)
        match.current_state = match.current_state.execute(match)
        if len(match.match_events) > prev_event_count:
            key = type(match.match_events[-1])
        else:
            key = type(match.current_state)
        time_range = EVENT_OR_STATE_DURATIONS.get(key,(3,8))
        time_passed = random.randint(*time_range)
        match.current_second += time_passed
        report = get_match_status_report()
        data_json = json.dumps(report)

        yield f"data: {data_json}\n\n"

        await asyncio.sleep(0.1)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/match/options", response_model=MatchOptionsResponse)
def match_options():
    return {
        "teams": list(loaded_teams.keys()),
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

@app.post("/match/tick", response_model=MatchStatusSchema)
def match_tick():
    global match
    if not match:
        raise HTTPException(status_code=400, detail="Brak aktywnego meczu")
    match.current_state = match.current_state.execute(match)
    match.current_second += 15
    return get_match_status_report()

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.get("/match/stream")
async def stream_match():
    if not match:
        raise HTTPException(status_code=400,detail="Brak aktywnego meczu")
    return StreamingResponse(match_event_generator(),media_type="text/event-stream")


app.mount("/static", StaticFiles(directory="static"), name="static")





