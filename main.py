from engine import Match
from models import Team, Player, Position

players_A = [
    Player("Bramkarz A", Position.DEFENDER, 85),
    Player("Obrońca A1", Position.DEFENDER, 80),
    Player("Obrońca A2", Position.DEFENDER, 78),
    Player("Pomocnik A1", Position.MIDFIELDER, 82),
    Player("Pomocnik A2", Position.MIDFIELDER, 84),
    Player("Napastnik A", Position.ATTACKER, 88)
]

players_B = [
    Player("Bramkarz B", Position.DEFENDER, 82),
    Player("Obrońca B1", Position.DEFENDER, 81),
    Player("Obrońca B2", Position.DEFENDER, 79),
    Player("Pomocnik B1", Position.MIDFIELDER, 85),
    Player("Pomocnik B2", Position.MIDFIELDER, 80),
    Player("Napastnik B", Position.ATTACKER, 86)
]

team_A = Team("team a",players_A)
team_B = Team("team b",players_B)

match1 = Match(team_A, team_B)


match1.play_match(90)
match1.show_score()