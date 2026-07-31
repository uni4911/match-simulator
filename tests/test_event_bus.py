import pytest
from unittest.mock import MagicMock
from src.event_bus import EventBus
from src.events import MatchEvent, Goal, YellowCardFoul, MatchEndEvent

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
