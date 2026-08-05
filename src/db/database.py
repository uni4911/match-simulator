from __future__ import annotations
from typing import Optional, List
from sqlalchemy import ForeignKey, String, Integer, Float, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from src.models.models import Position, Player, FieldPlayer, Goalkeeper, Team
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "match_simulator.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    pass


class ConfederationModel(Base):
    __tablename__ = "confederations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    countries: Mapped[list[CountryModel]] = relationship(
        back_populates="confederation", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ConfederationModel(id={self.id}, name='{self.name}', code='{self.code}')>"


class CountryModel(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)

    confederation_id: Mapped[int | None] = mapped_column(
        ForeignKey("confederations.id"), nullable=True
    )

    confederation: Mapped[ConfederationModel | None] = relationship(
        back_populates="countries"
    )
    leagues: Mapped[list[LeagueModel]] = relationship(
        back_populates="country", cascade="all, delete-orphan"
    )
    teams: Mapped[list[TeamModel]] = relationship(back_populates="country")
    players: Mapped[list[PlayerModel]] = relationship(back_populates="country")

    def __repr__(self) -> str:
        return f"<CountryModel(id={self.id}, name='{self.name}', code='{self.code}')>"


class LeagueModel(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id"), nullable=True
    )

    country: Mapped[CountryModel | None] = relationship(back_populates="leagues")
    teams: Mapped[list[TeamModel]] = relationship(back_populates="league", lazy="selectin")

    def __repr__(self) -> str:
        return f"<LeagueModel(id={self.id}, name='{self.name}')>"


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    league_id: Mapped[int | None] = mapped_column(
        ForeignKey("leagues.id"), nullable=True
    )
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id"), nullable=True
    )

    league: Mapped[LeagueModel | None] = relationship(back_populates="teams", lazy="joined")
    country: Mapped[CountryModel | None] = relationship(back_populates="teams", lazy="joined")
    players: Mapped[list[PlayerModel]] = relationship(
        back_populates="team", cascade="all, delete-orphan", lazy="selectin"
    )

    def to_domain(self) -> Team:
        domain_players = [p.to_domain() for p in self.players]
        return Team(self.name, domain_players)

    @classmethod
    def from_domain(cls, team: Team) -> TeamModel:
        team_model = cls(name=team.name)
        team_model.players = [PlayerModel.from_domain(p) for p in team.players]
        return team_model

    def __repr__(self) -> str:
        return f"<TeamModel(id={self.id}, name='{self.name}')>"


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    team_id: Mapped[int | None] = mapped_column(
        ForeignKey("teams.id"), nullable=True
    )
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id"), nullable=True
    )

    team: Mapped[TeamModel | None] = relationship(back_populates="players")
    country: Mapped[CountryModel | None] = relationship(back_populates="players", lazy="joined")

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    short_name: Mapped[str] = mapped_column(String(50), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(default=20)
    nationality: Mapped[str] = mapped_column(String(100), default="Unknown")
    fitness: Mapped[float] = mapped_column(default=1.0)
    form: Mapped[float] = mapped_column(default=1.0)
    height: Mapped[int] = mapped_column(default=180)


    pace: Mapped[int | None] = mapped_column(nullable=True)
    shooting: Mapped[int | None] = mapped_column(nullable=True)
    passing: Mapped[int | None] = mapped_column(nullable=True)
    dribbling: Mapped[int | None] = mapped_column(nullable=True)
    defence: Mapped[int | None] = mapped_column(nullable=True)
    physical: Mapped[int | None] = mapped_column(nullable=True)
    heading: Mapped[int | None] = mapped_column(nullable=True)

   
    diving: Mapped[int | None] = mapped_column(nullable=True)
    handling: Mapped[int | None] = mapped_column(nullable=True)
    kicking: Mapped[int | None] = mapped_column(nullable=True)
    reflexes: Mapped[int | None] = mapped_column(nullable=True)
    speed: Mapped[int | None] = mapped_column(nullable=True)
    positioning: Mapped[int | None] = mapped_column(nullable=True)

    def to_domain(self) -> Player:
        pos_enum = Position[self.position] if isinstance(self.position, str) and self.position in Position.__members__ else Position.CENTRAL_MIDFIELDER
        fn = self.full_name
        sn = self.short_name or self.full_name
        if pos_enum == Position.GOALKEEPER:
            gk = Goalkeeper(
                full_name=fn,
                short_name=sn,
                diving=self.diving or 50,
                handling=self.handling or 50,
                kicking=self.kicking or 50,
                reflexes=self.reflexes or 50,
                speed=self.speed or 50,
                positioning=self.positioning or 50,
                age=self.age,
                nationality=self.nationality,
                height=self.height
            )
            gk.fitness = self.fitness
            return gk
        else:
            fp = FieldPlayer(
                full_name=fn,
                short_name=sn,
                position=pos_enum,
                pace=self.pace or 50,
                shooting=self.shooting or 50,
                passing=self.passing or 50,
                dribbling=self.dribbling or 50,
                defending=self.defence or 50,
                physical=self.physical or 50,
                heading=self.heading or 50,
                height=self.height,
                age=self.age,
                nationality=self.nationality
            )
            fp.fitness = self.fitness
            return fp

    @classmethod
    def from_domain(cls, player: Player) -> PlayerModel:
        fn = getattr(player, "full_name", getattr(player, "name", "Unknown"))
        sn = getattr(player, "short_name", fn)
        if isinstance(player, Goalkeeper):
            return cls(
                full_name=fn,
                short_name=sn,
                position=player.position.name,
                age=player.age,
                nationality=player.nationality,
                fitness=player.fitness,
                height=player.height,
                diving=player.diving,
                handling=player.handling,
                kicking=player.kicking,
                reflexes=player.reflexes,
                speed=player.speed,
                positioning=player.positioning,
            )
        elif isinstance(player, FieldPlayer):
            return cls(
                full_name=fn,
                short_name=sn,
                position=player.position.name,
                age=player.age,
                nationality=player.nationality,
                fitness=player.fitness,
                height=player.height,
                pace=player.base_pace,
                shooting=player.base_shooting,
                passing=player.base_passing,
                dribbling=player.base_dribbling,
                defence=player.base_defending,
                physical=player.base_physical,
                heading=player.heading,
            )
        else:
            return cls(
                full_name=fn,
                short_name=sn,
                position=player.position.name,
                age=player.age,
                nationality=player.nationality,
                fitness=player.fitness,
                height=player.height,
            )

    def __repr__(self) -> str:
        return f"<PlayerModel(id={self.id}, full_name='{self.full_name}', short_name='{self.short_name}', position='{self.position}')>"