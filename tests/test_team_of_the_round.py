import pytest
from src.models import (
    League, Team, FieldPlayer, Position, Goalkeeper,
    MatchTeam, get_formation_positions, FORMATION_433, AVAILABLE_FORMATIONS
)
from src.engine.engine import Match, MatchEngine
from src.engine.league_engine import LeagueEngine
from src.engine.team_of_the_round import (
    get_team_of_the_round, get_team_of_the_season,
    extract_round_candidates, extract_season_candidates, build_squad_selection, SUPPORTED_FORMATIONS
)

def create_rich_team(name: str) -> Team:
    gk = Goalkeeper(f"GK {name}", 82, 80, 75, 84, 60, 80)
    lb = FieldPlayer(f"LB {name}", Position.LEFT_BACK, 78, 55, 74, 76, 78, 75, 68, 178)
    cb1 = FieldPlayer(f"CB1 {name}", Position.CENTRE_BACK, 70, 45, 68, 70, 82, 84, 82, 188)
    cb2 = FieldPlayer(f"CB2 {name}", Position.CENTRE_BACK, 68, 40, 65, 68, 80, 82, 80, 186)
    rb = FieldPlayer(f"RB {name}", Position.RIGHT_BACK, 80, 56, 73, 75, 77, 74, 69, 179)
    cm1 = FieldPlayer(f"CM1 {name}", Position.CENTRAL_MIDFIELDER, 74, 72, 80, 78, 74, 75, 70, 180)
    cm2 = FieldPlayer(f"CM2 {name}", Position.CENTRAL_MIDFIELDER, 73, 70, 82, 79, 72, 73, 68, 177)
    cam = FieldPlayer(f"CAM {name}", Position.CENTRAL_ATTACKING_MIDFIELDER, 76, 78, 84, 82, 60, 68, 65, 175)
    lw = FieldPlayer(f"LW {name}", Position.LEFT_WING, 86, 79, 78, 84, 52, 66, 68, 176)
    st = FieldPlayer(f"ST {name}", Position.STRIKER, 82, 86, 70, 78, 48, 80, 82, 185)
    rw = FieldPlayer(f"RW {name}", Position.RIGHT_WING, 85, 78, 76, 83, 50, 65, 66, 174)
    # Bench
    sub_gk = Goalkeeper(f"SubGK {name}", 74, 72, 70, 75, 55, 72)
    sub_def = FieldPlayer(f"SubDEF {name}", Position.CENTRE_BACK, 70, 40, 65, 68, 75, 78, 76, 184)
    sub_mid = FieldPlayer(f"SubMID {name}", Position.CENTRAL_MIDFIELDER, 72, 68, 75, 74, 70, 72, 68, 178)
    sub_att = FieldPlayer(f"SubATT {name}", Position.STRIKER, 78, 76, 68, 74, 45, 72, 74, 182)

    players = [gk, lb, cb1, cb2, rb, cm1, cm2, cam, lw, st, rw, sub_gk, sub_def, sub_mid, sub_att]
    return Team(name, players)


def test_totw_empty_league():
    league = League(name="Pusta Liga", teams=[])
    data = get_team_of_the_round(league, round_number=1, formation="4-3-3")
    assert data["round_number"] == 1
    assert data["starting_xi"] == []
    assert data["bench"] == []
    assert data["is_round_finished"] == False


def test_tots_empty_league():
    league = League(name="Pusta Liga", teams=[])
    data = get_team_of_the_season(league, formation="4-3-3")
    assert data["starting_xi"] == []
    assert data["bench"] == []
    assert data["is_season_finished"] == False


def test_totw_and_tots_simulation():
    team_a = create_rich_team("Team Alpha")
    team_b = create_rich_team("Team Beta")
    team_c = create_rich_team("Team Gamma")
    team_d = create_rich_team("Team Delta")

    league = League(name="Super Liga", teams=[team_a, team_b, team_c, team_d])
    league_engine = LeagueEngine(league, MatchEngine())
    league_engine.generate_fixture(double_round=False)

    # 4 teams -> 3 rounds, 2 matches per round -> 6 fixtures
    assert len(league.fixtures) == 6

    # Play Round 1 (first 2 matches)
    league_engine.play_match(league.fixtures[0])
    setattr(league.fixtures[0], "is_finished", True)
    league_engine.play_match(league.fixtures[1])
    setattr(league.fixtures[1], "is_finished", True)

    totw_r1 = league_engine.get_team_of_the_round(round_number=1, formation="4-3-3")
    assert totw_r1["round_number"] == 1
    assert totw_r1["is_round_finished"] == True
    assert totw_r1["matches_played_in_round"] == 2
    assert totw_r1["total_matches_in_round"] == 2
    assert len(totw_r1["starting_xi"]) == 11
    assert len(totw_r1["bench"]) == 7
    assert totw_r1["mvp"] is not None
    assert totw_r1["average_rating"] > 5.0
    assert totw_r1["starting_xi"][0]["category"] == "GK"

    # Test round 2 which is NOT yet played
    totw_r2 = league_engine.get_team_of_the_round(round_number=2, formation="4-3-3")
    assert totw_r2["round_number"] == 2
    assert totw_r2["is_round_finished"] == False
    assert totw_r2["matches_played_in_round"] == 0
    assert totw_r2["starting_xi"] == []

    # Play remaining rounds to complete the season
    for fix in league.fixtures[2:]:
        league_engine.play_match(fix)
        setattr(fix, "is_finished", True)

    tots = league_engine.get_team_of_the_season(formation="4-3-3")
    assert tots["is_season_finished"] == True
    assert len(tots["starting_xi"]) == 11
    assert len(tots["bench"]) == 7
    assert tots["mvp"] is not None
    assert tots["best_team_name"] is not None
    assert tots["average_rating"] > 5.0


def test_supported_formations_totw():
    team_a = create_rich_team("Team Alpha")
    team_b = create_rich_team("Team Beta")
    team_c = create_rich_team("Team Gamma")
    team_d = create_rich_team("Team Delta")

    league = League(name="Formation Liga", teams=[team_a, team_b, team_c, team_d])
    league_engine = LeagueEngine(league, MatchEngine())
    league_engine.generate_fixture(double_round=False)

    for fix in league.fixtures:
        league_engine.play_match(fix)
        setattr(fix, "is_finished", True)

    for form in ["4-3-3", "4-4-2", "4-2-3-1", "3-5-2", "3-4-3"]:
        totw = league_engine.get_team_of_the_round(round_number=1, formation=form)
        assert len(totw["starting_xi"]) == 11
        assert totw["formation"] == form
        assert len(totw["bench"]) == 7

        tots = league_engine.get_team_of_the_season(formation=form)
        assert len(tots["starting_xi"]) == 11
        assert tots["formation"] == form


def test_totw_and_tots_api_endpoints():
    from main import (
        league_start, play_league_match, match_options,
        get_league_team_of_the_week, get_league_team_of_the_season
    )
    from api.schemas import CreateLeagueRequest, PlayLeagueMatch

    options = match_options()
    teams = options["teams"][:4] if len(options["teams"]) >= 4 else options["teams"]

    create_req = CreateLeagueRequest(
        league_name="API Liga Test",
        league_teams=teams,
        double_round=False
    )
    league_start(create_req)

    # Play first match
    play_req = PlayLeagueMatch(match_index=0)
    play_league_match(play_req)

    # Test TOTW endpoint
    totw_resp = get_league_team_of_the_week(round_number=1, formation="4-3-3")
    assert totw_resp["round_number"] == 1
    assert len(totw_resp["starting_xi"]) > 0

    # Test TOTS endpoint
    tots_resp = get_league_team_of_the_season(formation="4-3-3")
    assert tots_resp["league_name"] == "API Liga Test"
    assert len(tots_resp["starting_xi"]) > 0


def test_tots_regular_starter_priority_over_few_matches_player():
    from src.models import PlayerSeasonStats

    # Create two strikers
    regular_starter = FieldPlayer("Regular Star ST", Position.STRIKER, 80, 82, 75, 78, 45, 75, 78, 182)
    bench_one_game = FieldPlayer("Bench Sub ST", Position.STRIKER, 75, 75, 70, 72, 40, 70, 72, 180)

    stats_starter = PlayerSeasonStats(regular_starter, team_name="Top FC")
    stats_starter.matches_played = 10
    stats_starter.ratings = [7.8] * 10
    stats_starter.goals = 8
    stats_starter.assists = 4
    stats_starter.motm_awards = 2
    stats_starter.minutes_played = 900

    stats_sub = PlayerSeasonStats(bench_one_game, team_name="Mid FC")
    stats_sub.matches_played = 1
    stats_sub.ratings = [8.8]
    stats_sub.goals = 1
    stats_sub.assists = 0
    stats_sub.motm_awards = 0
    stats_sub.minutes_played = 90

    player_stats = {
        regular_starter: stats_starter,
        bench_one_game: stats_sub
    }

    candidates = extract_season_candidates(player_stats, min_matches=1, total_rounds_played=10)
    assert len(candidates) == 2

    # Check that regular starter's composite score is higher than the 1-match player
    starter_cand = next(c for c in candidates if c.player_name == "Regular Star ST")
    sub_cand = next(c for c in candidates if c.player_name == "Bench Sub ST")

    assert starter_cand.composite_score > sub_cand.composite_score


def test_striker_hattrick_placed_in_attack_not_midfield():
    from src.engine.team_of_the_round import RoundCandidate, build_squad_selection

    # Create candidate striker who scored hattrick
    gyokeres = FieldPlayer("Viktor Gyökeres", Position.STRIKER, 88, 90, 78, 84, 45, 86, 88, 187)
    striker_cand = RoundCandidate(
        player_obj=gyokeres,
        player_name="Viktor Gyökeres",
        full_name="Viktor Gyökeres",
        short_name="V. Gyökeres",
        team_name="Sporting CP",
        position_enum=Position.STRIKER,
        position_str="STRIKER",
        rating=9.8,
        goals=3,
        assists=1,
        passes=25,
        yellow_cards=0,
        has_red_card=False,
        clean_sheet=False,
        is_motm=True,
        overall=84,
        age=26,
        nationality="Sweden",
        minutes_played=90
    )

    # Add other candidates for full 11 + bench
    gk = Goalkeeper("Alisson", 89, 88, 85, 90, 60, 89)
    gk_cand = RoundCandidate(
        player_obj=gk, player_name="Alisson", full_name="Alisson Becker", short_name="Alisson",
        team_name="Liverpool", position_enum=Position.GOALKEEPER, position_str="GOALKEEPER",
        rating=8.2, goals=0, assists=0, passes=30, yellow_cards=0, has_red_card=False,
        clean_sheet=True, is_motm=False, overall=89, age=31, nationality="Brazil", minutes_played=90
    )

    other_cands = [gk_cand, striker_cand]
    # Add defenders
    for i in range(4):
        p = FieldPlayer(f"DEF_{i}", Position.CENTRE_BACK, 75, 40, 70, 72, 80, 82, 80, 185)
        other_cands.append(RoundCandidate(
            player_obj=p, player_name=f"DEF_{i}", full_name=f"DEF_{i}", short_name=f"D{i}",
            team_name="Team D", position_enum=Position.CENTRE_BACK, position_str="CENTRE_BACK",
            rating=7.5, goals=0, assists=0, passes=40, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=78, age=25, nationality="Poland", minutes_played=90
        ))

    # Add midfielders
    for i in range(3):
        p = FieldPlayer(f"MID_{i}", Position.CENTRAL_MIDFIELDER, 75, 70, 80, 78, 70, 72, 70, 180)
        other_cands.append(RoundCandidate(
            player_obj=p, player_name=f"MID_{i}", full_name=f"MID_{i}", short_name=f"M{i}",
            team_name="Team M", position_enum=Position.CENTRAL_MIDFIELDER, position_str="CENTRAL_MIDFIELDER",
            rating=7.8, goals=0, assists=1, passes=55, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=80, age=24, nationality="Spain", minutes_played=90
        ))

    # Add wingers
    lw = FieldPlayer("LW_Star", Position.LEFT_WING, 88, 78, 76, 82, 45, 65, 68, 175)
    rw = FieldPlayer("RW_Star", Position.RIGHT_WING, 87, 77, 75, 80, 44, 64, 66, 174)
    other_cands.append(RoundCandidate(
        player_obj=lw, player_name="LW_Star", full_name="LW_Star", short_name="LW",
        team_name="Team W", position_enum=Position.LEFT_WING, position_str="LEFT_WING",
        rating=8.0, goals=1, assists=0, passes=20, yellow_cards=0, has_red_card=False,
        clean_sheet=False, is_motm=False, overall=82, age=22, nationality="Portugal", minutes_played=90
    ))
    other_cands.append(RoundCandidate(
        player_obj=rw, player_name="RW_Star", full_name="RW_Star", short_name="RW",
        team_name="Team W", position_enum=Position.RIGHT_WING, position_str="RIGHT_WING",
        rating=7.9, goals=0, assists=1, passes=22, yellow_cards=0, has_red_card=False,
        clean_sheet=False, is_motm=False, overall=81, age=23, nationality="France", minutes_played=90
    ))

    # Test across all formations
    for form in ["4-3-3", "4-4-2", "4-2-3-1", "3-5-2", "3-4-3"]:
        squad = build_squad_selection(other_cands, formation=form)
        gyokeres_slot = next((p for p in squad["starting_xi"] if p["player_name"] == "Viktor Gyökeres"), None)
        assert gyokeres_slot is not None, f"Gyökeres should be in Starting XI for formation {form}"
        assert gyokeres_slot["category"] == "ATT", f"Gyökeres category must be ATT in {form}, got {gyokeres_slot['category']}"
        assert "ST" in gyokeres_slot["slot_position"] or gyokeres_slot["slot_position"] == "ST", f"Gyökeres slot position should be ST in {form}, got {gyokeres_slot['slot_position']}"


def test_cdm_and_cm_included_in_midfield():
    from src.engine.team_of_the_round import RoundCandidate, build_squad_selection

    rodri = FieldPlayer("Rodri", Position.CENTRAL_DEFENSIVE_MIDFIELDER, 70, 78, 89, 84, 88, 86, 85, 191)
    kroos = FieldPlayer("Toni Kroos", Position.CENTRAL_MIDFIELDER, 65, 80, 93, 86, 75, 76, 70, 183)
    kdb = FieldPlayer("Kevin De Bruyne", Position.CENTRAL_ATTACKING_MIDFIELDER, 76, 86, 94, 88, 65, 78, 74, 181)

    cands = [
        # GK
        RoundCandidate(
            player_obj=Goalkeeper("Courtois", 90, 89, 85, 91, 60, 90),
            player_name="Courtois", full_name="Thibaut Courtois", short_name="Courtois",
            team_name="Real Madrid", position_enum=Position.GOALKEEPER, position_str="GOALKEEPER",
            rating=8.0, goals=0, assists=0, passes=25, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=90, age=32, nationality="Belgium", minutes_played=90
        ),
        # CDM
        RoundCandidate(
            player_obj=rodri, player_name="Rodri", full_name="Rodrigo Hernandez", short_name="Rodri",
            team_name="Man City", position_enum=Position.CENTRAL_DEFENSIVE_MIDFIELDER, position_str="CENTRAL_DEFENSIVE_MIDFIELDER",
            rating=8.3, goals=0, assists=0, passes=75, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=91, age=28, nationality="Spain", minutes_played=90
        ),
        # CM
        RoundCandidate(
            player_obj=kroos, player_name="Toni Kroos", full_name="Toni Kroos", short_name="T. Kroos",
            team_name="Real Madrid", position_enum=Position.CENTRAL_MIDFIELDER, position_str="CENTRAL_MIDFIELDER",
            rating=8.4, goals=0, assists=1, passes=80, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=90, age=34, nationality="Germany", minutes_played=90
        ),
        # CAM
        RoundCandidate(
            player_obj=kdb, player_name="Kevin De Bruyne", full_name="Kevin De Bruyne", short_name="KDB",
            team_name="Man City", position_enum=Position.CENTRAL_ATTACKING_MIDFIELDER, position_str="CENTRAL_ATTACKING_MIDFIELDER",
            rating=8.5, goals=1, assists=1, passes=50, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=True, overall=91, age=33, nationality="Belgium", minutes_played=90
        ),
        # ST
        RoundCandidate(
            player_obj=FieldPlayer("Haaland", Position.STRIKER, 90, 94, 75, 80, 45, 88, 90, 194),
            player_name="Erling Haaland", full_name="Erling Haaland", short_name="E. Haaland",
            team_name="Man City", position_enum=Position.STRIKER, position_str="STRIKER",
            rating=8.5, goals=2, assists=0, passes=15, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=91, age=24, nationality="Norway", minutes_played=90
        ),
        # Wingers
        RoundCandidate(
            player_obj=FieldPlayer("Vinicius", Position.LEFT_WING, 95, 84, 82, 90, 40, 68, 70, 176),
            player_name="Vinicius Jr", full_name="Vinicius Junior", short_name="Vini Jr",
            team_name="Real Madrid", position_enum=Position.LEFT_WING, position_str="LEFT_WING",
            rating=8.3, goals=1, assists=1, passes=25, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=90, age=24, nationality="Brazil", minutes_played=90
        ),
        RoundCandidate(
            player_obj=FieldPlayer("Saka", Position.RIGHT_WING, 88, 82, 84, 87, 50, 72, 74, 178),
            player_name="Bukayo Saka", full_name="Bukayo Saka", short_name="B. Saka",
            team_name="Arsenal", position_enum=Position.RIGHT_WING, position_str="RIGHT_WING",
            rating=8.2, goals=1, assists=0, passes=30, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=88, age=23, nationality="England", minutes_played=90
        ),
    ]
    # Add 4 defenders
    for i in range(4):
        p = FieldPlayer(f"DEF_{i}", Position.CENTRE_BACK, 75, 40, 70, 72, 85, 84, 82, 188)
        cands.append(RoundCandidate(
            player_obj=p, player_name=f"DEF_{i}", full_name=f"DEF_{i}", short_name=f"D{i}",
            team_name="Def FC", position_enum=Position.CENTRE_BACK, position_str="CENTRE_BACK",
            rating=7.8, goals=0, assists=0, passes=45, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=84, age=26, nationality="Spain", minutes_played=90
        ))

    # Test in 4-3-3 formation
    squad_433 = build_squad_selection(cands, formation="4-3-3")
    starter_names = [p["player_name"] for p in squad_433["starting_xi"]]
    starter_positions = {p["player_name"]: p["slot_position"] for p in squad_433["starting_xi"]}

    assert "Rodri" in starter_names, "Rodri (CDM) should be in Starting XI of 4-3-3"
    assert starter_positions["Rodri"] == "CDM", f"Rodri should be in CDM slot, got {starter_positions['Rodri']}"
    assert "Toni Kroos" in starter_names, "Toni Kroos (CM) should be in Starting XI of 4-3-3"

    # Test in 4-2-3-1 formation
    squad_4231 = build_squad_selection(cands, formation="4-2-3-1")
    starter_names_4231 = [p["player_name"] for p in squad_4231["starting_xi"]]
    assert "Rodri" in starter_names_4231, "Rodri (CDM) should be in Starting XI of 4-2-3-1"


def test_433_midfield_mix_two_offensive_one_defensive():
    from src.engine.team_of_the_round import RoundCandidate, build_squad_selection

    # Suppose we have 2 high-scoring CAMs and 1 holding CDM
    bellingham = FieldPlayer("Jude Bellingham", Position.CENTRAL_ATTACKING_MIDFIELDER, 82, 88, 86, 88, 77, 84, 82, 186)
    kdb = FieldPlayer("Kevin De Bruyne", Position.CENTRAL_ATTACKING_MIDFIELDER, 76, 86, 94, 88, 65, 78, 74, 181)
    rice = FieldPlayer("Declan Rice", Position.CENTRAL_DEFENSIVE_MIDFIELDER, 75, 70, 84, 80, 87, 85, 84, 188)

    cands = [
        # GK
        RoundCandidate(
            player_obj=Goalkeeper("Raya", 85, 84, 82, 86, 60, 85),
            player_name="David Raya", full_name="David Raya", short_name="D. Raya",
            team_name="Arsenal", position_enum=Position.GOALKEEPER, position_str="GOALKEEPER",
            rating=8.0, goals=0, assists=0, passes=30, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=85, age=28, nationality="Spain", minutes_played=90
        ),
        # 1 Defensive Midfielder
        RoundCandidate(
            player_obj=rice, player_name="Declan Rice", full_name="Declan Rice", short_name="D. Rice",
            team_name="Arsenal", position_enum=Position.CENTRAL_DEFENSIVE_MIDFIELDER, position_str="CENTRAL_DEFENSIVE_MIDFIELDER",
            rating=8.2, goals=0, assists=0, passes=65, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=87, age=25, nationality="England", minutes_played=90
        ),
        # 2 Offensive Midfielders
        RoundCandidate(
            player_obj=bellingham, player_name="Jude Bellingham", full_name="Jude Bellingham", short_name="J. Bellingham",
            team_name="Real Madrid", position_enum=Position.CENTRAL_ATTACKING_MIDFIELDER, position_str="CENTRAL_ATTACKING_MIDFIELDER",
            rating=8.7, goals=2, assists=0, passes=45, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=True, overall=90, age=21, nationality="England", minutes_played=90
        ),
        RoundCandidate(
            player_obj=kdb, player_name="Kevin De Bruyne", full_name="Kevin De Bruyne", short_name="KDB",
            team_name="Man City", position_enum=Position.CENTRAL_ATTACKING_MIDFIELDER, position_str="CENTRAL_ATTACKING_MIDFIELDER",
            rating=8.5, goals=1, assists=2, passes=55, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=91, age=33, nationality="Belgium", minutes_played=90
        ),
        # Attackers
        RoundCandidate(
            player_obj=FieldPlayer("Kane", Position.STRIKER, 80, 93, 86, 85, 45, 84, 86, 188),
            player_name="Harry Kane", full_name="Harry Kane", short_name="H. Kane",
            team_name="Bayern", position_enum=Position.STRIKER, position_str="STRIKER",
            rating=8.6, goals=2, assists=1, passes=20, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=90, age=31, nationality="England", minutes_played=90
        ),
        RoundCandidate(
            player_obj=FieldPlayer("Salah", Position.RIGHT_WING, 89, 88, 86, 88, 45, 75, 78, 175),
            player_name="Mohamed Salah", full_name="Mohamed Salah", short_name="M. Salah",
            team_name="Liverpool", position_enum=Position.RIGHT_WING, position_str="RIGHT_WING",
            rating=8.3, goals=1, assists=1, passes=25, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=89, age=32, nationality="Egypt", minutes_played=90
        ),
        RoundCandidate(
            player_obj=FieldPlayer("Son", Position.LEFT_WING, 88, 88, 84, 86, 40, 72, 75, 183),
            player_name="Heung-min Son", full_name="Heung-min Son", short_name="Son",
            team_name="Spurs", position_enum=Position.LEFT_WING, position_str="LEFT_WING",
            rating=8.2, goals=1, assists=0, passes=20, yellow_cards=0, has_red_card=False,
            clean_sheet=False, is_motm=False, overall=87, age=32, nationality="Korea", minutes_played=90
        ),
    ]
    # Add 4 defenders
    for i in range(4):
        p = FieldPlayer(f"DEF_{i}", Position.CENTRE_BACK, 75, 40, 70, 72, 85, 84, 82, 188)
        cands.append(RoundCandidate(
            player_obj=p, player_name=f"DEF_{i}", full_name=f"DEF_{i}", short_name=f"D{i}",
            team_name="Def FC", position_enum=Position.CENTRE_BACK, position_str="CENTRE_BACK",
            rating=7.8, goals=0, assists=0, passes=45, yellow_cards=0, has_red_card=False,
            clean_sheet=True, is_motm=False, overall=84, age=26, nationality="Spain", minutes_played=90
        ))

    squad_433 = build_squad_selection(cands, formation="4-3-3")
    starter_names = [p["player_name"] for p in squad_433["starting_xi"]]

    # Midfield should have Declan Rice (holding) + Jude Bellingham & KDB (offensive)
    assert "Declan Rice" in starter_names, "Declan Rice (holding CDM) must be in Starting XI"
    assert "Jude Bellingham" in starter_names, "Jude Bellingham (offensive MID) must be in Starting XI"
    assert "Kevin De Bruyne" in starter_names, "Kevin De Bruyne (offensive MID) must be in Starting XI"



