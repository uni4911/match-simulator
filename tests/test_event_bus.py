import pytest
from unittest.mock import MagicMock
from src.events.event_bus import EventBus
from src.events.events import MatchEvent, Goal, YellowCardFoul, MatchEndEvent

def test_subscribe_and_publish_event():
    bus = EventBus()
    mock_handler = MagicMock()

    bus.subscribe(Goal, mock_handler)
    goal_event = Goal(second=120, goalscorer="Lewandowski", team="Python FC")
    bus.publish(goal_event)

    mock_handler.assert_called_once_with(goal_event)

def test_subscribe_superclass_receives_subclass_event():
    bus = EventBus()
    mock_handler = MagicMock()

    bus.subscribe(MatchEvent, mock_handler)
    goal_event = Goal(second=300, goalscorer="Ronaldo", team="CF Java")
    bus.publish(goal_event)

    mock_handler.assert_called_once_with(goal_event)

def test_unrelated_event_not_triggered():
    bus = EventBus()
    mock_handler = MagicMock()

    bus.subscribe(YellowCardFoul, mock_handler)
    end_event = MatchEndEvent(second=5400)
    bus.publish(end_event)

    mock_handler.assert_not_called()

def test_unsubscribe_handler():
    bus = EventBus()
    mock_handler = MagicMock()

    bus.subscribe(MatchEvent, mock_handler)
    bus.unsubscribe(MatchEvent, mock_handler)
    
    event = MatchEndEvent(second=5400)
    bus.publish(event)

    mock_handler.assert_not_called()

def test_match_stats_tracker_events():
    from src.engine.engine import Match
    from src.models import Team, MatchTeam, Goalkeeper, FieldPlayer, FORMATION_433, Position
    from src.events.events import (
        Goal, GoalWithAssist, ShotSave, Foul, YellowCardFoul, RedCardFoul, DoubleYellowCard,
        CornerKickEvent, LongShotEvent, PossessionTimeEvent, PassEvent, ShotOffTargetEvent
    )
    gk1 = Goalkeeper("GK1", 80, 80, 70, 85, 60, 80)
    fp1 = [FieldPlayer(f"P1_{i}", pos, 75, 70, 75, 75, 70, 75, 70, 180) for i, pos in enumerate(FORMATION_433)]
    team_a = MatchTeam(Team("Team A", [gk1] + fp1), FORMATION_433)

    gk2 = Goalkeeper("GK2", 80, 80, 70, 85, 60, 80)
    fp2 = [FieldPlayer(f"P2_{i}", pos, 75, 70, 75, 75, 70, 75, 70, 180) for i, pos in enumerate(FORMATION_433)]
    team_b = MatchTeam(Team("Team B", [gk2] + fp2), FORMATION_433)

    match = Match(team_a, team_b)

    match.add_event(PossessionTimeEvent(10, team_a.team.name, 30))
    assert team_a.stats.possession_time == 30.0

    match.add_event(PassEvent(15, team_a.team.name, "P1_0", "P1_1"))
    assert team_a.stats.passes == 1

    match.add_event(Goal(20, "P1_0", team_a.team.name))
    assert team_a.stats.goals == 1
    assert team_a.stats.shots_on_target == 1

    match.add_event(ShotSave(30, "GK2", team_b.team.name))
    assert team_b.stats.shots_on_target == 1
    assert team_a.stats.saves == 1

    match.add_event(ShotOffTargetEvent(40, "P1_1", team_a.team.name))
    assert team_a.stats.shots_off_target == 1

    match.add_event(CornerKickEvent(50, team_b.team.name, "P2_0"))
    assert team_b.stats.corners == 1

    match.add_event(Foul(60, "P1_0", "normal_foul", "freekick", team=team_a.team.name))
    assert team_a.stats.fouls == 1

    match.add_event(YellowCardFoul(70, "P1_0", "yellow_card", "freekick", team=team_a.team.name))
    assert team_a.stats.fouls == 2
    assert team_a.stats.yellow_cards == 1

    match.add_event(RedCardFoul(80, "P1_1", "red_card", "freekick", team=team_a.team.name))
    assert team_a.stats.fouls == 3
    assert team_a.stats.red_cards == 1

    match.add_event(DoubleYellowCard(90, "P1_2", "yellow_card", "freekick", team=team_a.team.name))
    assert team_a.stats.fouls == 4
    assert team_a.stats.yellow_cards == 2
    assert team_a.stats.red_cards == 2

    match.add_event(LongShotEvent(100, "P1_3", team_a.team.name, "saved"))
    assert team_a.stats.shots_on_target == 2
    assert team_b.stats.saves == 1

    match.add_event(LongShotEvent(110, "P1_3", team_a.team.name, "missed"))
    assert team_a.stats.shots_off_target == 2
