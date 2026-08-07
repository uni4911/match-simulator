from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.db.database import TeamModel
from src.db.mappers import TeamMapper
from src.models.models import Team


class TeamRepository(ABC):
    @abstractmethod
    def get_team_by_name(self, name: str) -> Optional[Team]:
        pass

    @abstractmethod
    def get_team_by_id(self, id: int) -> Optional[Team]:
        pass

    @abstractmethod
    def get_all(self) -> list[Team]:
        pass

    @abstractmethod
    def save(self, team: Team) -> TeamModel:
        pass

    @abstractmethod
    def delete(self, team: Team) -> None:
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> bool:
        pass

    @abstractmethod
    def delete_by_name(self, name: str) -> bool:
        pass


class SqlAlchemyTeamRepository(TeamRepository):

    def __init__(self, session: Session):
        self.session: Session = session

    def get_team_by_name(self, name: str) -> Optional[Team]:
        stmt = (
            select(TeamModel)
            .options(joinedload(TeamModel.league), selectinload(TeamModel.players))
            .where(TeamModel.name == name)
        )
        result = self.session.execute(stmt).scalar_one_or_none()

        if result is None:
            return None
        return TeamMapper.to_domain(result)

    def get_team_by_id(self, id: int) -> Optional[Team]:
        stmt = (
            select(TeamModel)
            .options(joinedload(TeamModel.league), selectinload(TeamModel.players))
            .where(TeamModel.id == id)
        )
        result = self.session.execute(stmt).scalar_one_or_none()

        if result is None:
            return None
        return TeamMapper.to_domain(result)

    def get_all(self) -> list[Team]:
        stmt = select(TeamModel).options(
            joinedload(TeamModel.league), selectinload(TeamModel.players)
        )
        results = self.session.execute(stmt).scalars().all()
        return [TeamMapper.to_domain(tm) for tm in results]

    def save(self, team: Team) -> TeamModel:
        try:
            stmt = (
                select(TeamModel)
                .options(selectinload(TeamModel.players))
                .where(TeamModel.name == team.name)
            )
            existing = self.session.execute(stmt).scalar_one_or_none()

            if existing:
                team_model = TeamMapper.update_model(existing, team)
            else:
                team_model = TeamMapper.to_model(team)
                self.session.add(team_model)

            self.session.commit()
            self.session.refresh(team_model)
            return team_model
        except Exception:
            self.session.rollback()
            raise

    def delete(self, team: Team) -> None:
        self.delete_by_name(team.name)

    def delete_by_id(self, id: int) -> bool:
        try:
            stmt = select(TeamModel).where(TeamModel.id == id)
            existing = self.session.execute(stmt).scalar_one_or_none()
            if existing:
                self.session.delete(existing)
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            raise

    def delete_by_name(self, name: str) -> bool:
        try:
            stmt = select(TeamModel).where(TeamModel.name == name)
            existing = self.session.execute(stmt).scalar_one_or_none()
            if existing:
                self.session.delete(existing)
                self.session.commit()
                return True
            return False
        except Exception:
            self.session.rollback()
            raise