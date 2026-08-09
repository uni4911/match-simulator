from __future__ import annotations
from typing import TYPE_CHECKING
from src.events.events import (
    MatchEvent, Goal, GoalWithAssist, LongShotGoal, PenaltyKickGoal,
    ShotSave, Foul, YellowCardFoul, RedCardFoul, DoubleYellowCard,
    CornerKickEvent, LongShotEvent, PassEvent, ShotOffTargetEvent,
    WingPlayEvent, BuildUpEvent, InterceptionEvent, DispossessedEvent,
    MatchEndEvent
)
from src.events.event_bus import EventBus
from src.models import Position, Goalkeeper

if TYPE_CHECKING:
    from src.engine.engine import Match
    from src.models import MatchPlayer, MatchTeam, Player

class PlayerRatingTracker:
    def __init__(self, match: Match, event_bus: EventBus | None = None):
        self.match: Match = match
        if event_bus is not None:
            self.subscribe_to(event_bus)

    def subscribe_to(self, event_bus: EventBus) -> None:
        event_bus.subscribe(MatchEvent, self.handle_event)

    def _find_player(self, player_name: str) -> MatchPlayer | None:
        if not player_name:
            return None
        for team in [self.match.home_team, self.match.away_team]:
            if team:
                for p in team.match_players:
                    if (
                        p.name == player_name
                        or p.player.name == player_name
                        or getattr(p.player, 'full_name', '') == player_name
                        or getattr(p.player, 'short_name', '') == player_name
                    ):
                        return p
        return None

    def _get_opponent_team(self, team_name: str) -> MatchTeam | None:
        if self.match.home_team and self.match.home_team.team.name == team_name:
            return self.match.away_team
        elif self.match.away_team and self.match.away_team.team.name == team_name:
            return self.match.home_team
        return None

    def _get_goalkeeper_match_player(self, team: MatchTeam | None) -> MatchPlayer | None:
        if not team:
            return None
        for p in team.match_players:
            if isinstance(p.player, Goalkeeper) or p.assigned_position == Position.GOALKEEPER:
                if p.is_on_field or p.is_starter:
                    return p
        for p in team.match_players:
            if isinstance(p.player, Goalkeeper) or p.assigned_position == Position.GOALKEEPER:
                return p
        return None

    def _apply_delta(self, player_or_name: MatchPlayer | Player | str | None, delta: float) -> None:
        if player_or_name is None:
            return
        
        player: MatchPlayer | None = None
        if hasattr(player_or_name, "rating"):
            player = player_or_name  # It's a MatchPlayer
        elif hasattr(player_or_name, "name"):
            player = self._find_player(player_or_name.name)  # It's a Player model
        elif isinstance(player_or_name, str):
            player = self._find_player(player_or_name)

        if player is not None and hasattr(player, "rating"):
            new_rating = player.rating + delta
            player.rating = round(max(1.0, min(10.0, new_rating)), 1)

    def handle_event(self, event: MatchEvent) -> None:
        if isinstance(event, LongShotGoal):
            self._apply_delta(event.goalscorer, +1.35)
            if event.assistant:
                self._apply_delta(event.assistant, +0.6)
            opponent = self._get_opponent_team(event.team)
            if opponent:
                gk = self._get_goalkeeper_match_player(opponent)
                self._apply_delta(gk, -0.25)

        elif isinstance(event, GoalWithAssist):
            self._apply_delta(event.goalscorer, +1.25)
            if event.assistant:
                self._apply_delta(event.assistant, +0.6)
            opponent = self._get_opponent_team(event.team)
            if opponent:
                gk = self._get_goalkeeper_match_player(opponent)
                self._apply_delta(gk, -0.25)

        elif isinstance(event, PenaltyKickGoal):
            self._apply_delta(event.goalscorer, +0.9)
            opponent = self._get_opponent_team(event.team)
            if opponent:
                gk = self._get_goalkeeper_match_player(opponent)
                self._apply_delta(gk, -0.20)

        elif isinstance(event, Goal):
            self._apply_delta(event.goalscorer, +1.35)
            opponent = self._get_opponent_team(event.team)
            if opponent:
                gk = self._get_goalkeeper_match_player(opponent)
                self._apply_delta(gk, -0.25)

        elif isinstance(event, ShotSave):
            self._apply_delta(event.goalkeeper, +0.22)
            if getattr(event, "shooter", None):
                self._apply_delta(event.shooter, +0.10)

        elif isinstance(event, LongShotEvent):
            if event.outcome == "saved":
                self._apply_delta(event.shooter, +0.08)
                opponent = self._get_opponent_team(event.team)
                if opponent:
                    gk = self._get_goalkeeper_match_player(opponent)
                    self._apply_delta(gk, +0.16)
            elif event.outcome == "missed":
                self._apply_delta(event.shooter, -0.03)

        elif isinstance(event, ShotOffTargetEvent):
            self._apply_delta(event.shooter, -0.03)

        elif isinstance(event, InterceptionEvent):
            self._apply_delta(event.interceptor, +0.10)

        elif isinstance(event, DispossessedEvent):
            self._apply_delta(event.player, -0.05)

        elif isinstance(event, WingPlayEvent):
            self._apply_delta(event.winger, +0.15)

        elif isinstance(event, BuildUpEvent):
            self._apply_delta(event.passer, +0.08)

        elif isinstance(event, CornerKickEvent):
            self._apply_delta(event.taker, +0.04)

        elif isinstance(event, PassEvent):
            self._apply_delta(event.passer, +0.008)

        elif isinstance(event, MatchEndEvent):
            # Reward clean sheet to participating defenders and goalkeepers
            home_conceded = self.match.away_score
            away_conceded = self.match.home_score
            for team, conceded in [(self.match.home_team, home_conceded), (self.match.away_team, away_conceded)]:
                if team and conceded == 0:
                    for p in team.match_players:
                        if p.is_on_field or p.is_starter or p in team.played_players:
                            if p.assigned_position in [Position.GOALKEEPER, Position.CENTRE_BACK, Position.LEFT_BACK, Position.RIGHT_BACK]:
                                self._apply_delta(p, +0.20)
            # Reward winning team
            if self.match.home_score > self.match.away_score and self.match.home_team:
                for p in self.match.home_team.match_players:
                    if p.is_on_field or p.is_starter or p in self.match.home_team.played_players:
                        self._apply_delta(p, +0.10)
            elif self.match.away_score > self.match.home_score and self.match.away_team:
                for p in self.match.away_team.match_players:
                    if p.is_on_field or p.is_starter or p in self.match.away_team.played_players:
                        self._apply_delta(p, +0.10)

        elif isinstance(event, DoubleYellowCard):
            self._apply_delta(event.fouling_player, -1.2)

        elif isinstance(event, RedCardFoul):
            self._apply_delta(event.fouling_player, -1.5)

        elif isinstance(event, YellowCardFoul):
            self._apply_delta(event.fouling_player, -0.35)

        elif isinstance(event, Foul):
            self._apply_delta(event.fouling_player, -0.08)

