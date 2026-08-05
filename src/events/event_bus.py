from typing import Callable, Type
from src.events.events import MatchEvent

class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[Type[MatchEvent], list[Callable[[MatchEvent], None]]] = {}

    def subscribe(self, event_type: Type[MatchEvent], event_handler: Callable[[MatchEvent], None]) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if event_handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(event_handler)

    def unsubscribe(self, event_type: Type[MatchEvent], event_handler: Callable[[MatchEvent], None]) -> None:
        if event_type in self._subscribers and event_handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(event_handler)

    def publish(self, event: MatchEvent) -> None:
        for event_type, handlers in self._subscribers.items():
            if isinstance(event, event_type):
                for handler in list(handlers):
                    handler(event)