from __future__ import annotations
from src.models.models import Position, Player, FieldPlayer, Goalkeeper, Team
from src.db.database import TeamModel, PlayerModel, PlayerStatsModel, GoalkeeperStatsModel


class PlayerMapper:
    @staticmethod
    def to_domain(model: PlayerModel) -> Player:
        pos_enum = Position[model.position]
        if pos_enum == Position.GOALKEEPER:
            gk_stats = model.goalkeeper_stats
            player: Player = Goalkeeper(
                full_name=model.full_name,
                short_name=model.short_name,
                diving=gk_stats.diving if gk_stats else 50,
                handling=gk_stats.handling if gk_stats else 50,
                kicking=gk_stats.kicking if gk_stats else 50,
                reflexes=gk_stats.reflexes if gk_stats else 50,
                speed=gk_stats.speed if gk_stats else 50,
                positioning=gk_stats.positioning if gk_stats else 50,
                age=model.age,
                nationality=model.nationality,
                height=model.height,
                overall=model.overall,
            )
        else:
            p_stats = model.stats
            player = FieldPlayer(
                full_name=model.full_name,
                short_name=model.short_name,
                position=pos_enum,
                pace=p_stats.pace if p_stats else 50,
                shooting=p_stats.shooting if p_stats else 50,
                passing=p_stats.passing if p_stats else 50,
                dribbling=p_stats.dribbling if p_stats else 50,
                defending=p_stats.defence if p_stats else 50,
                physical=p_stats.physical if p_stats else 50,
                heading=p_stats.heading if p_stats else 50,
                height=model.height,
                age=model.age,
                nationality=model.nationality,
                overall=model.overall,
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
                overall=player.overall,
                goalkeeper_stats=GoalkeeperStatsModel(
                    diving=player.diving,
                    handling=player.handling,
                    kicking=player.kicking,
                    reflexes=player.reflexes,
                    speed=player.speed,
                    positioning=player.positioning,
                ),
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
                overall=player.overall,
                stats=PlayerStatsModel(
                    pace=player.base_pace,
                    shooting=player.base_shooting,
                    passing=player.base_passing,
                    dribbling=player.base_dribbling,
                    defence=player.base_defending,
                    physical=player.base_physical,
                    heading=player.heading,
                ),
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
                overall=player.overall,
            )

    @staticmethod
    def update_model(model: PlayerModel, player: Player) -> PlayerModel:
        model.full_name = player.full_name
        model.short_name = player.short_name
        model.position = player.position.name
        model.age = player.age
        model.nationality = player.nationality
        model.fitness = player.fitness
        model.form = player.form
        model.height = player.height
        model.overall = player.overall

        if isinstance(player, Goalkeeper):
            if model.goalkeeper_stats:
                model.goalkeeper_stats.diving = player.diving
                model.goalkeeper_stats.handling = player.handling
                model.goalkeeper_stats.kicking = player.kicking
                model.goalkeeper_stats.reflexes = player.reflexes
                model.goalkeeper_stats.speed = player.speed
                model.goalkeeper_stats.positioning = player.positioning
            else:
                model.goalkeeper_stats = GoalkeeperStatsModel(
                    player_id=model.id,
                    diving=player.diving,
                    handling=player.handling,
                    kicking=player.kicking,
                    reflexes=player.reflexes,
                    speed=player.speed,
                    positioning=player.positioning,
                )
            model.stats = None
        elif isinstance(player, FieldPlayer):
            if model.stats:
                model.stats.pace = player.base_pace
                model.stats.shooting = player.base_shooting
                model.stats.passing = player.base_passing
                model.stats.dribbling = player.base_dribbling
                model.stats.defence = player.base_defending
                model.stats.physical = player.base_physical
                model.stats.heading = player.heading
            else:
                model.stats = PlayerStatsModel(
                    player_id=model.id,
                    pace=player.base_pace,
                    shooting=player.base_shooting,
                    passing=player.base_passing,
                    dribbling=player.base_dribbling,
                    defence=player.base_defending,
                    physical=player.base_physical,
                    heading=player.heading,
                )
            model.goalkeeper_stats = None
        return model


class TeamMapper:
    @staticmethod
    def to_domain(model: TeamModel) -> Team:
        domain_players = [PlayerMapper.to_domain(p) for p in model.players]
        league_name = model.league.name if model.league else "Inne"
        formation = model.formation or "4-3-3"
        return Team(model.name, domain_players, league=league_name, formation=formation)

    @staticmethod
    def to_model(team: Team) -> TeamModel:
        team_model = TeamModel(name=team.name, formation=team.formation or "4-3-3")
        team_model.players = [PlayerMapper.to_model(p) for p in team.players]
        return team_model

    @staticmethod
    def update_model(team_model: TeamModel, team: Team) -> TeamModel:
        team_model.name = team.name
        team_model.formation = team.formation or "4-3-3"
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

