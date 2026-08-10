from __future__ import annotations
from typing import Optional, List
from sqlalchemy import ForeignKey, String, Integer, Float, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
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
    formation: Mapped[str] = mapped_column(String(50), default="4-3-3")

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

    def __repr__(self) -> str:
        return f"<TeamModel(id={self.id}, name='{self.name}', formation='{self.formation}')>"


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
    age: Mapped[int] = mapped_column(Integer, default=20)
    nationality: Mapped[str] = mapped_column(String(100), default="Unknown")
    fitness: Mapped[float] = mapped_column(Float, default=1.0)
    form: Mapped[float] = mapped_column(Float, default=1.0)
    height: Mapped[int] = mapped_column(Integer, default=180)
    overall: Mapped[int | None] = mapped_column(Integer, nullable=True)

    stats: Mapped[PlayerStatsModel | None] = relationship(
        "PlayerStatsModel",
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined",
    )
    goalkeeper_stats: Mapped[GoalkeeperStatsModel | None] = relationship(
        "GoalkeeperStatsModel",
        back_populates="player",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<PlayerModel(id={self.id}, full_name='{self.full_name}', short_name='{self.short_name}', position='{self.position}', overall={self.overall})>"


class PlayerStatsModel(Base):
    __tablename__ = "player_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    pace: Mapped[int] = mapped_column(Integer, default=50)
    shooting: Mapped[int] = mapped_column(Integer, default=50)
    passing: Mapped[int] = mapped_column(Integer, default=50)
    dribbling: Mapped[int] = mapped_column(Integer, default=50)
    defence: Mapped[int] = mapped_column(Integer, default=50)
    physical: Mapped[int] = mapped_column(Integer, default=50)
    heading: Mapped[int] = mapped_column(Integer, default=50)

    player: Mapped[PlayerModel] = relationship(back_populates="stats")

    def __repr__(self) -> str:
        return f"<PlayerStatsModel(id={self.id}, player_id={self.player_id}, pace={self.pace}, shooting={self.shooting}, passing={self.passing}, dribbling={self.dribbling}, defence={self.defence}, physical={self.physical}, heading={self.heading})>"


class GoalkeeperStatsModel(Base):
    __tablename__ = "goalkeeper_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    diving: Mapped[int] = mapped_column(Integer, default=50)
    handling: Mapped[int] = mapped_column(Integer, default=50)
    kicking: Mapped[int] = mapped_column(Integer, default=50)
    reflexes: Mapped[int] = mapped_column(Integer, default=50)
    speed: Mapped[int] = mapped_column(Integer, default=50)
    positioning: Mapped[int] = mapped_column(Integer, default=50)

    player: Mapped[PlayerModel] = relationship(back_populates="goalkeeper_stats")

    def __repr__(self) -> str:
        return f"<GoalkeeperStatsModel(id={self.id}, player_id={self.player_id}, diving={self.diving}, handling={self.handling}, kicking={self.kicking}, reflexes={self.reflexes}, speed={self.speed}, positioning={self.positioning})>"