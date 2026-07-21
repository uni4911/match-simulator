from src.engine import Match, MatchEngine
from src.models import Team, Position, Goalkeeper, FieldPlayer
from src.loader import load_file
    

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