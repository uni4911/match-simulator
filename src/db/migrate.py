from sqlalchemy import inspect, text
from src.db.database import engine, Base, SessionLocal, ConfederationModel, CountryModel


def init_db() -> None:
    with engine.connect() as conn:
        inspector = inspect(engine)
        if "players" in inspector.get_table_names():
            columns = [c["name"] for c in inspector.get_columns("players")]
            if "full_name" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN full_name VARCHAR(150)"))
            if "short_name" not in columns:
                conn.execute(text("ALTER TABLE players ADD COLUMN short_name VARCHAR(50)"))
            if "name" in columns:
                conn.execute(text("UPDATE players SET full_name = name WHERE full_name IS NULL OR full_name = ''"))
                conn.execute(text("UPDATE players SET short_name = name WHERE short_name IS NULL OR short_name = ''"))
                try:
                    conn.execute(text("ALTER TABLE players DROP COLUMN name"))
                except Exception as e:
                    print(f"Notice: Could not drop column name: {e}")
            conn.commit()
    Base.metadata.create_all(bind=engine)


run_migration = init_db

if __name__ == "__main__":
    init_db()



