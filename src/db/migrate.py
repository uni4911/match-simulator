import os
import json
from sqlalchemy import inspect, text, select
from sqlalchemy.orm import joinedload
from src.db.database import (
    engine,
    Base,
    SessionLocal,
    ConfederationModel,
    CountryModel,
    PlayerModel,
    PlayerStatsModel,
    GoalkeeperStatsModel,
    TeamModel,
)
from src.db.seeder import seed_confederations_and_countries, NATIONALITY_CLEAN_MAP


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if "teams" in tables:
            columns = [c["name"] for c in inspector.get_columns("teams")]
            if "formation" not in columns:
                conn.execute(text("ALTER TABLE teams ADD COLUMN formation VARCHAR(50) DEFAULT '4-3-3'"))
                conn.commit()
        if "players" in tables:
            columns = [c["name"] for c in inspector.get_columns("players")]
            if "full_name" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN full_name VARCHAR(150)"))
            if "short_name" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN short_name VARCHAR(50)"))
            if "overall" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN overall INTEGER"))
            conn.execute(text("UPDATE players SET short_name = full_name WHERE short_name IS NULL OR short_name = ''"))
            conn.commit()

            # Migrate data from players to player_stats and goalkeeper_stats if legacy columns exist
            if "pace" in columns or "diving" in columns:
                if "player_stats" in tables:
                    ps_count = conn.execute(text("SELECT COUNT(*) FROM player_stats")).scalar()
                    if ps_count == 0:
                        conn.execute(text("""
                            INSERT INTO player_stats (player_id, pace, shooting, passing, dribbling, defence, physical, heading)
                            SELECT id,
                                   COALESCE(pace, 50),
                                   COALESCE(shooting, 50),
                                   COALESCE(passing, 50),
                                   COALESCE(dribbling, 50),
                                   COALESCE(defence, 50),
                                   COALESCE(physical, 50),
                                   COALESCE(heading, 50)
                            FROM players
                            WHERE position != 'GOALKEEPER'
                        """))
                        conn.commit()

                if "goalkeeper_stats" in tables:
                    gk_count = conn.execute(text("SELECT COUNT(*) FROM goalkeeper_stats")).scalar()
                    if gk_count == 0:
                        conn.execute(text("""
                            INSERT INTO goalkeeper_stats (player_id, diving, handling, kicking, reflexes, speed, positioning)
                            SELECT id,
                                   COALESCE(diving, 50),
                                   COALESCE(handling, 50),
                                   COALESCE(kicking, 50),
                                   COALESCE(reflexes, 50),
                                   COALESCE(speed, 50),
                                   COALESCE(positioning, 50)
                            FROM players
                            WHERE position = 'GOALKEEPER'
                        """))
                        conn.commit()

                # Drop old stats columns from players table
                stat_columns_to_drop = [
                    "pace", "shooting", "passing", "dribbling", "defence", "physical", "heading",
                    "diving", "handling", "kicking", "reflexes", "speed", "positioning"
                ]
                for col in stat_columns_to_drop:
                    if col in columns:
                        try:
                            conn.execute(text(f"ALTER TABLE players DROP COLUMN {col}"))
                            conn.commit()
                        except Exception:
                            pass

    # Synchronize nationalities, countries, overalls and stats from scraped data
    sync_players_data_from_json()


def sync_players_data_from_json() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    players_json_path = os.path.join(base_dir, "data", "players.json")
    data_json_path = os.path.join(base_dir, "data", "data.json")

    with SessionLocal() as db:
        country_map = seed_confederations_and_countries(db)

        # 1. Sync from data/players.json
        if os.path.exists(players_json_path):
            try:
                with open(players_json_path, "r", encoding="utf-8") as f:
                    scraped_players = json.load(f)

                # Index scraped players by (team_name, full_name), (team_name, short_name), and full_name
                by_team_and_fullname = {}
                by_team_and_shortname = {}
                by_fullname = {}

                for p in scraped_players:
                    t_name = p.get("team_name")
                    fn = p.get("full_name")
                    sn = p.get("short_name")
                    if t_name and fn:
                        by_team_and_fullname[(t_name.lower(), fn.lower())] = p
                    if t_name and sn:
                        by_team_and_shortname[(t_name.lower(), sn.lower())] = p
                    if fn:
                        by_fullname[fn.lower()] = p

                db_players = db.scalars(
                    select(PlayerModel).options(
                        joinedload(PlayerModel.stats),
                        joinedload(PlayerModel.goalkeeper_stats),
                    )
                ).all()
                updated_count = 0

                for db_p in db_players:
                    team_name = db_p.team.name if db_p.team else None
                    t_key = team_name.lower() if team_name else None
                    fn_key = db_p.full_name.lower() if db_p.full_name else None
                    sn_key = db_p.short_name.lower() if db_p.short_name else None

                    match = None
                    if t_key and fn_key and (t_key, fn_key) in by_team_and_fullname:
                        match = by_team_and_fullname[(t_key, fn_key)]
                    elif t_key and sn_key and (t_key, sn_key) in by_team_and_shortname:
                        match = by_team_and_shortname[(t_key, sn_key)]
                    elif fn_key and fn_key in by_fullname:
                        match = by_fullname[fn_key]

                    if match:
                        raw_nat = match.get("nationality", "Unknown")
                        clean_nat = NATIONALITY_CLEAN_MAP.get(raw_nat, raw_nat)
                        ovr = match.get("overall")
                        c_obj = country_map.get(clean_nat)

                        if db_p.nationality != clean_nat or db_p.overall != ovr or (c_obj and db_p.country_id != c_obj.id):
                            db_p.nationality = clean_nat
                            db_p.overall = ovr
                            if c_obj:
                                db_p.country_id = c_obj.id
                            updated_count += 1

                        if db_p.position == "GOALKEEPER":
                            if db_p.goalkeeper_stats is None:
                                db_p.goalkeeper_stats = GoalkeeperStatsModel(
                                    player_id=db_p.id,
                                    diving=match.get("diving") or 50,
                                    handling=match.get("handling") or 50,
                                    kicking=match.get("kicking") or 50,
                                    reflexes=match.get("reflexes") or 50,
                                    speed=match.get("speed") or 50,
                                    positioning=match.get("positioning") or 50,
                                )
                                updated_count += 1
                            else:
                                db_p.goalkeeper_stats.diving = match.get("diving") or db_p.goalkeeper_stats.diving or 50
                                db_p.goalkeeper_stats.handling = match.get("handling") or db_p.goalkeeper_stats.handling or 50
                                db_p.goalkeeper_stats.kicking = match.get("kicking") or db_p.goalkeeper_stats.kicking or 50
                                db_p.goalkeeper_stats.reflexes = match.get("reflexes") or db_p.goalkeeper_stats.reflexes or 50
                                db_p.goalkeeper_stats.speed = match.get("speed") or db_p.goalkeeper_stats.speed or 50
                                db_p.goalkeeper_stats.positioning = match.get("positioning") or db_p.goalkeeper_stats.positioning or 50
                            db_p.stats = None
                        else:
                            def_val = (match.get("defending") if match.get("defending") is not None else match.get("defence")) or 50
                            if db_p.stats is None:
                                db_p.stats = PlayerStatsModel(
                                    player_id=db_p.id,
                                    pace=match.get("pace") or 50,
                                    shooting=match.get("shooting") or 50,
                                    passing=match.get("passing") or 50,
                                    dribbling=match.get("dribbling") or 50,
                                    defence=def_val,
                                    physical=match.get("physical") or 50,
                                    heading=match.get("heading") or 50,
                                )
                                updated_count += 1
                            else:
                                db_p.stats.pace = match.get("pace") or db_p.stats.pace or 50
                                db_p.stats.shooting = match.get("shooting") or db_p.stats.shooting or 50
                                db_p.stats.passing = match.get("passing") or db_p.stats.passing or 50
                                db_p.stats.dribbling = match.get("dribbling") or db_p.stats.dribbling or 50
                                db_p.stats.defence = def_val if match.get("defending") is not None or match.get("defence") is not None else (db_p.stats.defence or 50)
                                db_p.stats.physical = match.get("physical") or db_p.stats.physical or 50
                                db_p.stats.heading = match.get("heading") or db_p.stats.heading or 50
                            db_p.goalkeeper_stats = None

                if updated_count > 0:
                    db.commit()
                    print(f"Synchronized {updated_count} players with scraped nationality, overall and stats.")
            except Exception as e:
                print(f"Error syncing players from players.json: {e}")

        # 2. Sync from legacy data.json if needed
        if os.path.exists(data_json_path):
            try:
                with open(data_json_path, "r", encoding="utf-8") as f:
                    legacy_data = json.load(f)

                legacy_by_team_name = {}
                for t_name, p_list in legacy_data.items():
                    for p in p_list:
                        p_name = p.get("name") or p.get("full_name") or p.get("short_name")
                        if p_name:
                            legacy_by_team_name[(t_name.lower(), p_name.lower())] = p

                db_players = db.scalars(
                    select(PlayerModel)
                    .options(
                        joinedload(PlayerModel.stats),
                        joinedload(PlayerModel.goalkeeper_stats),
                    )
                    .where(PlayerModel.overall.is_(None))
                ).all()
                for db_p in db_players:
                    t_name = db_p.team.name if db_p.team else None
                    if t_name and db_p.full_name:
                        key = (t_name.lower(), db_p.full_name.lower())
                        if key in legacy_by_team_name:
                            p_info = legacy_by_team_name[key]
                            if "nationality" in p_info and (not db_p.nationality or db_p.nationality == "Unknown"):
                                raw_nat = p_info["nationality"]
                                clean_nat = NATIONALITY_CLEAN_MAP.get(raw_nat, raw_nat)
                                db_p.nationality = clean_nat
                                c_obj = country_map.get(clean_nat)
                                if c_obj:
                                    db_p.country_id = c_obj.id
                            if "overall" in p_info and p_info["overall"]:
                                db_p.overall = p_info["overall"]
                            if db_p.position == "GOALKEEPER":
                                if db_p.goalkeeper_stats is None:
                                    db_p.goalkeeper_stats = GoalkeeperStatsModel(
                                        player_id=db_p.id,
                                        diving=p_info.get("diving") or 50,
                                        handling=p_info.get("handling") or 50,
                                        kicking=p_info.get("kicking") or 50,
                                        reflexes=p_info.get("reflexes") or 50,
                                        speed=p_info.get("speed") or 50,
                                        positioning=p_info.get("positioning") or 50,
                                    )
                            else:
                                def_val = (p_info.get("defending") if p_info.get("defending") is not None else p_info.get("defence")) or 50
                                if db_p.stats is None:
                                    db_p.stats = PlayerStatsModel(
                                        player_id=db_p.id,
                                        pace=p_info.get("pace") or 50,
                                        shooting=p_info.get("shooting") or 50,
                                        passing=p_info.get("passing") or 50,
                                        dribbling=p_info.get("dribbling") or 50,
                                        defence=def_val,
                                        physical=p_info.get("physical") or 50,
                                        heading=p_info.get("heading") or 50,
                                    )
                    if db_p.overall is None:
                        db_p.overall = 50

                db.commit()
            except Exception as e:
                print(f"Error syncing legacy players: {e}")


run_migration = init_db

if __name__ == "__main__":
    init_db()



