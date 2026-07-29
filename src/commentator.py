from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from src.events import (
    KickoffEvent, Goal, GoalWithAssist, ShotSave, PenaltyKickGoal, 
    Foul, YellowCardFoul, RedCardFoul, DoubleYellowCard, MatchEndEvent,
    Substitution, MatchEvent, CornerKickEvent
)
import random

if TYPE_CHECKING:
    from src.engine import Match

KICKOFF_EVENT_COMMENTS = [
    "Sedzia gwizdzo po raz pierwszy! Rozpoczyna druzyna {event.executing_team}.",
    "Pilka wprawiona w ruch przez {event.executing_team}. Gramy!",
    "Gwizdek arbitra! Wybrani zawodnicy zespolu {event.executing_team} wznowili gre od srodkowego kola.",
    "Poczatek spotkania! Przy pilce od pierwszej sekundy zespol {event.executing_team}.",
    "Zaczynamy! Gra od srodka rozpoczyna sie dla druzyny {event.executing_team}.",
    "Sedzia daje sygnal do rozpoczecia meczu! Przejmuje pilke {event.executing_team}.",
    "Gwizdek sedziego rozbrzmiewa na stadionie! Od srodka zawodnicy {event.executing_team}.",
    "I ruszyly zegary! Pierwsze zagranie w tym meczu nalezy do {event.executing_team}.",
    "Zostawmy statystyki, czas na emocje! {event.executing_team} rozpoczyna to widowisko!",
    "Pilka w grze! Zobaczymy, co dzisiaj zaprezentuje nam {event.executing_team}.",
    "Panie i panowie, zaczynamy to wielkie widowisko! Od srodka {event.executing_team}!",
    "Pierwsze podanie w tym spotkaniu, pilke wymieniaja zawodnicy {event.executing_team}.",
    "Trybuny rycza, a {event.executing_team} zaczyna budowac swoj pierwszy atak!",
]

GOAL_COMMENTS = [
    "GOOOOAL! Co za fantastyczne wykonczenie! Strzelcem bramki jest {event.goalscorer}!",
    "Bramka! {event.goalscorer} umieszcza pilke w siatce! Punkty dla {event.team}!",
    "Niesamowite uderzenie! {event.goalscorer} trafia do bramki bez dawania szans obroncom!",
    "Mamy gola! {event.goalscorer} podwyzsza wynik meczu dla {event.team}!",
    "Siatka sie zatrzesla! Kapitalna akcja, ktora wykonczyl {event.goalscorer}!",
    "ALEZ UDERZENIE! {event.goalscorer} nie daje zadnych szans bramkarzowi! Gol dla {event.team}!",
    "Alez precyzja! {event.goalscorer} trafia idealnie w okienko! Kibice {event.team} szaleja na trybunach!",
    "GOOOOOOL! Stadion eksplodowal! {event.goalscorer} wpisuje sie na liste strzelcow!",
    "Co za kunszt! {event.goalscorer} zachowuje zimna krew w polu karnym i zdobywa bramke dla {event.team}!",
    "To byl po prostu majstersztyk! {event.goalscorer} umieszcza pilke tuz przy slupku!",
    "Zimna krew, klasa i precyzja! {event.goalscorer} pokonuje bramkarza!",
    "Prawdziwa poezja futbolu! {event.goalscorer} strzela pieknego gola dla {event.team}!",
    "BRAMKA! Stadion doslownie odlecial! {event.goalscorer} pokazal ogromna klase!",
    "Co za przymierzenie! {event.goalscorer} nie dal bramkarzowi najmniejszych szans! {event.team} w skowronkach!",
    "Futbol z innej planety! {event.goalscorer} konczy te koronkowa akcje trafieniem!",
    "Nici z planow obronnych! {event.goalscorer} mija defensorow i umieszcza pilke w siatce!",
]

GOAL_WITH_ASSIST_COMMENTS = [
    "GOAAAL! {event.goalscorer} wpisuje sie na liste strzelcow, ale co za kapitalna asysta, ktora popisal sie {event.assistant}!",
    "Bramka dla {event.team}! {event.goalscorer} wykonczyl to genialne zagranie, ktore dogral {event.assistant}!",
    "Mamy gola! Perfect duo: {event.assistant} dogrywa na centymetry, a {event.goalscorer} dopelnia formalnosci!",
    "Co za zespolowa akcja! {event.assistant} obsluguje partnera idealnym podaniem, a {event.goalscorer} umieszcza pilke w siatce!",
    "Siatka sie zatrzesla! {event.goalscorer} strzelcem gola, lecz brawa naleza sie rowniez dla {event.assistant} za to kluczowe podanie!",
]

SHOT_SAVE_COMMENTS = [
    "Co za obrona! {event.goalkeeper} wyciaga sie jak struna i paruje ten strzal!",
    "Niesamowity refleks! {event.goalkeeper} ratuje swoj zespol przed utrata bramki!",
    "Strzal byl grozny, ale {event.goalkeeper} pewnie interweniuje!",
    "Bramkarz na miejscu! {event.goalkeeper} zatrzymuje uderzenie zawodnika druzyny przeciwnej!",
    "Fantastyczna parada! {event.goalkeeper} udowadnia swoja klase miedzy slupkami!",
    "Alez wyciagnal sie {event.goalkeeper}! Klasa swiatowa miedzy slupkami!",
    "Obronione! {event.goalkeeper} czyta gre niczym otwarta ksierge!",
    "To powinna byc bramka, ale {event.goalkeeper} robi cos niesamowitego! Co za instynkt!",
    "Pewny chwyt! {event.goalkeeper} uspokaja sytuacje we wlasnym polu karnym.",
    "Zlapal to! {event.goalkeeper} paruje grozne uderzenie na rzut rozny!",
    "Nie ma gola! Kapitalna interwencja, {event.goalkeeper} bohaterem akcji!",
    "Niewiarygodne! Jak on to wyciagnal?! {event.goalkeeper} ratuje skore swoim obroncom!",
    "Koci refleks! {event.goalkeeper} paruje to uderzenie wprost za linie koncowa!",
    "To byl wrezc pewny gol, ale {event.goalkeeper} mowi stanowcze NIE!",
]

PENALTY_KICK_GOAL_COMMENTS = [
    "GOOOOOOL Z RZUTU KARNEGO! {event.goalscorer} pewnym strzalem zamienia 'jedenastke' na bramke dla {event.team}!",
    "Zimna krew! {event.goalscorer} myli bramkarza z karnego! Gol dla {event.team}!",
    "Bezradny bramkarz przy tym strzale z 11 metrow! {event.goalscorer} pewnie egzekwuje rzut karny!",
    "Pewnie, mocno i bez kalkulacji! {event.goalscorer} trafia z karnego dla {event.team}!",
    "Presja go nie przerosla! {event.goalscorer} zdobywa bramke z rzutu karnego!",
    "Spokoj godny mistrza! {event.goalscorer} wysyla bramkarza w jeden rog, a pilke w drugi!",
    "Zimne nerwy i perfekcja! {event.goalscorer} uderza tuz pod poprzeczke z rzutu karnego!",
    "Bramkarz wyczul intencje, ale uderzenie {event.goalscorer} bylo zbyt precyzyjne!",
]

FOUL_COMMENTS = [
    "Ostrzejsze starcie! {event.fouling_player} fauluje przeciwnika!",
    "Gwizdek sedziego! {event.fouling_player} przesadzil z agresja w tej walce o pilke.",
    "Paskudny faul! {event.fouling_player} nieprzepisowo zatrzymuje atak.",
    "Sedzia przerywa gre. {event.fouling_player} dopuszcza sie przewinienia.",
    "Zostawienie nogi... {event.fouling_player} powstrzymuje rywala faulem.",
    "Za mocne wejscie w nogi przeciwnika! {event.fouling_player} przekroczyl granice przepisow.",
    "Taktyczny faul. {event.fouling_player} przerywa obiecujaca akcje rywali.",
    "Ostre sprowadzenie do parteru! {event.fouling_player} zmusza sedziego do uzycia gwizdka.",
]

YELLOW_CARD_FOUL_COMMENTS = [
    "Sedzia siega do kieszeni... Zolta kartka dla {event.fouling_player}!",
    "To musialo sie tak skonczyc! {event.fouling_player} ukarany zoltym kartonikiem.",
    "Za to wejscie {event.fouling_player} oglada zolta kartke. Musi od teraz uwazac!",
    "Arbitra nie przekonaly tlumaczenia. {event.fouling_player} z zolta kartka na swoim koncie.",
    "Ostre starcie i sprawiedliwy wyrok: {event.fouling_player} wpisany do notesu sedziego!",
]

DOUBLE_YELLOW_CARD_COMMENTS = [
    "Druga zolta i w konsekwencji czerwona! {event.fouling_player} opuszcza boisko za drugie przewinienie!",
    "To nie bylo madre zagranie! {event.fouling_player} zbiera druga zolta kartke i oslabia swoj zespol!",
    "Arbiter nie mial litosci! {event.fouling_player} mial juz na koncie kartonik, a teraz wyleci do szatni!",
    "Koniec meczu dla {event.fouling_player}! Druga zolta kartka wyklucza go z dalszej gry!",
]

RED_CARD_FOUL_COMMENTS = [
    "CZERWONA KARTKA! {event.fouling_player} wyleci z boiska za to bezmyslne wejscie!",
    "Dramat zespolu! {event.fouling_player} oslabia swoja druzyne i schodzi do szatni!",
    "Sedzia nie ma zadnych watpliwosci! Prosta czerwona kartka dla {event.fouling_player}!",
    "Brutalne zagranie! {event.fouling_player} opuszcza plac gry po czerwonej kartce!",
    "Koniec meczu dla {event.fouling_player}! Arbiter wyciaga czerwony kartonik!",
]

MATCH_END_COMMENTS = [
    "Koniec meczu! Sedzia gwiżdże po raz ostatni w tym spotkaniu!",
    "Gwizdek arbitra obwieszcza koniec emocji! Mecz dobiegl konca.",
    "To juz wszystko na dzisiaj! Arbiter konczy to zacięte widowisko!",
]

SUBSTITUTION_COMMENTS = [
    "Zmiana w zespole {event.team}: {event.subbed_off} opuszcza boisko, wchodzi {event.subbed_in}!",
    "Roszada w skladzie {event.team}! Zmeczony {event.subbed_off} zastapiony przez {event.subbed_in}.",
]

CORNER_KICK_COMMENTS = [
    "Rzut rozny dla zespolu {event.executing_team}! Do pilki ustawionej w narożniku podchodzi {event.taker}.",
    "Sansa na zagrozenie z rzutu roznego! {event.taker} przygotowuje sie do dosrodkowania.",
    "Krotka narada w polu karnym, a {event.taker} juz ustawia pilke w narożniku boiska dla {event.executing_team}.",
    "Będzie dosrodkowanie z rzutu roznego! {event.taker} spoglada w pole karne.",
]

EVENT_COMMENT_MAP: dict[type[MatchEvent], list[str]] = {
    KickoffEvent: KICKOFF_EVENT_COMMENTS,
    GoalWithAssist: GOAL_WITH_ASSIST_COMMENTS,
    Goal: GOAL_COMMENTS,
    ShotSave: SHOT_SAVE_COMMENTS,
    PenaltyKickGoal: PENALTY_KICK_GOAL_COMMENTS,
    Foul: FOUL_COMMENTS,
    YellowCardFoul: YELLOW_CARD_FOUL_COMMENTS,
    DoubleYellowCard: DOUBLE_YELLOW_CARD_COMMENTS,
    RedCardFoul: RED_CARD_FOUL_COMMENTS,
    MatchEndEvent: MATCH_END_COMMENTS,
    Substitution: SUBSTITUTION_COMMENTS,
    CornerKickEvent: CORNER_KICK_COMMENTS
}
class Commentator:
    def __init__(self):
        self.last_commented_event: MatchEvent | None = None

    def comment(self, match: Match) -> None:
       if not match.match_events:
           return None

       latest_event = match.match_events[-1]
       if self.last_commented_event == latest_event:
           return None

       self.last_commented_event = latest_event

       comments_list = EVENT_COMMENT_MAP.get(type(latest_event))
       if comments_list:
           comment = random.choice(comments_list)
           minute = latest_event.second // 60
           print(f"{minute}' min: {comment.format(event=latest_event)}")
    