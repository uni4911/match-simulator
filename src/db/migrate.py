import os
import json
from sqlalchemy import inspect, text, select
from src.db.database import engine, Base, SessionLocal, ConfederationModel, CountryModel, PlayerModel, TeamModel
from src.db.seeder import seed_confederations_and_countries, NATIONALITY_CLEAN_MAP


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "teams" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("teams")]
            if "formation" not in columns:
                conn.execute(text("ALTER TABLE teams ADD COLUMN formation VARCHAR(50) DEFAULT '4-3-3'"))
                conn.commit()
        if "players" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("players")]
            if "full_name" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN full_name VARCHAR(150)"))
            if "short_name" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN short_name VARCHAR(50)"))
            if "overall" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN overall INTEGER"))
            conn.execute(text("UPDATE players SET short_name = full_name WHERE short_name IS NULL OR short_name = ''"))
            conn.commit()

    # Synchronize nationalities, countries and overalls from scraped data
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

                db_players = db.scalars(select(PlayerModel)).all()
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

                if updated_count > 0:
                    db.commit()
                    print(f"Synchronized {updated_count} players with scraped nationality and overall.")
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

                db_players = db.scalars(select(PlayerModel).where(PlayerModel.overall.is_(None))).all()
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
                    if db_p.overall is None:
                        db_p.overall = 50

                db.commit()
            except Exception as e:
                print(f"Error syncing legacy players: {e}")


run_migration = init_db

if __name__ == "__main__":
    init_db()



