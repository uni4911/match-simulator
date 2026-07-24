from __future__ import annotations
from typing import Optional
from typing import TYPE_CHECKING
from src.events import KickoffEvent, Goal, ShotSave, PenaltyKickGoal, FoulDuringAttack
import random

if TYPE_CHECKING:
    from src.engine import Match

KICKOFF_EVENT_COMMENTS = [
    "Sędzia gwiżdże po raz pierwszy! Rozpoczyna drużyna {event.executing_team}.",
    "Piłka wprawiona w ruch przez {event.executing_team}. Gramy!",
    "Gwizdek arbitra! Wybrani zawodnicy zespołu {event.executing_team} wznowili grę od środkowego koła.",
    "Początek spotkania! Przy piłce od pierwszej sekundy zespół {event.executing_team}.",
    "Zaczynamy! Gra od środka rozpoczyna się dla drużyny {event.executing_team}.",
    "Sędzia daje sygnał do rozpoczęcia meczu! Przejmuje piłkę {event.executing_team}.",
    "Gwizdek sędziego rozbrzmiewa na stadionie! Od środka zawodnicy {event.executing_team}.",
    "I ruszyły zegary! Pierwsze zagranie w tym meczu należy do {event.executing_team}.",
    "Zostawmy statystyki, czas na emocje! {event.executing_team} rozpoczyna to widowisko!",
    "Piłka w grze! Zobaczymy, co dzisiaj zaprezentuje nam {event.executing_team}.",
]

GOAL_COMMENTS = [
    "GOOOOAL! Co za fantastyczne wykończenie! Strzelcem bramki jest {event.goalscorer}!",
    "Bramka! {event.goalscorer} umieszcza piłkę w siatce! Punkty dla {event.team}!",
    "Niesamowite uderzenie! {event.goalscorer} trafia do bramki bez dawania szans obrońcom!",
    "Mamy gola! {event.goalscorer} podwyższa wynik meczu dla {event.team}!",
    "Siatka się zatrzęsła! Kapitalna akcja, którą wykończył {event.goalscorer}!",
    "ALEŻ UDERZENIE! {event.goalscorer} nie daje żadnych szans bramkarzowi! Gol dla {event.team}!",
    "Ależ precyzja! {event.goalscorer} trafia idealnie w okienko! Kibice {event.team} szaleją na trybunach!",
    "GOOOOOOL! Stadion eksplodował! {event.goalscorer} wpisuje się na listę strzelców!",
    "Co za kunszt! {event.goalscorer} zachowuje zimną krew w polu karnym i daje prowadzenie/bramkę dla {event.team}!",
    "To była po prostu majstersztyk! {event.goalscorer} umieszcza piłkę tuż przy słupku!",
    "Zimna krew, klasa i precyzja! {event.goalscorer} pokonuje bramkarza!",
    "Prawdziwa poezja futbolu! {event.goalscorer} strzela pięknego gola dla {event.team}!",
]

SHOT_SAVE_COMMENTS = [
    "Co za obrona! {event.goalkeeper} wyciąga się jak struna i paruje ten strzał!",
    "Niesamowity refleks! {event.goalkeeper} ratuje swój zespół przed utratą bramki!",
    "Strzał był groźny, ale {event.goalkeeper} pewnie interweniuje!",
    "Bramkarz na miejscu! {event.goalkeeper} zatrzymuje uderzenie zawodnika drużyny przeciwnej!",
    "Fantastyczna parada! {event.goalkeeper} udowadnia swoją klasę między słupkami!",
    "Ależ wyciągnął się {event.goalkeeper}! Klasa światowa między słupkami!",
    "Obronione! {event.goalkeeper} czyta grę niczym otwartą księgę!",
    "To powinna być bramka, ale {event.goalkeeper} robi coś niesamowitego! Co za instynkt!",
    "Pewny chwyt! {event.goalkeeper} uspokaja sytuację we własnym polu karnym.",
    "Złapał to! {event.goalkeeper} paruje groźne uderzenie na rzut rożny!",
    "Nie ma gola! Kapitalna interwencja, {event.goalkeeper} bohaterem akcji!",
]

PENALTY_KICK_GOAL_COMMENTS = [
    "GOOOOOOL Z RZUTU KARNEGO! {event.goalscorer} pewnym strzałem zamienia 'jedenastkę' na bramkę dla {event.team}!",
    "Zimna krew! {event.goalscorer} myli bramkarza z karnego! Gol dla {event.team}!",
    "Bezradny bramkarz przy tym strzale z 11 metrów! {event.goalscorer} pewnie egzekwuje rzut karny!",
    "Pewnie, mocno i bez kalkulacji! {event.goalscorer} trafia z karnego dla {event.team}!",
    "Presja go nie przerosła! {event.goalscorer} zdobywa bramkę z rzutu karnego!",
]

FOUL_COMMENTS = [
    "Ostrzejsze starcie! {event.fouling_player} fauluje przeciwnika!",
    "Gwizdek sędziego! {event.fouling_player} przesadził z agresją w tej walce o piłkę.",
    "Paskudny faul! {event.fouling_player} nieprzepisowo zatrzymuje atak.",
    "Sędzia przerywa grę. {event.fouling_player} dopuszcza się przewinienia.",
]

class Commentator:
    def __init__(self):
        self.last_commented_event: str|None = None

    def comment(self, match: Match) -> None:
        if match.match_events:
            if self.last_commented_event != match.match_events[-1]:
                self.last_commented_event = match.match_events[-1]

                match self.last_commented_event: 
                    case KickoffEvent() as event:
                        template = random.choice(KICKOFF_EVENT_COMMENTS)
                        minute = event.second // 60 
                        print(f"{minute} minute: {template.format(event=event)}")
                    case Goal() as event:
                        template = random.choice(GOAL_COMMENTS)
                        minute = event.second // 60 
                        print(f"{minute} minute: {template.format(event=event)}")
                    case ShotSave() as event:
                        template = random.choice(SHOT_SAVE_COMMENTS)
                        minute = event.second // 60 
                        print(f"{minute} minute: {template.format(event=event)}")
                    case PenaltyKickGoal() as event:
                        template = random.choice(PENALTY_KICK_GOAL_COMMENTS)
                        minute = event.second // 60 
                        print(f"{minute} minute: {template.format(event=event)}")
                    case FoulDuringAttack() as event:
                        template = random.choice(FOUL_COMMENTS)
                        minute = event.second // 60 
                        print(f"{minute} minute: {template.format(event=event)}")