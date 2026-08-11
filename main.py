import os
import json
import asyncio
import random
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.db.loader import load_all_teams
from src.db.migrate import run_migration
from src.models import AVAILABLE_FORMATIONS, FORMATION_433, League, PlayerSeasonStats, get_formation_positions, Goalkeeper, Player
from src.engine.league_engine import LeagueEngine
from src.events.event_bus import EventBus
from src.engine.engine import MatchTeam, Match, MatchEngine, EVENT_OR_STATE_DURATIONS
from src.events.commentator import Commentator
from api.schemas import (MatchStatusSchema, StartMatchRequest, MatchOptionsResponse, MatchFullStatsSchema, 
                         MatchPlayerStatsSchema, LeagueTableResponse, CreateLeagueRequest, LeagueTeamStats,
                         PlayLeagueMatch, PlayerSeasonStatsSchema, PlayerProfileResponse, PlayerMatchLogSchema,
                         TeamOfTheWeekResponse, TeamOfTheSeasonResponse, TotwPlayerSchema)

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
    home_form = get_formation_positions(getattr(home_team_obj, "formation", "4-3-3"))
    away_form = get_formation_positions(getattr(away_team_obj, "formation", "4-3-3"))
    match_home = MatchTeam(home_team_obj, home_form)
    match_away = MatchTeam(away_team_obj, away_form)
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
        'home_team_stats': match.home_team.stats.to_dict(match.away_team.stats, average_rating=match.home_team.average_rating),
        'away_team_stats': match.away_team.stats.to_dict(match.home_team.stats, average_rating=match.away_team.average_rating),
        'man_of_the_match': match.man_of_the_match
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
        data_json = MatchStatusSchema.model_validate(report).model_dump_json()

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
        data_json = MatchStatusSchema.model_validate(report).model_dump_json()
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

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


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


@app.get("/teams")
def get_teams():
    result = {}
    for team_name, team_obj in loaded_teams.items():
        players_list = []
        for p in team_obj.players:
            actual = getattr(p, "player", p)
            players_list.append({
                "full_name": actual.full_name,
                "short_name": actual.short_name,
                "name": actual.name,
                "position": actual.position.name if hasattr(actual.position, "name") else str(actual.position),
                "nationality": actual.nationality,
                "overall": actual.overall,
                "age": actual.age,
                "height": actual.height
            })
        result[team_name] = players_list
    return result


@app.post("/match/start", response_model=MatchStatusSchema)
def start_match(req: StartMatchRequest):
    global match, event_bus, commentator, engine
    if req.home_team_name not in loaded_teams:
        raise HTTPException(status_code=400, detail=f"Nie znaleziono drużyny: {req.home_team_name}")
    if req.away_team_name not in loaded_teams:
        raise HTTPException(status_code=400, detail=f"Nie znaleziono drużyny: {req.away_team_name}")

    home_team_obj = loaded_teams[req.home_team_name]
    away_team_obj = loaded_teams[req.away_team_name]
    home_form = get_formation_positions(req.home_formation) if req.home_formation in AVAILABLE_FORMATIONS else get_formation_positions(getattr(home_team_obj, "formation", "4-3-3"))
    away_form = get_formation_positions(req.away_formation) if req.away_formation in AVAILABLE_FORMATIONS else get_formation_positions(getattr(away_team_obj, "formation", "4-3-3"))

    home_match_team = MatchTeam(home_team_obj, home_form)
    away_match_team = MatchTeam(away_team_obj, away_form)

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
                   'home_team_stats': match.home_team.stats.to_dict(match.away_team.stats, average_rating=match.home_team.average_rating),
                   'away_team_stats': match.away_team.stats.to_dict(match.home_team.stats, average_rating=match.away_team.average_rating),
                   'man_of_the_match': match.man_of_the_match}
    
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
        raise HTTPException(status_code=400, detail="Brak aktywnego meczu")
    return StreamingResponse(
        match_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

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

        motm = None
        if is_fin and hasattr(m, "home_team") and hasattr(m.home_team, "stats"):
            home_avg = getattr(m.home_team, "average_rating", 6.0)
            away_avg = getattr(m.away_team, "average_rating", 6.0)
            home_t_stats = m.home_team.stats.to_dict(m.away_team.stats, average_rating=home_avg)
            away_t_stats = m.away_team.stats.to_dict(m.home_team.stats, average_rating=away_avg)
            for ev in getattr(m, "match_events", []):
                ev_name = type(ev).__name__
                if ev_name in IMPORTANT_EVENT_NAMES:
                    desc = commentator.get_comment_text(ev) or f"Zdarzenie: {ev_name}"
                    events_list.append({'second': ev.second, 'event_type': ev_name, 'description': desc})
            if hasattr(m.home_team, "match_players"):
                home_players_list = [p for p in m.home_team.match_players]
            if hasattr(m.away_team, "match_players"):
                away_players_list = [p for p in m.away_team.match_players]
            motm = getattr(m, "man_of_the_match", None)

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
            "away_players": away_players_list,
            "man_of_the_match": motm
        })

    # Ensure all players from league teams are tracked in player_stats
    for team_obj in league_obj.teams:
        for player in team_obj.players:
            actual_player = getattr(player, 'player', player)
            if actual_player not in league_obj.player_stats:
                league_obj.player_stats[actual_player] = PlayerSeasonStats(actual_player, team_name=team_obj.name)
            elif not getattr(league_obj.player_stats[actual_player], "team_name", None):
                league_obj.player_stats[actual_player].team_name = team_obj.name

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
    for team_obj in selected_teams:
        for player in team_obj.players:
            player.fitness = 1.0

    league = League(name=req.league_name, teams=selected_teams)
    for team_obj in selected_teams:
        league.table[team_obj] = LeagueTeamStats(team_obj)
    league_engine = LeagueEngine(league, engine)
    league_engine.generate_fixture(req.double_round)

    return _get_league_response(league)


@app.get("/league/table", response_model=Optional[LeagueTableResponse])
def league_table():
    if league is None:
        return None
    return _get_league_response(league)

@app.get("/league/player-stats", response_model=list[PlayerSeasonStatsSchema])
def league_player_stats():
    if league is None:
        return []
    return sorted(list(league.player_stats.values()), key=lambda p: (p.goals, p.assists, p.average_rating), reverse=True)

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

@app.get("/league/team-of-the-week", response_model=TeamOfTheWeekResponse)
def get_league_team_of_the_week(round_number: Optional[int] = None, formation: str = "4-3-3"):
    global league, league_engine
    if league is None or league_engine is None:
        raise HTTPException(400, "Liga nie została utworzona")
    
    num_teams = len(league.teams)
    matches_per_round = max(1, num_teams // 2)

    if round_number is None:
        finished_rounds = [
            (idx // matches_per_round) + 1
            for idx, m in enumerate(league.fixtures)
            if getattr(m, "is_finished", False)
        ]
        round_number = max(finished_rounds) if finished_rounds else 1

    return league_engine.get_team_of_the_round(round_number=round_number, formation=formation)

@app.get("/league/team-of-the-season", response_model=TeamOfTheSeasonResponse)
def get_league_team_of_the_season(formation: str = "4-3-3"):
    global league, league_engine
    if league is None or league_engine is None:
        raise HTTPException(400, "Liga nie została utworzona")

    return league_engine.get_team_of_the_season(formation=formation)

def _find_player_in_all_teams(name: str, team_name: str | None = None) -> tuple[Player | None, str | None]:
    clean_name = name.strip()
    # Strip rank prefix like "1. ", "12. " if present
    if "." in clean_name:
        parts = clean_name.split(".", 1)
        if parts[0].strip().isdigit():
            clean_name = parts[1].strip()

    import unicodedata

    def strip_accents(text: str) -> str:
        return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn").lower()

    clean_norm = strip_accents(clean_name).replace("jr", "junior").replace(".", "").replace("-", " ")
    clean_name_lower = clean_name.lower()
    team_name_lower = team_name.strip().lower() if team_name else None

    # Collect candidates: (priority, player, team_name)
    def check_match(p_obj, t_name: str):
        actual = getattr(p_obj, "player", p_obj)
        fn = actual.full_name or ""
        sn = actual.short_name or ""
        nm = actual.name or ""
        
        # 1. Exact matches
        if fn.lower() == clean_name_lower or sn.lower() == clean_name_lower or nm.lower() == clean_name_lower:
            return 1, actual, t_name
        
        # 2. Normalized exact matches
        fn_norm = strip_accents(fn).replace("jr", "junior").replace(".", "").replace("-", " ")
        sn_norm = strip_accents(sn).replace("jr", "junior").replace(".", "").replace("-", " ")
        if fn_norm == clean_norm or sn_norm == clean_norm:
            return 2, actual, t_name

        # 3. Substring in normalized
        if (clean_norm and clean_norm in fn_norm) or (clean_norm and clean_norm in sn_norm):
            return 3, actual, t_name

        # 4. Partial word matching
        words = [w for w in clean_norm.split() if len(w) > 2]
        if words and all(w in fn_norm or w in sn_norm for w in words):
            return 4, actual, t_name

        return 999, None, None

    # Search in order: match, league, loaded_teams
    best_candidate = None
    best_prio = 999

    sources = []
    if match:
        for mt in [match.home_team, match.away_team]:
            if not team_name_lower or mt.team.name.lower() == team_name_lower:
                sources.append((mt.team.name, [mp.player for mp in mt.match_players]))
    if league:
        for t in league.teams:
            if not team_name_lower or t.name.lower() == team_name_lower:
                sources.append((t.name, t.players))
    for t_name, t_obj in loaded_teams.items():
        if not team_name_lower or t_name.lower() == team_name_lower:
            sources.append((t_name, t_obj.players))

    for t_name, player_list in sources:
        for p in player_list:
            prio, act, team_ret = check_match(p, t_name)
            if prio == 1:
                return act, team_ret
            if prio < best_prio:
                best_prio = prio
                best_candidate = (act, team_ret)

    if best_candidate and best_prio < 999:
        return best_candidate

    return None, None


@app.get("/player/profile", response_model=PlayerProfileResponse)
def get_player_profile(name: str, team: str | None = None):
    player_obj, found_team_name = _find_player_in_all_teams(name, team)
    if not player_obj:
        raise HTTPException(status_code=404, detail=f"Nie znaleziono zawodnika: {name}")

    # Season stats
    season_stats_obj = None
    if league and player_obj in league.player_stats:
        season_stats_obj = league.player_stats[player_obj]
    elif league:
        for p, stats in league.player_stats.items():
            if p.full_name == player_obj.full_name or p.short_name == player_obj.short_name:
                season_stats_obj = stats
                break

    if not season_stats_obj:
        season_stats_obj = PlayerSeasonStats(player_obj, team_name=found_team_name)
        # If single match is active or finished, populate single match stats
        if match:
            for mt in [match.home_team, match.away_team]:
                for mp in mt.match_players:
                    if mp.player == player_obj or mp.name == player_obj.name:
                        if mp.is_starter or mp.minutes_played > 0 or mp in mt.played_players:
                            is_motm = (match.man_of_the_match is not None and (match.man_of_the_match == mp or match.man_of_the_match.player == player_obj))
                            conceded = match.away_score if mt == match.home_team else match.home_score
                            season_stats_obj.register_match_player(mp, team_conceded_zero=(conceded == 0), is_motm=bool(is_motm))

    match_history: list[PlayerMatchLogSchema] = []
    if league and league.fixtures:
        num_teams = len(league.teams)
        matches_per_round = max(1, num_teams // 2)

        for fix_idx, fixture in enumerate(league.fixtures):
            h_name = getattr(fixture.home_team, "team", fixture.home_team).name
            a_name = getattr(fixture.away_team, "team", fixture.away_team).name

            if h_name != found_team_name and a_name != found_team_name:
                continue

            is_home = (h_name == found_team_name)
            opp_name = a_name if is_home else h_name
            r_num = (fix_idx // matches_per_round) + 1
            is_fin = getattr(fixture, "is_finished", False)

            my_score = fixture.home_score if is_home else fixture.away_score
            opp_score = fixture.away_score if is_home else fixture.home_score
            res = "W" if my_score > opp_score else ("D" if my_score == opp_score else "L") if is_fin else "-"

            played = False
            is_starter = False
            is_on_field = False
            was_sub_in = False
            was_sub_off = False
            m_played = 0
            rating = 6.0
            goals = 0
            assists = 0
            passes = 0
            yellow_cards = 0
            has_red = False
            is_injured = False
            is_motm = False

            if is_fin:
                match_team = fixture.home_team if is_home else fixture.away_team
                if hasattr(match_team, "match_players"):
                    for mp in match_team.match_players:
                        if mp.player == player_obj or mp.name == player_obj.name or mp.full_name == player_obj.full_name:
                            is_starter = mp.is_starter
                            is_on_field = mp.is_on_field
                            m_played = getattr(mp, "minutes_played", 0)
                            rating = getattr(mp, "rating", 6.0)
                            goals = mp.goals
                            assists = mp.assists
                            passes = mp.passes
                            yellow_cards = mp.yellow_cards
                            has_red = mp.has_red_card
                            is_injured = mp.is_injured
                            played = (is_starter or m_played > 0 or mp in getattr(match_team, "played_players", set()))
                            was_sub_in = (not is_starter and played)
                            was_sub_off = (is_starter and not is_on_field and not has_red and not getattr(mp, "is_forced_off", False))
                            motm = getattr(fixture, "man_of_the_match", None)
                            if motm and (motm == mp or motm.player == player_obj):
                                is_motm = True
                            break

            match_history.append(PlayerMatchLogSchema(
                round_number=r_num,
                home_team_name=h_name,
                away_team_name=a_name,
                home_score=fixture.home_score,
                away_score=fixture.away_score,
                is_home=is_home,
                opponent_name=opp_name,
                result=res,
                is_finished=is_fin,
                played_in_match=played,
                is_starter=is_starter,
                is_on_field=is_on_field,
                was_subbed_in=was_sub_in,
                was_subbed_off=was_sub_off,
                minutes_played=m_played,
                rating=rating,
                goals=goals,
                assists=assists,
                passes=passes,
                yellow_cards=yellow_cards,
                has_red_card=has_red,
                is_injured=is_injured,
                is_motm=is_motm,
                fixture_index=fix_idx
            ))

    elif match:
        h_name = match.home_team.team.name
        a_name = match.away_team.team.name
        if h_name == found_team_name or a_name == found_team_name:
            is_home = (h_name == found_team_name)
            opp_name = a_name if is_home else h_name
            is_fin = match.current_second >= 5400
            my_score = match.home_score if is_home else match.away_score
            opp_score = match.away_score if is_home else match.home_score
            res = "W" if my_score > opp_score else ("D" if my_score == opp_score else "L") if is_fin else "-"

            match_team = match.home_team if is_home else match.away_team
            for mp in match_team.match_players:
                if mp.player == player_obj or mp.name == player_obj.name or mp.full_name == player_obj.full_name:
                    is_motm = (match.man_of_the_match and (match.man_of_the_match == mp or match.man_of_the_match.player == player_obj))
                    played = (mp.is_starter or mp.minutes_played > 0 or mp in match_team.played_players)
                    match_history.append(PlayerMatchLogSchema(
                        round_number=1,
                        home_team_name=h_name,
                        away_team_name=a_name,
                        home_score=match.home_score,
                        away_score=match.away_score,
                        is_home=is_home,
                        opponent_name=opp_name,
                        result=res,
                        is_finished=is_fin,
                        played_in_match=played,
                        is_starter=mp.is_starter,
                        is_on_field=mp.is_on_field,
                        was_subbed_in=(not mp.is_starter and played),
                        was_subbed_off=(mp.is_starter and not mp.is_on_field),
                        minutes_played=mp.minutes_played,
                        rating=mp.rating,
                        goals=mp.goals,
                        assists=mp.assists,
                        passes=mp.passes,
                        yellow_cards=mp.yellow_cards,
                        has_red_card=mp.has_red_card,
                        is_injured=mp.is_injured,
                        is_motm=bool(is_motm),
                        fixture_index=None
                    ))
                    break

    is_gk = isinstance(player_obj, Goalkeeper)
    return PlayerProfileResponse(
        player_name=player_obj.name,
        full_name=player_obj.full_name,
        short_name=player_obj.short_name,
        team_name=found_team_name or "Brak drużyny",
        position=player_obj.position.name if hasattr(player_obj.position, "name") else str(player_obj.position),
        age=getattr(player_obj, "age", 20),
        nationality=getattr(player_obj, "nationality", "Unknown"),
        height=getattr(player_obj, "height", 180),
        overall=getattr(player_obj, "overall", 50),
        fitness=getattr(player_obj, "fitness", 1.0),
        form=getattr(player_obj, "form", 1.0),
        is_goalkeeper=is_gk,
        attributes=season_stats_obj.attributes,
        season_stats=season_stats_obj,
        match_history=match_history
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
