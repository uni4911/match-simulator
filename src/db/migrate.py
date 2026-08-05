from src.db.database import engine, Base, SessionLocal, ConfederationModel, CountryModel


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


run_migration = init_db

if __name__ == "__main__":
    init_db()

