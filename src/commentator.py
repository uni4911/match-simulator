from __future__ import annotations
from typing import Optional
from typing import TYPE_CHECKING
from src.events import KickoffEvent, Goal, ShotSave
import random

if TYPE_CHECKING:
    from src.engine import Match

KICKOFF_EVENT_COMMENTS = [
    "Sędzia gwiżdże po raz pierwszy! Rozpoczyna drużyna {event.executing_team}.",
    "Piłka wprawiona w ruch przez {event.executing_team}. Gramy!",
    "Gwizdek arbitra! Wybrani zawodnicy zespołu {event.executing_team} wznowili grę od środkowego koła.",
    "Początek spotkania! Przy piłce od pierwszej sekundy zespół {event.executing_team}.",
    "Zaczynamy! Gra od środka rozpoczyna się dla drużyny {event.executing_team}.",
]

GOAL_COMMENTS = [
    "GOOOOAL! Co za fantastyczne wykończenie! Strzelcem bramki jest {event.goalscorer}!",
    "Bramka! {event.goalscorer} umieszcza piłkę w siatce! Punty dla {event.team}!",
    "Niesamowite uderzenie! {event.goalscorer} trafia do bramki bez dających szans obrońcom!",
    "Mamy gola! {event.goalscorer} podwyższa wynik meczu dla {event.team}!",
    "Siatka się zatrzęsła! Kapitalna akcja, którą wykończył {event.goalscorer}!",
]

SHOT_SAVE_COMMENTS = [
    "Co za obrona! {event.goalkeeper} wyciąga się jak struna i paruje ten strzał!",
    "Niesamowity refleks! {event.goalkeeper} ratuje swój zespół przed utratą bramki!",
    "Strzał był groźny, ale {event.goalkeeper} pewnie interweniuje!",
    "Bramkarz na miejscu! {event.goalkeeper} zatrzymuje uderzenie zawodnika drużyny przeciwnej!",
    "Fantastyczna parada! {event.goalkeeper} udowadnia swoją klasę między słupkami!",
]


class Commentator:
    def __init__(self):
        self.last_commented_event: str|None = None

    def comment(self, match: Match) -> None:
        if len(match.match_events) >0:
            if self.last_commented_event != match.match_events[-1]:
                self.last_commented_event = match.match_events[-1]
                match self.last_commented_event: 

                    case KickoffEvent() as event:
                        template = random.choice(KICKOFF_EVENT_COMMENTS)
                        print(template.format(event=event))
                    case Goal() as event:
                        template = random.choice(GOAL_COMMENTS)
                        print(template.format(event=event))
                    case ShotSave() as event:
                        template = random.choice(SHOT_SAVE_COMMENTS)
                        print(template.format(event=event))
