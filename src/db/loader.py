from __future__ import annotations
import json
import os
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from src.models import Position, Goalkeeper, FieldPlayer, Team, Player
from src.db.database import SessionLocal, TeamModel, PlayerModel, Base, engine


def load_file(file_name: str, team_name: str) -> list[FieldPlayer | Goalkeeper]:
    file_path = file_name if os.path.isabs(file_name) or os.path.exists(file_name) else os.path.join("data", file_name)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            player_data = json.load(file)
            team_players = []
            for player in player_data[team_name]:
                position_text = player["position"]
                player["position"] = Position[position_text]
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

    # Fallback to DB if file doesn't exist
    with SessionLocal() as session:
        stmt = select(TeamModel.name)
        return list(session.scalars(stmt).all())


def load_team(team_name: str, file_name: str = "data.json") -> Team:
    # Try DB first if available, else load from file
    team_from_db = load_team_from_db(team_name)
    if team_from_db is not None:
        return team_from_db

    players = load_file(file_name, team_name)
    return Team(team_name, players)


def load_all_teams(file_name: str = "data.json") -> dict[str, Team]:
    # Try DB first if populated
    teams_from_db = load_all_teams_from_db()
    if teams_from_db:
        return teams_from_db

    names = get_team_names(file_name)
    teams = {}
    for name in names:
        teams[name] = load_team(name, file_name)
    return teams


# Database persistence functions
def load_team_from_db(team_name: str, session: Optional[Session] = None) -> Optional[Team]:
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        stmt = select(TeamModel).options(selectinload(TeamModel.players)).where(TeamModel.name == team_name)
        team_model = session.execute(stmt).scalar_one_or_none()
        if team_model is None:
            return None
        return team_model.to_domain()
    finally:
        if close_session:
            session.close()


def load_all_teams_from_db(session: Optional[Session] = None) -> dict[str, Team]:
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        stmt = select(TeamModel).options(selectinload(TeamModel.players))
        team_models = session.execute(stmt).scalars().all()
        teams = {}
        for tm in team_models:
            teams[tm.name] = tm.to_domain()
        return teams
    finally:
        if close_session:
            session.close()


def save_team_to_db(team: Team, session: Optional[Session] = None) -> TeamModel:
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        stmt = select(TeamModel).where(TeamModel.name == team.name)
        existing = session.execute(stmt).scalar_one_or_none()
        if existing:
            # Update players
            session.delete(existing)
            session.flush()

        team_model = TeamModel.from_domain(team)
        session.add(team_model)
        session.commit()
        session.refresh(team_model)
        return team_model
    except Exception:
        session.rollback()
        raise
    finally:
        if close_session:
            session.close()
