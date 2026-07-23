from src.models import Position, Goalkeeper, FieldPlayer
import json

def load_file(file_name: str, team_name: str) -> list[FieldPlayer|Goalkeeper]:

    try:
        with open(f"data/{file_name}",'r') as file:
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