import pytest
from src.db.database import SessionLocal, ConfederationModel, CountryModel, LeagueModel, TeamModel, PlayerModel
from src.db.seeder import seed_all
from src.db.loader import load_all_teams_from_db, load_team_from_db


def test_database_seeding_and_counts():
    with SessionLocal() as db:
        seed_all(db)
        conf_count = db.query(ConfederationModel).count()
        country_count = db.query(CountryModel).count()
        league_count = db.query(LeagueModel).count()
        team_count = db.query(TeamModel).count()
        player_count = db.query(PlayerModel).count()

        assert conf_count == 6
        assert country_count == 211
        assert league_count >= 1
        assert team_count == 20
        assert player_count == 400


def test_load_teams_from_db():
    teams = load_all_teams_from_db()
    assert len(teams) == 20
    assert "Python FC" in teams
    python_fc = teams["Python FC"]
    assert python_fc.name == "Python FC"
    assert len(python_fc.players) == 20


def test_load_single_team_from_db():
    team = load_team_from_db("CF Java")
    assert team is not None
    assert team.name == "CF Java"
    assert len(team.players) == 20


def test_load_all_teams_no_n_plus_1():
    from sqlalchemy import event
    from src.db.database import engine

    query_count = 0

    def count_queries(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        query_count += 1

    event.listen(engine, "before_cursor_execute", count_queries)
    try:
        teams = load_all_teams_from_db()
        assert len(teams) == 20
        # Verified N+1 protection: Exactly 2 queries (1 for teams + 1 batched IN for players) instead of 21
        assert query_count <= 2
    finally:
        event.remove(engine, "before_cursor_execute", count_queries)
