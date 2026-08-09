import pytest
from src.engine.engine import Match
from src.models import Team, MatchTeam, Goalkeeper, FieldPlayer, FORMATION_433
from src.events.events import (
    Goal, GoalWithAssist, LongShotGoal, PenaltyKickGoal,
    ShotSave, Foul, YellowCardFoul, RedCardFoul, DoubleYellowCard,
    CornerKickEvent, LongShotEvent, PassEvent, ShotOffTargetEvent,
    WingPlayEvent, BuildUpEvent, InterceptionEvent
)
from src.events.rating_tracker import PlayerRatingTracker

@pytest.fixture
def match_setup():
    gk1 = Goalkeeper("GK1", 80, 80, 70, 85, 60, 80)
    fp1 = [FieldPlayer(f"P1_{i}", pos, 75, 70, 75, 75, 70, 75, 70, 180) for i, pos in enumerate(FORMATION_433)]
    team_a = MatchTeam(Team("Team A", [gk1] + fp1), FORMATION_433)

    gk2 = Goalkeeper("GK2", 80, 80, 70, 85, 60, 80)
    fp2 = [FieldPlayer(f"P2_{i}", pos, 75, 70, 75, 75, 70, 75, 70, 180) for i, pos in enumerate(FORMATION_433)]
    team_b = MatchTeam(Team("Team B", [gk2] + fp2), FORMATION_433)

    match = Match(team_a, team_b)
    return match, team_a, team_b

def test_initial_ratings(match_setup):
    match, team_a, team_b = match_setup
    for p in team_a.match_players:
        assert p.rating == 6.0
    for p in team_b.match_players:
        assert p.rating == 6.0

def test_goal_and_assist_ratings(match_setup):
    match, team_a, team_b = match_setup
    # Goal with assist
    match.add_event(GoalWithAssist(100, goalscorer="P1_0", team=team_a.team.name, assistant="P1_1"))
    
    p0 = next(p for p in team_a.match_players if p.player.name == "P1_0")
    p1 = next(p for p in team_a.match_players if p.player.name == "P1_1")
    gk_b = next(p for p in team_b.match_players if p.player.name == "GK2")

    assert p0.rating == round(6.0 + 1.25, 1)  # 7.2
    assert p1.rating == round(6.0 + 0.6, 1)   # 6.6
    assert gk_b.rating == round(6.0 - 0.25, 1) # 5.8

def test_long_shot_goal_ratings(match_setup):
    match, team_a, team_b = match_setup
    match.add_event(LongShotGoal(150, goalscorer="P1_2", team=team_a.team.name, assistant=""))
    p2 = next(p for p in team_a.match_players if p.player.name == "P1_2")
    assert p2.rating == round(6.0 + 1.35, 1)  # 7.4

def test_penalty_goal_ratings(match_setup):
    match, team_a, team_b = match_setup
    match.add_event(PenaltyKickGoal(200, goalscorer="P1_3", team=team_a.team.name))
    p3 = next(p for p in team_a.match_players if p.player.name == "P1_3")
    gk_b = next(p for p in team_b.match_players if p.player.name == "GK2")
    assert p3.rating == round(6.0 + 0.9, 1)   # 6.9
    assert gk_b.rating == round(6.0 - 0.20, 1) # 5.8

def test_shot_save_ratings(match_setup):
    match, team_a, team_b = match_setup
    match.add_event(ShotSave(250, goalkeeper="GK1", team=team_a.team.name))
    gk_a = next(p for p in team_a.match_players if p.player.name == "GK1")
    assert gk_a.rating == round(6.0 + 0.22, 1) # 6.2

def test_fouls_and_cards_ratings(match_setup):
    match, team_a, team_b = match_setup
    p0 = next(p for p in team_a.match_players if p.player.name == "P1_0")
    p1 = next(p for p in team_a.match_players if p.player.name == "P1_1")
    p2 = next(p for p in team_a.match_players if p.player.name == "P1_2")
    p3 = next(p for p in team_a.match_players if p.player.name == "P1_3")

    match.add_event(Foul(300, fouling_player="P1_0", punishment="normal_foul", foul_aftermath="freekick", team=team_a.team.name))
    assert p0.rating == round(6.0 - 0.08, 1) # 5.9

    match.add_event(YellowCardFoul(350, fouling_player="P1_1", punishment="yellow_card", foul_aftermath="freekick", team=team_a.team.name))
    assert p1.rating == round(6.0 - 0.35, 1) # 5.6

    match.add_event(RedCardFoul(400, fouling_player="P1_2", punishment="red_card", foul_aftermath="freekick", team=team_a.team.name))
    assert p2.rating == 4.5

    match.add_event(DoubleYellowCard(450, fouling_player="P1_3", punishment="yellow_card", foul_aftermath="freekick", team=team_a.team.name))
    assert p3.rating == 4.8

def test_defensive_and_offensive_events(match_setup):
    match, team_a, team_b = match_setup
    p0 = next(p for p in team_a.match_players if p.player.name == "P1_0")
    p1 = next(p for p in team_a.match_players if p.player.name == "P1_1")
    p2 = next(p for p in team_a.match_players if p.player.name == "P1_2")

    match.add_event(InterceptionEvent(500, interceptor="P1_0", team=team_a.team.name))
    assert p0.rating == round(6.0 + 0.10, 1)

    match.add_event(WingPlayEvent(550, winger="P1_1", team=team_a.team.name, action_type="cross"))
    assert p1.rating == round(6.0 + 0.15, 1)

    match.add_event(BuildUpEvent(600, team=team_a.team.name, passer="P1_2"))
    assert p2.rating == round(6.0 + 0.08, 1)

def test_dispossessed_and_duel_loss(match_setup):
    from src.events.events import DispossessedEvent
    match, team_a, team_b = match_setup
    p0 = next(p for p in team_a.match_players if p.player.name == "P1_0")

    match.add_event(DispossessedEvent(650, player="P1_0", team=team_a.team.name))
    assert p0.rating == round(6.0 - 0.05, 1)

def test_rating_bounds_clamping(match_setup):
    match, team_a, team_b = match_setup
    p0 = next(p for p in team_a.match_players if p.player.name == "P1_0")
    
    # Repeatedly add goals to test max cap of 10.0
    for _ in range(10):
        match.add_event(Goal(700, goalscorer="P1_0", team=team_a.team.name))
    assert p0.rating == 10.0

    # Repeatedly add red cards to test min cap of 1.0
    p1 = next(p for p in team_a.match_players if p.player.name == "P1_1")
    for _ in range(10):
        match.add_event(RedCardFoul(800, fouling_player="P1_1", punishment="red_card", foul_aftermath="freekick", team=team_a.team.name))
    assert p1.rating == 1.0

def test_team_average_rating_and_man_of_the_match(match_setup):
    match, team_a, team_b = match_setup
    
    # Baseline
    assert team_a.average_rating == 6.0
    assert team_b.average_rating == 6.0
    
    # Score two goals with P1_0
    match.add_event(Goal(100, goalscorer="P1_0", team=team_a.team.name))
    match.add_event(Goal(200, goalscorer="P1_0", team=team_a.team.name))
    
    motm = match.man_of_the_match
    assert motm is not None
    assert motm.player.name == "P1_0"
    assert motm.rating == round(6.0 + 1.35 + 1.35, 1)  # 8.7
    assert team_a.average_rating > 6.0
