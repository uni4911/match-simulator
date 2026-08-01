from src.models import Position, Goalkeeper, FieldPlayer, Team
import json

def load_file(file_name: str, team_name: str) -> list[FieldPlayer|Goalkeeper]:
    try:
        with open(f"data/{file_name}",'r', encoding='utf-8') as file:
            player_data = json.load(file)
            team_players = []
            for player in player_data[team_name]:
                position_text = player['position']
                player['position'] = Position[position_text]
                if player['position'] is Position.GOALKEEPER:
                    del player['position']
                    temp_player = Goalkeeper(**player)
                else:
                    temp_player = FieldPlayer(**player)
                team_players.append(temp_player)
            return team_players
    except FileNotFoundError:
        print("data.json doesn't exist")
        raise

def get_team_names(file_name: str = "data.json") -> list[str]:
    with open(f"data/{file_name}", 'r', encoding='utf-8') as file:
        data = json.load(file)
        return list(data.keys())

def load_team(team_name: str, file_name: str = "data.json") -> Team:
    players = load_file(file_name, team_name)
    return Team(team_name, players)

def load_all_teams(file_name: str = "data.json") -> dict[str, Team]:
    names = get_team_names(file_name)
    teams = {}
    for name in names:
        teams[name] = load_team(name, file_name)
    return teams
