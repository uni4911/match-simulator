from src.models import FieldPlayer, Position, Goalkeeper, MatchPlayer, MatchTeam
import pytest



@pytest.mark.parametrize("name , position, pace, shooting, passing, dribbling, defending, physical, overall, heading, height",
    [("Test",Position.STRIKER,90,82,75,75,40,68,82,75,180),
     ("Test",Position.CENTRE_BACK,70,55,65,50,90,85,81,75,180),
     ("Test", Position.CENTRAL_ATTACKING_MIDFIELDER,75,70,85,85,65,55,78,75,180)])

def test_field_player_overall_calculation(name: str,position: Position, pace: int, shooting: int, passing: int, dribbling: int, defending: int, physical: int, overall:int, heading: int, height: int) -> None:
    playerA = FieldPlayer(name,position,pace,shooting,passing,dribbling,defending, physical,heading,height,overall=overall)
    playerA_overall = playerA.overall
    
    assert playerA_overall == overall

@pytest.mark.parametrize("reflexes, positioning, expected_score",[(85,90,87),(80,85,82)])

def test_goalkeeping_score(reflexes: int, positioning: int, expected_score: int):
    player_test = Goalkeeper("Test",0,0,0,reflexes,0,positioning)
    score = player_test.goalkeeping_score

    assert score == expected_score
@pytest.fixture
def fresh_match_player() -> MatchPlayer:
    player = FieldPlayer(
        name="Jan Kowalski", 
        position=Position.STRIKER, 
        pace=80, shooting=85, passing=70, dribbling=75, defending=30, physical=70,heading=70, height=180
    )
    return MatchPlayer(player)

def test_receive_first_yellow_card(fresh_match_player: MatchPlayer):
    fresh_match_player.receive_card('yellow_card')

    assert fresh_match_player.yellow_card == 1
    assert fresh_match_player.has_red_card == False

def test_receive_two_yellow_cards(fresh_match_player: MatchPlayer):
    fresh_match_player.receive_card('yellow_card')
    fresh_match_player.receive_card('yellow_card')

    assert fresh_match_player.yellow_card == 2 
    assert fresh_match_player.has_red_card == True

def test_receive_red_cards(fresh_match_player: MatchPlayer):
    fresh_match_player.receive_card('red_card')

    assert fresh_match_player.yellow_card == 0  
    assert fresh_match_player.has_red_card == True

def test_minor_injury_stat_penalty(fresh_match_player: MatchPlayer):
    base_shooting = fresh_match_player.shooting
    fresh_match_player.is_injured = True
    fresh_match_player.injury_severity = "minor"
    assert fresh_match_player.shooting < base_shooting
    assert fresh_match_player.stat_modifier < 1.0

def test_severe_injury_forced_off(fresh_match_player: MatchPlayer):
    fresh_match_player.is_injured = True
    fresh_match_player.injury_severity = "severe"
    fresh_match_player.is_forced_off = True
    assert fresh_match_player.is_forced_off == True

def test_is_injured_field(fresh_match_player: MatchPlayer):
    assert fresh_match_player.is_injured is False

    fresh_match_player.is_injured = True
    assert fresh_match_player.is_injured is True

    fresh_match_player.is_injured = False
    assert fresh_match_player.is_injured is False

def test_all_formations_initialization():
    from src.models import AVAILABLE_FORMATIONS, Team
    from src.db.loader import load_file
    players = load_file("data.json", "Python FC")
    team = Team("Python FC", players)

    for name, formation in AVAILABLE_FORMATIONS.items():
        match_team = MatchTeam(team, formation)
        assert len(match_team.players_on_field) == 11
        assert match_team.formation == formation


def test_team_stats_match_defaults_and_total_shots():
    from src.models import TeamStatsMatch
    stats = TeamStatsMatch()
    assert stats.possession_time == 0.0
    assert stats.shots_on_target == 0
    assert stats.shots_off_target == 0
    assert stats.total_shots == 0
    assert stats.fouls == 0
    assert stats.passes == 0
    assert stats.corners == 0
    assert stats.saves == 0

    stats.shots_on_target = 5
    stats.shots_off_target = 3
    assert stats.total_shots == 8


def test_possession_percentage_calculation():
    from src.models import TeamStatsMatch
    home_stats = TeamStatsMatch()
    away_stats = TeamStatsMatch()

    assert home_stats.get_possession_percentage(away_stats) == 50.0

    home_stats.possession_time = 300.0
    away_stats.possession_time = 200.0

    assert home_stats.get_possession_percentage(away_stats) == 60.0
    assert away_stats.get_possession_percentage(home_stats) == 40.0


def test_team_stats_match_reset_and_to_dict():
    from src.models import TeamStatsMatch
    stats = TeamStatsMatch()
    stats.possession_time = 150.0
    stats.shots_on_target = 4
    stats.shots_off_target = 2
    stats.fouls = 3
    stats.passes = 120
    stats.goals = 2

    opponent = TeamStatsMatch()
    opponent.possession_time = 150.0

    d = stats.to_dict(opponent)
    assert d["possession_percentage"] == 50.0
    assert d["shots_on_target"] == 4
    assert d["total_shots"] == 6
    assert d["fouls"] == 3
    assert d["passes"] == 120

    stats.reset()
    assert stats.possession_time == 0.0
    assert stats.shots_on_target == 0
    assert stats.fouls == 0


def test_player_full_name_and_short_name():
    player_default = FieldPlayer(
        full_name="Robert Lewandowski",
        position=Position.STRIKER,
        pace=80, shooting=85, passing=70, dribbling=75, defending=30, physical=70, heading=70, height=180
    )
    assert player_default.full_name == "Robert Lewandowski"
    assert player_default.short_name == "Robert Lewandowski"

    player_custom = FieldPlayer(
        full_name="Robert Lewandowski",
        position=Position.STRIKER,
        pace=80, shooting=85, passing=70, dribbling=75, defending=30, physical=70, heading=70, height=180,
        short_name="Lewandowski"
    )
    assert player_custom.full_name == "Robert Lewandowski"
    assert player_custom.short_name == "Lewandowski"

    match_player = MatchPlayer(player_custom)
    assert match_player.full_name == "Robert Lewandowski"
    assert match_player.short_name == "Lewandowski"


def test_league_team_stats_form_modifier_ceiling_and_floor():
    from src.models import LeagueTeamStats, Team
    team = Team("Test FC", [])
    stats = LeagueTeamStats(team)

    # Initial form
    assert stats.form_modifier == 1.0

    # 5 Wins -> Ceiling +2.5% (1.025)
    for _ in range(5):
        stats.register_match_result(2, 0)
    assert stats.form_modifier == 1.025
    assert len(stats.recent_results) == 5

    # 6th Win -> still 5 recent_results and still 1.025 ceiling
    stats.register_match_result(1, 0)
    assert stats.form_modifier == 1.025
    assert len(stats.recent_results) == 5

    # 5 Losses -> Floor -2.5% (0.975)
    for _ in range(5):
        stats.register_match_result(0, 2)
    assert stats.form_modifier == 0.975
    assert len(stats.recent_results) == 5
    assert stats.form == stats.recent_results

def test_match_team_starter_and_bench_status_tracking():
    from src.models import Team, FieldPlayer, Goalkeeper, Position, FORMATION_433
    gk1 = Goalkeeper("GK 1", 70, 70, 70, 80, 70, 80)
    gk2 = Goalkeeper("GK 2", 60, 60, 60, 70, 60, 70)
    field_players = [
        FieldPlayer(f"Player {i}", pos, 70, 70, 70, 70, 70, 70, 70, 180)
        for i, pos in enumerate(FORMATION_433)
    ]
    bench_fp1 = FieldPlayer("Bench 1", Position.STRIKER, 70, 70, 70, 70, 70, 70, 70, 180)
    bench_fp2 = FieldPlayer("Bench 2", Position.CENTRE_BACK, 70, 70, 70, 70, 70, 70, 70, 180)

    team = Team("Test Team", [gk1, gk2] + field_players + [bench_fp1, bench_fp2])
    match_team = MatchTeam(team, FORMATION_433)

    assert len(match_team.players_on_field) == 11  # 11 starting players on field (1 GK + 10 field players)
    assert len(match_team.bench_players) == 3

    for p in match_team.players_on_field:
        assert p.is_starter is True
        assert p.is_on_field is True

    for p in match_team.bench_players:
        assert p.is_starter is False
        assert p.is_on_field is False

    # Perform a substitution
    starter = match_team.players_on_field[0]
    bench_p = match_team.bench_players[0]
    sub_success = match_team.make_substitution(starter, bench_p)

    assert sub_success is True
    assert starter.is_starter is True
    assert starter.is_on_field is False
    assert bench_p.is_starter is False
    assert bench_p.is_on_field is True


def test_goalkeeper_never_assigned_to_field_position():
    from src.models import Team, FieldPlayer, Goalkeeper, Position, FORMATION_433
    gk1 = Goalkeeper("Primary GK", 85, 85, 75, 90, 70, 85)
    gk2 = Goalkeeper("Backup GK", 80, 80, 70, 85, 65, 80)
    gk3 = Goalkeeper("Third GK", 75, 75, 65, 80, 60, 75)

    # Team has 3 Goalkeepers and only 9 field players (missing 1 field player position)
    field_players = [
        FieldPlayer(f"Field {i}", pos, 70, 70, 70, 70, 70, 70, 70, 180)
        for i, pos in enumerate(FORMATION_433[:9])
    ]

    team = Team("GK Test Team", [gk1, gk2, gk3] + field_players)
    match_team = MatchTeam(team, FORMATION_433)

    # Check assigned position of every starting player on field
    for p in match_team.players_on_field:
        if isinstance(p.player, Goalkeeper):
            assert p.assigned_position == Position.GOALKEEPER, f"Goalkeeper {p.name} assigned to field position {p.assigned_position}"
        else:
            assert p.assigned_position != Position.GOALKEEPER


def test_positional_substitutions_select_appropriate_replacement():
    from src.models import Team, FieldPlayer, Goalkeeper, Position, FORMATION_433
    gk = Goalkeeper("GK", 85, 85, 75, 90, 70, 85)
    
    # 10 field starters matching formation positions exactly
    starters = [
        FieldPlayer(f"Starter {i}", pos, 85, 85, 85, 85, 85, 85, 85, 180)
        for i, pos in enumerate(FORMATION_433)
    ]
    # Set the forward to Kylian Mbappe
    starters[-1] = FieldPlayer("Kylian Mbappe", Position.CENTRAL_FORWARD, 91, 91, 91, 91, 91, 91, 91, 178)
    
    # Bench has Dean Huijsen (CB) listed FIRST, and Endrick (ST) listed SECOND
    huijsen = FieldPlayer("Dean Huijsen", Position.CENTRE_BACK, 78, 78, 78, 78, 78, 78, 78, 192)
    endrick = FieldPlayer("Endrick", Position.STRIKER, 80, 80, 80, 80, 80, 80, 80, 173)

    team = Team("Real Madrid", [gk] + starters + [huijsen, endrick])
    match_team = MatchTeam(team, FORMATION_433)

    # Find Mbappé in match team players on field
    mbappe_mp = next(p for p in match_team.players_on_field if p.player.full_name == "Kylian Mbappe")

    # Ensure bench has Huijsen and Endrick
    bench_names = [p.player.full_name for p in match_team.bench_players]
    assert "Dean Huijsen" in bench_names
    assert "Endrick" in bench_names

    # Find best substitute for Mbappé
    best_sub = match_team.get_best_substitute(mbappe_mp)
    assert best_sub is not None
    assert best_sub.player.full_name == "Endrick", f"Expected Endrick for Mbappe, but got {best_sub.player.full_name}"

    # Verify when defender is subbed off, Huijsen is chosen
    defender_mp = next(p for p in match_team.players_on_field if p.assigned_position in (Position.CENTRE_BACK, Position.LEFT_BACK, Position.RIGHT_BACK))
    best_def_sub = match_team.get_best_substitute(defender_mp)
    assert best_def_sub is not None
    assert best_def_sub.player.full_name == "Dean Huijsen", f"Expected Dean Huijsen for defender, but got {best_def_sub.player.full_name}"

