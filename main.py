from engine import Match 
from models import Team, Position, Goalkeeper, FieldPlayer


cpp_players = [
    Goalkeeper("Bramkarz C++", diving=75, handling=70, kicking=65, reflexes=80, speed=50, positioning=75),
    FieldPlayer("Lewy Obrońca C++", Position.DEFENDER, pace=80, shooting=40, passing=65, dribbling=60, defending=85, physical=80),
    FieldPlayer("Środkowy Obrońca C++ 1", Position.DEFENDER, pace=65, shooting=30, passing=55, dribbling=50, defending=90, physical=88),
    FieldPlayer("Środkowy Obrońca C++ 2", Position.DEFENDER, pace=68, shooting=35, passing=58, dribbling=52, defending=88, physical=90),
    FieldPlayer("Prawy Obrońca C++", Position.DEFENDER, pace=82, shooting=45, passing=68, dribbling=65, defending=82, physical=78),
    FieldPlayer("Lewy Pomocnik C++", Position.MIDFIELDER, pace=85, shooting=70, passing=82, dribbling=80, defending=60, physical=75),
    FieldPlayer("Środkowy Pomocnik C++ 1", Position.MIDFIELDER, pace=75, shooting=75, passing=88, dribbling=85, defending=70, physical=80),
    FieldPlayer("Środkowy Pomocnik C++ 2", Position.MIDFIELDER, pace=78, shooting=72, passing=85, dribbling=82, defending=68, physical=78),
    FieldPlayer("Prawy Pomocnik C++", Position.MIDFIELDER, pace=86, shooting=68, passing=80, dribbling=84, defending=55, physical=72),
    FieldPlayer("Napastnik C++ 1", Position.ATTACKER, pace=90, shooting=88, passing=75, dribbling=85, defending=40, physical=82),
    FieldPlayer("Napastnik C++ 2", Position.ATTACKER, pace=88, shooting=92, passing=70, dribbling=82, defending=35, physical=85)
]


ruby_players = [
    Goalkeeper("Bramkarz Ruby", diving=80, handling=75, kicking=70, reflexes=85, speed=55, positioning=80),
    FieldPlayer("Lewy Obrońca Ruby", Position.DEFENDER, pace=85, shooting=50, passing=70, dribbling=68, defending=80, physical=75),
    FieldPlayer("Środkowy Obrońca Ruby 1", Position.DEFENDER, pace=70, shooting=40, passing=60, dribbling=55, defending=85, physical=82),
    FieldPlayer("Środkowy Obrońca Ruby 2", Position.DEFENDER, pace=72, shooting=45, passing=65, dribbling=58, defending=82, physical=85),
    FieldPlayer("Prawy Obrońca Ruby", Position.DEFENDER, pace=88, shooting=55, passing=75, dribbling=72, defending=78, physical=70),
    FieldPlayer("Defensywny Pomocnik Ruby", Position.MIDFIELDER, pace=75, shooting=60, passing=85, dribbling=75, defending=80, physical=82),
    FieldPlayer("Środkowy Pomocnik Ruby", Position.MIDFIELDER, pace=80, shooting=78, passing=90, dribbling=88, defending=65, physical=75),
    FieldPlayer("Ofensywny Pomocnik Ruby", Position.MIDFIELDER, pace=85, shooting=82, passing=92, dribbling=90, defending=50, physical=70),
    FieldPlayer("Lewy Napastnik Ruby", Position.ATTACKER, pace=92, shooting=85, passing=80, dribbling=88, defending=45, physical=75),
    FieldPlayer("Środkowy Napastnik Ruby", Position.ATTACKER, pace=85, shooting=95, passing=75, dribbling=85, defending=30, physical=88),
    FieldPlayer("Prawy Napastnik Ruby", Position.ATTACKER, pace=90, shooting=88, passing=78, dribbling=86, defending=40, physical=72)
]

team_ruby = Team("Ruby Rovers", ruby_players)
team_cpp = Team("C++ Strikers", cpp_players)

test_match = Match(team_ruby, team_cpp)
test_match.play_match()


print("--- WYNIK MECZU ---")
test_match.show_score()