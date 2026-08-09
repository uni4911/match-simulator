import pytest
from src.db.database import SessionLocal, ConfederationModel, CountryModel, LeagueModel, TeamModel, PlayerModel
from src.db.mappers import PlayerMapper, TeamMapper
from src.db.seeder import seed_all
from src.db.loader import load_all_teams_from_db, load_team_from_db, save_team_to_db
from src.models import Goalkeeper, FieldPlayer, Position, Team


def test_save_team_to_db_updates_existing_records():
    gk = Goalkeeper(full_name="Existing Keeper", short_name="Keeper", diving=70, handling=70)
    fp = FieldPlayer(full_name="Existing Striker", short_name="Striker", position=Position.STRIKER, pace=75, shooting=80)
    team = Team("Existing Team", [gk, fp], league="Test League")

    # Initial save
    team_model_1 = save_team_to_db(team)
    team_id_1 = team_model_1.id
    player_ids_1 = {p.full_name: p.id for p in team_model_1.players}

    assert team_id_1 is not None
    assert len(player_ids_1) == 2

    # Modify domain players
    gk.diving = 95
    fp.base_pace = 99
    fp.fitness = 0.90

    # Save modified team
    team_model_2 = save_team_to_db(team)
    team_id_2 = team_model_2.id
    player_ids_2 = {p.full_name: p.id for p in team_model_2.players}

    # Verify team ID is preserved (not deleted and recreated)
    assert team_id_2 == team_id_1

    # Verify player IDs are preserved (not deleted and recreated)
    assert player_ids_2["Existing Keeper"] == player_ids_1["Existing Keeper"]
    assert player_ids_2["Existing Striker"] == player_ids_1["Existing Striker"]

    # Verify updated values are saved in DB
    with SessionLocal() as db:
        loaded_team = load_team_from_db("Existing Team", session=db)
        assert loaded_team is not None
        loaded_gk = next(p for p in loaded_team.players if p.full_name == "Existing Keeper")
        loaded_fp = next(p for p in loaded_team.players if p.full_name == "Existing Striker")
        assert loaded_gk.diving == 95
        assert loaded_fp.base_pace == 99
        assert loaded_fp.fitness == 0.90



def test_database_seeding_and_counts():
    with SessionLocal() as db:
        seed_all(db)
        conf_count = db.query(ConfederationModel).count()
        country_count = db.query(CountryModel).count()
        league_count = db.query(LeagueModel).count()
        team_count = db.query(TeamModel).count()
        player_count = db.query(PlayerModel).count()

        assert conf_count == 6
        assert country_count >= 211
        assert league_count >= 1
        assert team_count >= 20
        assert player_count >= 400


def test_load_teams_from_db():
    teams = load_all_teams_from_db()
    assert len(teams) >= 20
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
        assert len(teams) >= 20
        # Verified N+1 protection: Batched queries instead of N+1
        assert query_count <= 3
    finally:
        event.remove(engine, "before_cursor_execute", count_queries)


def test_player_model_full_and_short_names():
    with SessionLocal() as db:
        player_model = db.query(PlayerModel).first()
        assert player_model is not None
        assert "name" not in PlayerModel.__table__.columns
        assert "full_name" in PlayerModel.__table__.columns
        assert "short_name" in PlayerModel.__table__.columns
        domain_player = PlayerMapper.to_domain(player_model)
        assert domain_player.full_name is not None
        assert domain_player.short_name is not None


def test_mappers_field_player_and_goalkeeper():
    gk = Goalkeeper(full_name="Manuel Neuer", short_name="Neuer", diving=88, handling=86, kicking=91, reflexes=89, speed=56, positioning=90)
    gk.fitness = 0.90
    gk.form = 1.05

    fp = FieldPlayer(full_name="Robert Lewandowski", short_name="Lewandowski", position=Position.STRIKER, pace=78, shooting=92, passing=79, dribbling=86, defending=44, physical=82)
    fp.fitness = 0.85
    fp.form = 1.20

    gk_model = PlayerMapper.to_model(gk)
    assert gk_model.full_name == "Manuel Neuer"
    assert gk_model.short_name == "Neuer"
    assert gk_model.position == Position.GOALKEEPER.name
    assert gk_model.diving == 88
    assert gk_model.fitness == 0.90
    assert gk_model.form == 1.05

    reconstructed_gk = PlayerMapper.to_domain(gk_model)
    assert isinstance(reconstructed_gk, Goalkeeper)
    assert reconstructed_gk.full_name == "Manuel Neuer"
    assert reconstructed_gk.short_name == "Neuer"
    assert reconstructed_gk.diving == 88
    assert reconstructed_gk.fitness == 0.90
    assert reconstructed_gk.form == 1.05

    fp_model = PlayerMapper.to_model(fp)
    assert fp_model.full_name == "Robert Lewandowski"
    assert fp_model.short_name == "Lewandowski"
    assert fp_model.position == Position.STRIKER.name
    assert fp_model.fitness == 0.85
    assert fp_model.form == 1.20

    reconstructed_fp = PlayerMapper.to_domain(fp_model)
    assert isinstance(reconstructed_fp, FieldPlayer)
    assert reconstructed_fp.full_name == "Robert Lewandowski"
    assert reconstructed_fp.short_name == "Lewandowski"
    assert reconstructed_fp.position == Position.STRIKER
    assert reconstructed_fp.fitness == 0.85
    assert reconstructed_fp.form == 1.20



def test_team_mapper():
    gk = Goalkeeper(full_name="Keeper", short_name="GK")
    fp = FieldPlayer(full_name="Striker", short_name="ST", position=Position.STRIKER)
    team = Team("Test Team", [gk, fp], league="Test League")

    team_model = TeamMapper.to_model(team)
    assert team_model.name == "Test Team"
    assert len(team_model.players) == 2

    reconstructed_team = TeamMapper.to_domain(team_model)
    assert reconstructed_team.name == "Test Team"
    assert len(reconstructed_team.players) == 2




