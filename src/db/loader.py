from __future__ import annotations
import json
import os
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, joinedload
from src.models import Position, Goalkeeper, FieldPlayer, Team, Player
from src.db.database import SessionLocal, TeamModel, PlayerModel, Base, engine
from src.db.mappers import TeamMapper, PlayerMapper


from src.repositories import SqlAlchemyTeamRepository


def load_file(file_name: str, team_name: str) -> list[FieldPlayer | Goalkeeper]:
    file_path = file_name if os.path.isabs(file_name) or os.path.exists(file_name) else os.path.join("data", file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            player_data = json.load(file)
            team_players = []
            for player in player_data[team_name]:
                position_text = player["position"]
                player["position"] = Position[position_text]
                if "name" in player:
                    name_val = player.pop("name")
                    player.setdefault("full_name", name_val)
                    player.setdefault("short_name", name_val)
                if player["position"] is Position.GOALKEEPER:
                    del player["position"]
                    temp_player = Goalkeeper(**player)
                else:
                    temp_player = FieldPlayer(**player)
                team_players.append(temp_player)
            return team_players
    except FileNotFoundError:
        print(f"{file_name} doesn't exist")
        raise


def get_team_names(file_name: str = "data.json") -> list[str]:
    file_path = file_name if os.path.isabs(file_name) or os.path.exists(file_name) else os.path.join("data", file_name)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return list(data.keys())

  
    with SessionLocal() as session:
        stmt = select(TeamModel.name)
        return list(session.scalars(stmt).all())


def load_team(team_name: str, file_name: str = "data.json") -> Team:
   
    team_from_db = load_team_from_db(team_name)
    if team_from_db is not None:
        return team_from_db

    players = load_file(file_name, team_name)
    league_name = "Inne"
    formation_name = "4-3-3"
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    teams_json_path = os.path.join(base_dir, "data", "teams.json")
    if os.path.exists(teams_json_path):
        try:
            with open(teams_json_path, "r", encoding="utf-8") as f:
                teams_info = json.load(f)
                for t in teams_info:
                    if t.get("name") == team_name:
                        league_name = t.get("league", "Inne")
                        formation_name = t.get("formation", "4-3-3")
                        break
        except Exception:
            pass

    return Team(team_name, players, league=league_name, formation=formation_name)


def load_all_teams(file_name: str = "data.json") -> dict[str, Team]:

    teams_from_db = load_all_teams_from_db()
    if teams_from_db:
        return teams_from_db

    names = get_team_names(file_name)
    teams = {}
    for name in names:
        teams[name] = load_team(name, file_name)
    return teams


def load_team_from_db(team_name: str, session: Optional[Session] = None) -> Optional[Team]:
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        repo = SqlAlchemyTeamRepository(session)
        return repo.get_team_by_name(team_name)
    finally:
        if close_session:
            session.close()


def load_all_teams_from_db(session: Optional[Session] = None) -> dict[str, Team]:
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        repo = SqlAlchemyTeamRepository(session)
        team_list = repo.get_all()
        return {team.name: team for team in team_list}
    finally:
        if close_session:
            session.close()


def save_team_to_db(team: Team, session: Optional[Session] = None) -> TeamModel:
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        repo = SqlAlchemyTeamRepository(session)
        return repo.save(team)
    finally:
        if close_session:
            session.close()


