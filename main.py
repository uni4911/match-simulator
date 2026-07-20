from engine import Match, MatchEngine
from models import Team, Position, Goalkeeper, FieldPlayer


python_players = [
    Goalkeeper("Bramkarz Python", diving=82, handling=78, kicking=75, reflexes=85, speed=60, positioning=80),
    FieldPlayer("Lewy Obrońca Python", Position.LEFT_BACK, pace=85, shooting=45, passing=70, dribbling=65, defending=82, physical=75),
    FieldPlayer("Środkowy Obrońca Python 1", Position.CENTRE_BACK, pace=65, shooting=35, passing=55, dribbling=50, defending=88, physical=90),
    FieldPlayer("Środkowy Obrońca Python 2", Position.CENTRE_BACK, pace=68, shooting=40, passing=60, dribbling=55, defending=86, physical=88),
    FieldPlayer("Prawy Obrońca Python", Position.RIGHT_BACK, pace=82, shooting=50, passing=68, dribbling=62, defending=80, physical=78),
    FieldPlayer("Defensywny Pomocnik Python", Position.CENTRAL_DEFENSIVE_MIDFIELDER, pace=75, shooting=65, passing=80, dribbling=75, defending=85, physical=82),
    FieldPlayer("Środkowy Pomocnik Python", Position.CENTRAL_MIDFIELDER, pace=78, shooting=75, passing=88, dribbling=82, defending=70, physical=78),
    FieldPlayer("Ofensywny Pomocnik Python", Position.CENTRAL_ATTACKING_MIDFIELDER, pace=80, shooting=82, passing=90, dribbling=88, defending=55, physical=70),
    FieldPlayer("Lewy Skrzydłowy Python", Position.LEFT_WING, pace=90, shooting=80, passing=75, dribbling=85, defending=45, physical=72),
    FieldPlayer("Napastnik Python", Position.STRIKER, pace=88, shooting=92, passing=70, dribbling=84, defending=35, physical=85),
    FieldPlayer("Prawy Skrzydłowy Python", Position.RIGHT_WING, pace=92, shooting=78, passing=72, dribbling=86, defending=40, physical=68)
]


java_players = [
    Goalkeeper("Bramkarz Java", diving=78, handling=82, kicking=80, reflexes=80, speed=55, positioning=85),
    FieldPlayer("Wahadłowy Java Lewy", Position.LEFT_WING_BACK, pace=88, shooting=55, passing=72, dribbling=70, defending=75, physical=78),
    FieldPlayer("Środkowy Obrońca Java 1", Position.CENTRE_BACK, pace=62, shooting=30, passing=50, dribbling=45, defending=90, physical=92),
    FieldPlayer("Środkowy Obrońca Java 2", Position.CENTRE_BACK, pace=66, shooting=32, passing=52, dribbling=48, defending=88, physical=90),
    FieldPlayer("Wahadłowy Java Prawy", Position.RIGHT_WING_BACK, pace=86, shooting=58, passing=75, dribbling=72, defending=76, physical=75),
    FieldPlayer("Lewy Pomocnik Java", Position.LEFT_MIDFIELDER, pace=84, shooting=72, passing=82, dribbling=80, defending=60, physical=75),
    FieldPlayer("Środkowy Pomocnik Java", Position.CENTRAL_MIDFIELDER, pace=76, shooting=78, passing=86, dribbling=84, defending=68, physical=80),
    FieldPlayer("Prawy Pomocnik Java", Position.RIGHT_MIDFIELDER, pace=82, shooting=70, passing=84, dribbling=82, defending=62, physical=76),
    FieldPlayer("Cofnięty Napastnik Java", Position.CENTRAL_FORWARD, pace=85, shooting=85, passing=80, dribbling=88, defending=45, physical=72),
    FieldPlayer("Snajper Java 1", Position.STRIKER, pace=90, shooting=88, passing=65, dribbling=82, defending=30, physical=84),
    FieldPlayer("Snajper Java 2", Position.STRIKER, pace=86, shooting=90, passing=68, dribbling=85, defending=35, physical=86)
]

team_java = Team("Java United", java_players)
team_python = Team("FC Python", python_players)

test_match = Match(team_java, team_python)
engine = MatchEngine()

engine.play_match(test_match)


print("--- WYNIK MECZU ---")
print(f"{test_match.home_team.name}: {test_match.home_score}")
print(f"{test_match.away_team.name}: {test_match.away_score}")