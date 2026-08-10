import pytest
from src.db.database import SessionLocal, TeamModel
from src.db.seeder import seed_all
from src.repositories.team_repository import SqlAlchemyTeamRepository
from src.models import Goalkeeper, FieldPlayer, Position, Team


def test_repository_get_team_by_name_and_id():
    with SessionLocal() as db:
        seed_all(db)
        repo = SqlAlchemyTeamRepository(db)

        # Get first available team from DB
        first_team_model = db.query(TeamModel).first()
        assert first_team_model is not None
        target_name = first_team_model.name

        # Retrieve by name
        team = repo.get_team_by_name(target_name)
        assert team is not None
        assert team.name == target_name
        assert len(team.players) > 0

        # Retrieve by id
        team_by_id = repo.get_team_by_id(first_team_model.id)
        assert team_by_id is not None
        assert team_by_id.name == target_name

        # Non-existent team
        assert repo.get_team_by_name("NonExistentTeam123") is None
        assert repo.get_team_by_id(999999) is None


def test_repository_get_all():
    with SessionLocal() as db:
        seed_all(db)
        repo = SqlAlchemyTeamRepository(db)

        all_teams = repo.get_all()
        assert len(all_teams) >= 20
        team_names = [t.name for t in all_teams]
        assert len(team_names) >= 20


def test_repository_save_insert_and_update():
    with SessionLocal() as db:
        repo = SqlAlchemyTeamRepository(db)

        gk = Goalkeeper(full_name="Repo Keeper", short_name="RepoGK", diving=80)
        fp = FieldPlayer(full_name="Repo Striker", short_name="RepoST", position=Position.STRIKER, pace=85)
        new_team = Team("Repo United", [gk, fp], league="Repo League")

        # Save new team
        saved_model = repo.save(new_team)
        assert saved_model.id is not None
        saved_id = saved_model.id

        # Verify query after save
        retrieved_team = repo.get_team_by_name("Repo United")
        assert retrieved_team is not None
        assert retrieved_team.name == "Repo United"
        assert len(retrieved_team.players) == 2

        # Update existing team
        gk.diving = 95
        fp.base_pace = 99
        updated_model = repo.save(new_team)
        assert updated_model.id == saved_id

        reloaded_team = repo.get_team_by_id(saved_id)
        assert reloaded_team is not None
        reloaded_gk = next(p for p in reloaded_team.players if p.full_name == "Repo Keeper")
        assert reloaded_gk.diving == 95


def test_repository_delete():
    with SessionLocal() as db:
        repo = SqlAlchemyTeamRepository(db)

        gk = Goalkeeper(full_name="Delete Keeper", short_name="DelGK")
        team = Team("Team To Delete", [gk], league="Test League")
        saved_model = repo.save(team)
        saved_id = saved_model.id

        assert repo.get_team_by_id(saved_id) is not None

        # Delete by instance/name
        repo.delete(team)
        assert repo.get_team_by_id(saved_id) is None

        # Save another and delete by ID
        saved_model_2 = repo.save(Team("Team To Delete 2", [gk]))
        saved_id_2 = saved_model_2.id
        assert repo.delete_by_id(saved_id_2) is True
        assert repo.get_team_by_id(saved_id_2) is None
        assert repo.delete_by_id(saved_id_2) is False

        # Save another and delete by name
        saved_model_3 = repo.save(Team("Team To Delete 3", [gk]))
        assert repo.delete_by_name("Team To Delete 3") is True
        assert repo.get_team_by_name("Team To Delete 3") is None
        assert repo.delete_by_name("Team To Delete 3") is False
