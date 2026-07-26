import os
from src.loader import load_file
from src.models import Team, FORMATION_433
from src.engine import MatchTeam, Match, MatchEngine
from src.commentator import Commentator

def main():
    json_filename = "data.json"
    
    print("==========================================")
    print("   SYMULATOR MECZU PIŁKI NOŻNEJ - TEST   ")
    print("==========================================\n")

    # 1. Wczytanie zawodników dla poszczególnych drużyn z pliku data.json
    try:
        html_players = load_file(json_filename, "Amatorzy HTML")
        java_players = load_file(json_filename, "CF Java")
        python_players = load_file(json_filename, "Python FC")
        rust_players = load_file(json_filename, "Galacticos Rust")
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku '{json_filename}' w katalogu 'data/'.")
        return
    except KeyError as e:
        print(f"Błąd: Nie znaleziono drużyny w pliku JSON: {e}")
        return

    team_html = Team("Amatorzy HTML", html_players)
    team_java = Team("CF Java", java_players)
    team_python = Team("Python FC", python_players)
    team_rust = Team("Galacticos Rust", rust_players)

    home_team_obj = team_java
    away_team_obj = team_python

    print(f"Mecz: {home_team_obj.name} (Gospodarze) vs {away_team_obj.name} (Goście)")
    print("Formacja obu zespołów: 4-3-3\n")


    match_home = MatchTeam(home_team_obj, FORMATION_433)
    match_away = MatchTeam(away_team_obj, FORMATION_433)

    match = Match(match_home, match_away)
    commentator = Commentator()
    engine = MatchEngine(commentator)


    print("--- ROZPOCZĘCIE RELACJI NA ŻYWO ---")
    engine.play_match(match)
    print("--- KONIEC MECZU ---\n")


    print("==========================================")
    print(f"KOŃCOWY WYNIK: {match.home_team.team.name} {match.home_score} - {match.away_score} {match.away_team.team.name}")
    print("==========================================")


    print(f"\nStatystyki drużyny {match.home_team.team.name}:")
    for player in match.home_team.match_players:
        if player.goals > 0 or player.yellow_card > 0 or player.has_red_card:
            print(f" - {player.player.name}: Gole={player.goals}, Żółte kartki={player.yellow_card}, Czerwona kartka={player.has_red_card}")

    print(f"\nStatystyki drużyny {match.away_team.team.name}:")
    for player in match.away_team.match_players:
        if player.goals > 0 or player.yellow_card > 0 or player.has_red_card:
            print(f" - {player.player.name}: Gole={player.goals}, Żółte kartki={player.yellow_card}, Czerwona kartka={player.has_red_card}")

if __name__ == "__main__":
    main()