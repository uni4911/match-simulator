from engine import Match, MatchEngine
from models import Team, Position, Goalkeeper, FieldPlayer
import json

def load_file(file_name: str, team_name: str) -> list[FieldPlayer|Goalkeeper]:

    with open(file_name,'r') as file:
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

python_players = load_file('data.json','PYTHON FC')
java_players = load_file('data.json','CF JAVA')

team_java = Team("Java United", java_players)
team_python = Team("FC Python", python_players)

test_match = Match(team_java, team_python)
engine = MatchEngine()
engine.play_match(test_match)

print("--- WYNIK MECZU ---")
print(f"{test_match.home_team.name}: {test_match.home_score}")
print(f"{test_match.away_team.name}: {test_match.away_score}")