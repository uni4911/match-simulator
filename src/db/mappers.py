from __future__ import annotations
from src.models.models import Position, Player, FieldPlayer, Goalkeeper, Team
from src.db.database import TeamModel, PlayerModel


class PlayerMapper:
    @staticmethod
    def to_domain(model: PlayerModel) -> Player:
        pos_enum = Position[model.position] if isinstance(model.position, str) and model.position in Position.__members__ else Position.CENTRAL_MIDFIELDER
        fn = model.full_name or model.short_name or "Unknown Player"
        sn = model.short_name or model.full_name or "Unknown Player"
        if pos_enum == Position.GOALKEEPER:
            player: Player = Goalkeeper(
                full_name=fn,
                short_name=sn,
                diving=model.diving or 50,
                handling=model.handling or 50,
                kicking=model.kicking or 50,
                reflexes=model.reflexes or 50,
                speed=model.speed or 50,
                positioning=model.positioning or 50,
                age=model.age,
                nationality=model.nationality,
                height=model.height
            )
        else:
            player = FieldPlayer(
                full_name=fn,
                short_name=sn,
                position=pos_enum,
                pace=model.pace or 50,
                shooting=model.shooting or 50,
                passing=model.passing or 50,
                dribbling=model.dribbling or 50,
                defending=model.defence or 50,
                physical=model.physical or 50,
                heading=model.heading or 50,
                height=model.height,
                age=model.age,
                nationality=model.nationality
            )
        player.fitness = model.fitness
        player.form = model.form
        return player

    @staticmethod
    def to_model(player: Player) -> PlayerModel:
        if isinstance(player, Goalkeeper):
            return PlayerModel(
                full_name=player.full_name,
                short_name=player.short_name,
                position=player.position.name,
                age=player.age,
                nationality=player.nationality,
                fitness=player.fitness,
                form=player.form,
                height=player.height,
                diving=player.diving,
                handling=player.handling,
                kicking=player.kicking,
                reflexes=player.reflexes,
                speed=player.speed,
                positioning=player.positioning,
            )
        elif isinstance(player, FieldPlayer):
            return PlayerModel(
                full_name=player.full_name,
                short_name=player.short_name,
                position=player.position.name,
                age=player.age,
                nationality=player.nationality,
                fitness=player.fitness,
                form=player.form,
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
            return PlayerModel(
                full_name=player.full_name,
                short_name=player.short_name,
                position=player.position.name,
                age=player.age,
                nationality=player.nationality,
                fitness=player.fitness,
                form=player.form,
                height=player.height,
            )

    @staticmethod
    def update_model(model: PlayerModel, player: Player) -> PlayerModel:
        model.full_name = player.full_name
        model.short_name = player.short_name
        model.position = player.position.name if hasattr(player.position, "name") else str(player.position)
        model.age = player.age
        model.nationality = player.nationality
        model.fitness = player.fitness
        model.form = player.form
        model.height = player.height
        if isinstance(player, Goalkeeper):
            model.diving = player.diving
            model.handling = player.handling
            model.kicking = player.kicking
            model.reflexes = player.reflexes
            model.speed = player.speed
            model.positioning = player.positioning
            model.pace = None
            model.shooting = None
            model.passing = None
            model.dribbling = None
            model.defence = None
            model.physical = None
            model.heading = None
        elif isinstance(player, FieldPlayer):
            model.pace = player.base_pace
            model.shooting = player.base_shooting
            model.passing = player.base_passing
            model.dribbling = player.base_dribbling
            model.defence = player.base_defending
            model.physical = player.base_physical
            model.heading = player.heading
            model.diving = None
            model.handling = None
            model.kicking = None
            model.reflexes = None
            model.speed = None
            model.positioning = None
        return model


class TeamMapper:
    @staticmethod
    def to_domain(model: TeamModel) -> Team:
        domain_players = [PlayerMapper.to_domain(p) for p in model.players]
        league_name = model.league.name if model.league else "Inne"
        formation = getattr(model, "formation", "4-3-3") or "4-3-3"
        return Team(model.name, domain_players, league=league_name, formation=formation)

    @staticmethod
    def to_model(team: Team) -> TeamModel:
        team_model = TeamModel(name=team.name, formation=getattr(team, "formation", "4-3-3") or "4-3-3")
        team_model.players = [PlayerMapper.to_model(p) for p in team.players]
        return team_model

    @staticmethod
    def update_model(team_model: TeamModel, team: Team) -> TeamModel:
        team_model.name = team.name
        team_model.formation = getattr(team, "formation", "4-3-3") or "4-3-3"
        existing_by_full_name = {p.full_name: p for p in team_model.players if p.full_name}
        existing_by_short_name = {p.short_name: p for p in team_model.players if p.short_name}

        updated_players = []
        used_models = set()
        initial_models = set(team_model.players)

        for player in team.players:
            pm = None
            if player.full_name in existing_by_full_name and existing_by_full_name[player.full_name] not in used_models:
                pm = existing_by_full_name[player.full_name]
            elif player.short_name in existing_by_short_name and existing_by_short_name[player.short_name] not in used_models:
                pm = existing_by_short_name[player.short_name]

            if pm is not None:
                PlayerMapper.update_model(pm, player)
                used_models.add(pm)
                updated_players.append(pm)
            else:
                new_pm = PlayerMapper.to_model(player)
                updated_players.append(new_pm)

        orphaned_players = initial_models - used_models

        for pm in orphaned_players:
            pm.team = None

        team_model.players = updated_players
        return team_model

