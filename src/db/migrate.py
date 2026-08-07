from sqlalchemy import inspect, text
from src.db.database import engine, Base, SessionLocal, ConfederationModel, CountryModel


def init_db() -> None:
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
            conn.execute(text("UPDATE players SET short_name = full_name WHERE short_name IS NULL OR short_name = ''"))
            conn.commit()
    Base.metadata.create_all(bind=engine)


run_migration = init_db

if __name__ == "__main__":
    init_db()



