from __future__ import annotations
from typing import TYPE_CHECKING
from src.events.events import (
    MatchEvent, Goal, ShotSave, Foul, YellowCardFoul, RedCardFoul, DoubleYellowCard,
    CornerKickEvent, LongShotEvent, PossessionTimeEvent, PassEvent, ShotOffTargetEvent
)
from src.events.event_bus import EventBus

if TYPE_CHECKING:
    from src.engine.engine import Match
    from src.models import MatchTeam

class MatchStatsTracker:
    def __init__(self, match: Match, event_bus: EventBus | None = None):
        self.match: Match = match
        if event_bus is not None:
            self.subscribe_to(event_bus)

    def subscribe_to(self, event_bus: EventBus) -> None:
        event_bus.subscribe(MatchEvent, self.handle_event)

    def _get_team(self, team_name: str) -> MatchTeam | None:
        if self.match.home_team and self.match.home_team.team.name == team_name:
            return self.match.home_team
        elif self.match.away_team and self.match.away_team.team.name == team_name:
            return self.match.away_team
        return None

    def _get_opponent(self, team_name: str) -> MatchTeam | None:
        if self.match.home_team and self.match.home_team.team.name == team_name:
            return self.match.away_team
        elif self.match.away_team and self.match.away_team.team.name == team_name:
            return self.match.home_team
        return None

    def _find_fouling_team(self, event: Foul) -> MatchTeam | None:
        if hasattr(event, 'team') and event.team:
            team = self._get_team(event.team)
            if team:
                return team
        if self.match.home_team:
            for p in self.match.home_team.match_players:
                if p.player.name == event.fouling_player:
                    return self.match.home_team
        if self.match.away_team:
            for p in self.match.away_team.match_players:
                if p.player.name == event.fouling_player:
                    return self.match.away_team
        return None

    def handle_event(self, event: MatchEvent) -> None:
        if isinstance(event, PossessionTimeEvent):
            team = self._get_team(event.team)
            if team:
                team.stats.possession_time += event.duration

        elif isinstance(event, PassEvent):
            team = self._get_team(event.team)
            if team:
                team.stats.passes += 1

        elif isinstance(event, CornerKickEvent):
            team = self._get_team(event.executing_team)
            if team:
                team.stats.corners += 1

        elif isinstance(event, ShotOffTargetEvent):
            team = self._get_team(event.team)
            if team:
                team.stats.shots_off_target += 1

        elif isinstance(event, Goal):
            team = self._get_team(event.team)
            if team:
                team.stats.shots_on_target += 1
                team.stats.goals += 1

        elif isinstance(event, ShotSave):
            shooting_team = self._get_team(event.team)
            if shooting_team:
                shooting_team.stats.shots_on_target += 1
            saving_team = self._get_opponent(event.team)
            if saving_team:
                saving_team.stats.saves += 1

        elif isinstance(event, LongShotEvent):
            if event.outcome == "saved":
                shooting_team = self._get_team(event.team)
                if shooting_team:
                    shooting_team.stats.shots_on_target += 1
                saving_team = self._get_opponent(event.team)
                if saving_team:
                    saving_team.stats.saves += 1
            elif event.outcome == "missed":
                shooting_team = self._get_team(event.team)
                if shooting_team:
                    shooting_team.stats.shots_off_target += 1

        elif isinstance(event, DoubleYellowCard):
            fouling_team = self._find_fouling_team(event)
            if fouling_team:
                fouling_team.stats.fouls += 1
                fouling_team.stats.yellow_cards += 1
                fouling_team.stats.red_cards += 1

        elif isinstance(event, YellowCardFoul):
            fouling_team = self._find_fouling_team(event)
            if fouling_team:
                fouling_team.stats.fouls += 1
                fouling_team.stats.yellow_cards += 1

        elif isinstance(event, RedCardFoul):
            fouling_team = self._find_fouling_team(event)
            if fouling_team:
                fouling_team.stats.fouls += 1
                fouling_team.stats.red_cards += 1

        elif isinstance(event, Foul):
            fouling_team = self._find_fouling_team(event)
            if fouling_team:
                fouling_team.stats.fouls += 1
