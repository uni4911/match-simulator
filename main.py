from src.engine import Match, MatchEngine
from src.models import Team
from src.loader import load_file
from src.commentator import Commentator

commentator = Commentator()    

python_players = load_file('data.json','PYTHON FC')
java_players = load_file('data.json','CF JAVA')

team_java = Team("Java United", java_players)
team_python = Team("FC Python", python_players)

test_match = Match(team_java, team_python)
engine = MatchEngine(commentator)
engine.play_match(test_match)
print(test_match.match_events)

print("--- WYNIK MECZU ---")
print(f"{test_match.home_team.name}: {test_match.home_score}")
print(f"{test_match.away_team.name}: {test_match.away_score}")