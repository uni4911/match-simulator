from src.engine import Match, MatchEngine
from src.models import Team, MatchTeam, FORMATION_433
from src.loader import load_file
from src.commentator import Commentator

commentator = Commentator()    

python_players = load_file('data.json','PYTHON FC')
java_players = load_file('data.json','CF JAVA')

team_java = Team("Java United", java_players)
team_python = Team("FC Python", python_players)
match_java = MatchTeam(team_java, FORMATION_433)
match_python = MatchTeam(team_python, FORMATION_433)


test_match = Match(match_java, match_python)
engine = MatchEngine(commentator)
engine.play_match(test_match)

print("--- WYNIK MECZU ---")
print(f"{test_match.home_team.team.name}: {test_match.home_score}")
print(f"{test_match.away_team.team.name}: {test_match.away_score}")