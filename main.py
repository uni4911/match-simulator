import os
from src.loader import load_file
from src.models import Team, FORMATION_433
from src.event_bus import EventBus
from src.engine import MatchTeam, Match, MatchEngine
from src.commentator import Commentator
from fastapi import FastAPI
from pydantic import BaseModel
from api.schemas import MatchStatusSchema
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware



json_filename = "data.json"
try:
    html_players = load_file(json_filename, "Amatorzy HTML")
    java_players = load_file(json_filename, "CF Java")
    python_players = load_file(json_filename, "Python FC")
    rust_players = load_file(json_filename, "Galacticos Rust")
except FileNotFoundError:
    print(f"Błąd: Nie znaleziono pliku '{json_filename}' w katalogu 'data/'.")
except KeyError as e:
    print(f"Błąd: Nie znaleziono drużyny w pliku JSON: {e}")
 

team_html = Team("Amatorzy HTML", html_players)
team_java = Team("CF Java", java_players)
team_python = Team("Python FC", python_players)
team_rust = Team("Galacticos Rust", rust_players)

home_team_obj = team_java
away_team_obj = team_python

match_home = MatchTeam(home_team_obj, FORMATION_433)
match_away = MatchTeam(away_team_obj, FORMATION_433)

event_bus = EventBus()
commentator = Commentator(event_bus=event_bus)
match = Match(match_home, match_away, event_bus=event_bus)
engine = MatchEngine(commentator=commentator, speed_factor=0.1, event_bus=event_bus)

def get_match_status_report():
    api_events = []

    print(f"DEBUG SCORE: Home={match.home_score}, Away={match.away_score}")

    for event in match.match_events:
        event_name = type(event).__name__
        description = commentator.get_comment_text(event) or f"Zdarzenie: {event_name}"

        event_dict = {'second':event.second,'event_type':event_name,'description':description}
        api_events.append(event_dict)

    return {'home_team_name':match.home_team.team.name,
            'away_team_name':match.away_team.team.name,
            'home_score':match.home_score,
            'away_score':match.away_score,
            'current_minute':match.current_second // 60,
            'is_finished':match.current_second>=5400,
            'events': api_events}

app = FastAPI()
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods = ["*"],
    allow_headers= ["*"]
)

@app.get("/match/status",response_model=MatchStatusSchema)
def match_status():
    return get_match_status_report()

@app.post("/match/tick",response_model=MatchStatusSchema)
def match_tick():
    match.current_state = match.current_state.execute(match)
    match.current_second +=15
    return get_match_status_report()

app.mount("/static",StaticFiles(directory="static"),name="static")



