from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from src.models import Position, Goalkeeper, Player, League, LeagueTeamStats, PlayerSeasonStats

if TYPE_CHECKING:
    from src.engine.engine import Match, MatchPlayer

# Supported formation slot structures
# Each formation defines 11 slots: slot_id -> { "slot_name": str, "category": "GK"|"DEF"|"MID"|"ATT", "preferred_positions": list[Position], "grid_pos": tuple[row, col] }
SUPPORTED_FORMATIONS: dict[str, list[dict]] = {
    "4-3-3": [
        {"slot_id": "GK", "name": "Bramkarz", "short_pos": "GK", "category": "GK", "preferred": [Position.GOALKEEPER], "row": 4, "col": 2},
        {"slot_id": "LB", "name": "Lewy Obrońca", "short_pos": "LB", "category": "DEF", "preferred": [Position.LEFT_BACK, Position.LEFT_WING_BACK], "row": 3, "col": 0},
        {"slot_id": "LCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 3, "col": 1},
        {"slot_id": "RCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 3, "col": 2},
        {"slot_id": "RB", "name": "Prawy Obrońca", "short_pos": "RB", "category": "DEF", "preferred": [Position.RIGHT_BACK, Position.RIGHT_WING_BACK], "row": 3, "col": 3},
        {"slot_id": "LCM", "name": "Środkowy Pomocnik", "short_pos": "CM", "category": "MID", "preferred": [Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER], "row": 2, "col": 0},
        {"slot_id": "CDM", "name": "Defensywny Pomocnik", "short_pos": "CDM", "category": "MID", "preferred": [Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER], "row": 2, "col": 1},
        {"slot_id": "RCM", "name": "Środkowy Pomocnik", "short_pos": "CM", "category": "MID", "preferred": [Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER], "row": 2, "col": 2},
        {"slot_id": "LW", "name": "Lewy Skrzydłowy", "short_pos": "LW", "category": "ATT", "preferred": [Position.LEFT_WING, Position.LEFT_MIDFIELDER], "row": 1, "col": 0},
        {"slot_id": "ST", "name": "Środkowy Napastnik", "short_pos": "ST", "category": "ATT", "preferred": [Position.STRIKER, Position.CENTRAL_FORWARD], "row": 1, "col": 1},
        {"slot_id": "RW", "name": "Prawy Skrzydłowy", "short_pos": "RW", "category": "ATT", "preferred": [Position.RIGHT_WING, Position.RIGHT_MIDFIELDER], "row": 1, "col": 2},
    ],
    "4-4-2": [
        {"slot_id": "GK", "name": "Bramkarz", "short_pos": "GK", "category": "GK", "preferred": [Position.GOALKEEPER], "row": 4, "col": 2},
        {"slot_id": "LB", "name": "Lewy Obrońca", "short_pos": "LB", "category": "DEF", "preferred": [Position.LEFT_BACK, Position.LEFT_WING_BACK], "row": 3, "col": 0},
        {"slot_id": "LCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 3, "col": 1},
        {"slot_id": "RCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 3, "col": 2},
        {"slot_id": "RB", "name": "Prawy Obrońca", "short_pos": "RB", "category": "DEF", "preferred": [Position.RIGHT_BACK, Position.RIGHT_WING_BACK], "row": 3, "col": 3},
        {"slot_id": "LM", "name": "Lewy Pomocnik", "short_pos": "LM", "category": "MID", "preferred": [Position.LEFT_MIDFIELDER, Position.LEFT_WING], "row": 2, "col": 0},
        {"slot_id": "LCM", "name": "Środkowy Pomocnik", "short_pos": "CM", "category": "MID", "preferred": [Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER], "row": 2, "col": 1},
        {"slot_id": "RCM", "name": "Środkowy Pomocnik", "short_pos": "CM", "category": "MID", "preferred": [Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER], "row": 2, "col": 2},
        {"slot_id": "RM", "name": "Prawy Pomocnik", "short_pos": "RM", "category": "MID", "preferred": [Position.RIGHT_MIDFIELDER, Position.RIGHT_WING], "row": 2, "col": 3},
        {"slot_id": "LST", "name": "Środkowy Napastnik", "short_pos": "ST", "category": "ATT", "preferred": [Position.STRIKER, Position.CENTRAL_FORWARD], "row": 1, "col": 0},
        {"slot_id": "RST", "name": "Środkowy Napastnik", "short_pos": "ST", "category": "ATT", "preferred": [Position.STRIKER, Position.CENTRAL_FORWARD], "row": 1, "col": 1},
    ],
    "4-2-3-1": [
        {"slot_id": "GK", "name": "Bramkarz", "short_pos": "GK", "category": "GK", "preferred": [Position.GOALKEEPER], "row": 5, "col": 2},
        {"slot_id": "LB", "name": "Lewy Obrońca", "short_pos": "LB", "category": "DEF", "preferred": [Position.LEFT_BACK, Position.LEFT_WING_BACK], "row": 4, "col": 0},
        {"slot_id": "LCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 4, "col": 1},
        {"slot_id": "RCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 4, "col": 2},
        {"slot_id": "RB", "name": "Prawy Obrońca", "short_pos": "RB", "category": "DEF", "preferred": [Position.RIGHT_BACK, Position.RIGHT_WING_BACK], "row": 4, "col": 3},
        {"slot_id": "LDM", "name": "Defensywny Pomocnik", "short_pos": "CDM", "category": "MID", "preferred": [Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER], "row": 3, "col": 0},
        {"slot_id": "RDM", "name": "Defensywny Pomocnik", "short_pos": "CDM", "category": "MID", "preferred": [Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER], "row": 3, "col": 1},
        {"slot_id": "LAM", "name": "Lewy Ofensywny Pomocnik", "short_pos": "LAM", "category": "MID", "preferred": [Position.LEFT_MIDFIELDER, Position.LEFT_WING, Position.CENTRAL_ATTACKING_MIDFIELDER], "row": 2, "col": 0},
        {"slot_id": "CAM", "name": "Ofensywny Pomocnik", "short_pos": "CAM", "category": "MID", "preferred": [Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_MIDFIELDER], "row": 2, "col": 1},
        {"slot_id": "RAM", "name": "Prawy Ofensywny Pomocnik", "short_pos": "RAM", "category": "MID", "preferred": [Position.RIGHT_MIDFIELDER, Position.RIGHT_WING, Position.CENTRAL_ATTACKING_MIDFIELDER], "row": 2, "col": 2},
        {"slot_id": "ST", "name": "Środkowy Napastnik", "short_pos": "ST", "category": "ATT", "preferred": [Position.STRIKER, Position.CENTRAL_FORWARD], "row": 1, "col": 0},
    ],
    "3-5-2": [
        {"slot_id": "GK", "name": "Bramkarz", "short_pos": "GK", "category": "GK", "preferred": [Position.GOALKEEPER], "row": 4, "col": 2},
        {"slot_id": "LCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK, Position.LEFT_BACK], "row": 3, "col": 0},
        {"slot_id": "CCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 3, "col": 1},
        {"slot_id": "RCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK, Position.RIGHT_BACK], "row": 3, "col": 2},
        {"slot_id": "LWB", "name": "Lewy Wahadłowy", "short_pos": "LWB", "category": "MID", "preferred": [Position.LEFT_WING_BACK, Position.LEFT_BACK, Position.LEFT_MIDFIELDER], "row": 2, "col": 0},
        {"slot_id": "LDM", "name": "Defensywny Pomocnik", "short_pos": "CDM", "category": "MID", "preferred": [Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER], "row": 2, "col": 1},
        {"slot_id": "CAM", "name": "Ofensywny Pomocnik", "short_pos": "CAM", "category": "MID", "preferred": [Position.CENTRAL_ATTACKING_MIDFIELDER, Position.CENTRAL_MIDFIELDER], "row": 2, "col": 2},
        {"slot_id": "RCM", "name": "Środkowy Pomocnik", "short_pos": "CM", "category": "MID", "preferred": [Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER], "row": 2, "col": 3},
        {"slot_id": "RWB", "name": "Prawy Wahadłowy", "short_pos": "RWB", "category": "MID", "preferred": [Position.RIGHT_WING_BACK, Position.RIGHT_BACK, Position.RIGHT_MIDFIELDER], "row": 2, "col": 4},
        {"slot_id": "LST", "name": "Środkowy Napastnik", "short_pos": "ST", "category": "ATT", "preferred": [Position.STRIKER, Position.CENTRAL_FORWARD], "row": 1, "col": 0},
        {"slot_id": "RST", "name": "Środkowy Napastnik", "short_pos": "ST", "category": "ATT", "preferred": [Position.STRIKER, Position.CENTRAL_FORWARD], "row": 1, "col": 1},
    ],
    "3-4-3": [
        {"slot_id": "GK", "name": "Bramkarz", "short_pos": "GK", "category": "GK", "preferred": [Position.GOALKEEPER], "row": 4, "col": 2},
        {"slot_id": "LCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK, Position.LEFT_BACK], "row": 3, "col": 0},
        {"slot_id": "CCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK], "row": 3, "col": 1},
        {"slot_id": "RCB", "name": "Środkowy Obrońca", "short_pos": "CB", "category": "DEF", "preferred": [Position.CENTRE_BACK, Position.RIGHT_BACK], "row": 3, "col": 2},
        {"slot_id": "LM", "name": "Lewy Pomocnik", "short_pos": "LM", "category": "MID", "preferred": [Position.LEFT_MIDFIELDER, Position.LEFT_WING_BACK, Position.LEFT_WING], "row": 2, "col": 0},
        {"slot_id": "LCM", "name": "Defensywny Pomocnik", "short_pos": "CDM", "category": "MID", "preferred": [Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER], "row": 2, "col": 1},
        {"slot_id": "RCM", "name": "Środkowy Pomocnik", "short_pos": "CM", "category": "MID", "preferred": [Position.CENTRAL_MIDFIELDER, Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER], "row": 2, "col": 2},
        {"slot_id": "RM", "name": "Prawy Pomocnik", "short_pos": "RM", "category": "MID", "preferred": [Position.RIGHT_MIDFIELDER, Position.RIGHT_WING_BACK, Position.RIGHT_WING], "row": 2, "col": 3},
        {"slot_id": "LW", "name": "Lewy Skrzydłowy", "short_pos": "LW", "category": "ATT", "preferred": [Position.LEFT_WING], "row": 1, "col": 0},
        {"slot_id": "ST", "name": "Środkowy Napastnik", "short_pos": "ST", "category": "ATT", "preferred": [Position.STRIKER, Position.CENTRAL_FORWARD], "row": 1, "col": 1},
        {"slot_id": "RW", "name": "Prawy Skrzydłowy", "short_pos": "RW", "category": "ATT", "preferred": [Position.RIGHT_WING], "row": 1, "col": 2},
    ],
}

ALL_DEF_POSITIONS = {Position.LEFT_BACK, Position.CENTRE_BACK, Position.RIGHT_BACK, Position.LEFT_WING_BACK, Position.RIGHT_WING_BACK}
ALL_MID_POSITIONS = {Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER, Position.CENTRAL_ATTACKING_MIDFIELDER, Position.LEFT_MIDFIELDER, Position.RIGHT_MIDFIELDER}
ALL_ATT_POSITIONS = {Position.LEFT_WING, Position.RIGHT_WING, Position.STRIKER, Position.CENTRAL_FORWARD}

def get_category_for_position(pos: Position) -> str:
    if pos == Position.GOALKEEPER:
        return "GK"
    if pos in ALL_DEF_POSITIONS:
        return "DEF"
    if pos in ALL_MID_POSITIONS:
        return "MID"
    if pos in ALL_ATT_POSITIONS:
        return "ATT"
    return "MID"


@dataclass
class RoundCandidate:
    player_obj: Player
    player_name: str
    full_name: str
    short_name: str
    team_name: str
    position_enum: Position
    position_str: str
    rating: float
    goals: int
    assists: int
    passes: int
    yellow_cards: int
    has_red_card: bool
    clean_sheet: bool
    is_motm: bool
    overall: int
    age: int
    nationality: str
    minutes_played: int
    matches_played: int = 1
    clean_sheets: int = 0
    saves: int = 0
    is_season: bool = False
    total_rounds_played: int = 1
    motm_awards_count: int = 0

    @property
    def composite_score(self) -> float:
        if not self.is_season:
            # Single round match performance
            score = self.rating * 100.0
            score += self.goals * 24.0
            score += self.assists * 17.0
            if self.is_motm:
                score += 15.0

            # Clean sheet bonus for defensive positions (GK, Defenders, and CDMs!)
            if self.clean_sheet and self.position_enum in (
                Position.GOALKEEPER, Position.CENTRE_BACK, Position.LEFT_BACK, Position.RIGHT_BACK,
                Position.LEFT_WING_BACK, Position.RIGHT_WING_BACK, Position.CENTRAL_DEFENSIVE_MIDFIELDER
            ):
                score += 12.0

            # Midfield workrate, passing volume & defensive control (CM & CDM)
            if self.position_enum == Position.CENTRAL_DEFENSIVE_MIDFIELDER:
                score += (self.passes * 0.25)
                score += 12.0
            elif self.position_enum == Position.CENTRAL_MIDFIELDER:
                score += (self.passes * 0.20)
                score += 8.0
            else:
                score += (self.passes * 0.10)

            score += (self.overall * 0.05)
            if self.has_red_card:
                score -= 50.0
            return round(score, 2)
        else:
            # Full Season (TOTS) performance evaluation:
            # Regularize average rating using Bayesian shrinkage towards 6.0 based on matches played
            rounds = max(1, self.total_rounds_played)
            m0 = max(2.0, min(8.0, rounds * 0.25))
            m = max(1, self.matches_played)

            # Bayesian smoothed rating to prevent small sample size bias
            bayesian_rating = (m * self.rating + m0 * 6.0) / (m + m0)

            # Appearance ratio (reward consistent starters across all matches)
            appearance_ratio = min(1.0, m / rounds)

            score = bayesian_rating * 100.0
            score += appearance_ratio * 60.0
            score += self.goals * 22.0
            score += self.assists * 16.0
            score += self.motm_awards_count * 20.0

            # Defensive clean sheets (including CDMs!)
            if self.position_enum in (
                Position.GOALKEEPER, Position.CENTRE_BACK, Position.LEFT_BACK, Position.RIGHT_BACK,
                Position.LEFT_WING_BACK, Position.RIGHT_WING_BACK, Position.CENTRAL_DEFENSIVE_MIDFIELDER
            ):
                score += self.clean_sheets * 12.0

            if self.position_enum == Position.CENTRAL_DEFENSIVE_MIDFIELDER:
                score += (self.passes / max(1, self.matches_played)) * 0.45
                score += 12.0
            elif self.position_enum == Position.CENTRAL_MIDFIELDER:
                score += (self.passes / max(1, self.matches_played)) * 0.35
                score += 8.0

            score += (self.minutes_played / 90.0) * 3.0
            score += self.overall * 0.05
            if self.has_red_card:
                score -= 30.0

            return round(score, 2)


def extract_round_candidates(fixtures: list[Match], round_number: int, matches_per_round: int) -> list[RoundCandidate]:
    if not fixtures or matches_per_round <= 0:
        return []

    start_idx = (round_number - 1) * matches_per_round
    end_idx = min(len(fixtures), round_number * matches_per_round)
    if start_idx >= len(fixtures) or start_idx < 0:
        return []

    round_matches = fixtures[start_idx:end_idx]
    candidates: list[RoundCandidate] = []

    for match in round_matches:
        if not getattr(match, "is_finished", False):
            continue

        motm = getattr(match, "man_of_the_match", None)

        for match_team, opp_score in [
            (match.home_team, match.away_score),
            (match.away_team, match.home_score),
        ]:
            team_name = getattr(getattr(match_team, "team", match_team), "name", "Brak drużyny")
            clean_sheet = (opp_score == 0)
            played_players = getattr(match_team, "played_players", set())

            for mp in match_team.match_players:
                has_played = mp.is_starter or mp.minutes_played > 0 or mp in played_players
                if not has_played:
                    continue

                act_player = getattr(mp, "player", mp)
                # Primary natural position of player is always authoritative
                pos_enum = getattr(act_player, "position", getattr(mp, "assigned_position", Position.CENTRAL_MIDFIELDER))
                is_motm = (motm is not None and (motm == mp or getattr(motm, "player", None) == act_player))

                saves = getattr(match_team.stats, "saves", 0) if isinstance(act_player, Goalkeeper) else 0

                candidates.append(RoundCandidate(
                    player_obj=act_player,
                    player_name=mp.name,
                    full_name=mp.full_name,
                    short_name=mp.short_name,
                    team_name=team_name,
                    position_enum=pos_enum,
                    position_str=pos_enum.name if hasattr(pos_enum, "name") else str(pos_enum),
                    rating=round(float(getattr(mp, "rating", 6.0)), 2),
                    goals=int(getattr(mp, "goals", 0)),
                    assists=int(getattr(mp, "assists", 0)),
                    passes=int(getattr(mp, "passes", 0)),
                    yellow_cards=int(getattr(mp, "yellow_cards", getattr(mp, "yellow_card", 0))),
                    has_red_card=bool(getattr(mp, "has_red_card", False)),
                    clean_sheet=clean_sheet,
                    is_motm=is_motm,
                    overall=int(getattr(mp, "overall", 50)),
                    age=int(getattr(mp, "age", 20)),
                    nationality=str(getattr(mp, "nationality", "Unknown")),
                    minutes_played=int(getattr(mp, "minutes_played", 0)),
                    matches_played=1,
                    clean_sheets=1 if (clean_sheet and isinstance(act_player, Goalkeeper)) else 0,
                    saves=saves,
                    is_season=False,
                    total_rounds_played=1,
                    motm_awards_count=1 if is_motm else 0
                ))

    return candidates


def extract_season_candidates(player_stats: dict[Player, PlayerSeasonStats], min_matches: int = 1, total_rounds_played: int = 1) -> list[RoundCandidate]:
    candidates: list[RoundCandidate] = []

    for player_obj, stats in player_stats.items():
        if stats.matches_played < min_matches:
            continue

        pos_enum = getattr(player_obj, "position", Position.CENTRAL_MIDFIELDER)
        avg_rating = stats.average_rating

        cand = RoundCandidate(
            player_obj=player_obj,
            player_name=stats.player_name,
            full_name=stats.full_name,
            short_name=stats.short_name,
            team_name=stats.team_name or "Brak drużyny",
            position_enum=pos_enum,
            position_str=pos_enum.name if hasattr(pos_enum, "name") else str(pos_enum),
            rating=avg_rating,
            goals=stats.goals,
            assists=stats.assists,
            passes=stats.passes,
            yellow_cards=stats.yellow_cards,
            has_red_card=(stats.red_cards > 0),
            clean_sheet=(stats.clean_sheets > 0),
            is_motm=(stats.motm_awards > 0),
            overall=stats.overall,
            age=stats.age,
            nationality=stats.nationality,
            minutes_played=stats.minutes_played,
            matches_played=stats.matches_played,
            clean_sheets=stats.clean_sheets,
            saves=0,
            is_season=True,
            total_rounds_played=max(1, total_rounds_played),
            motm_awards_count=stats.motm_awards
        )
        candidates.append(cand)

    return candidates


def build_squad_selection(candidates: list[RoundCandidate], formation: str = "4-3-3") -> dict:
    if formation not in SUPPORTED_FORMATIONS:
        formation = "4-3-3"

    slot_templates = SUPPORTED_FORMATIONS[formation]

    # Sort candidates by composite_score descending
    sorted_candidates = sorted(
        candidates,
        key=lambda c: (c.composite_score, c.rating, c.goals, c.assists, c.overall),
        reverse=True
    )

    assigned_player_ids = set()
    starting_xi_map: dict[str, tuple[dict, RoundCandidate]] = {}

    # Map candidate to dict representation
    def candidate_to_dict(cand: RoundCandidate, slot_info: dict, is_bench: bool = False, is_mvp: bool = False) -> dict:
        return {
            "player_name": cand.player_name,
            "full_name": cand.full_name,
            "short_name": cand.short_name,
            "team_name": cand.team_name,
            "position": cand.position_str,
            "slot_position": slot_info.get("short_pos", cand.position_str),
            "slot_id": slot_info.get("slot_id", "SUB"),
            "slot_name": slot_info.get("name", "Rezerwowy"),
            "grid_row": slot_info.get("row", 0),
            "grid_col": slot_info.get("col", 0),
            "category": slot_info.get("category", get_category_for_position(cand.position_enum)),
            "rating": cand.rating,
            "goals": cand.goals,
            "assists": cand.assists,
            "passes": cand.passes,
            "yellow_cards": cand.yellow_cards,
            "has_red_card": cand.has_red_card,
            "clean_sheet": cand.clean_sheet,
            "clean_sheets": cand.clean_sheets,
            "is_motm": cand.is_motm,
            "overall": cand.overall,
            "age": cand.age,
            "nationality": cand.nationality,
            "minutes_played": cand.minutes_played,
            "matches_played": cand.matches_played,
            "is_bench": is_bench,
            "is_mvp": is_mvp
        }

    # Group slots by category for strict category-isolated selection
    gk_slots = [s for s in slot_templates if s.get("category") == "GK"]
    def_slots = [s for s in slot_templates if s.get("category") == "DEF"]
    mid_slots = [s for s in slot_templates if s.get("category") == "MID"]
    att_slots = [s for s in slot_templates if s.get("category") == "ATT"]

    # 1. Fill GOALKEEPER slots (Strict GK category)
    for slot in gk_slots:
        gk_cands = [c for c in sorted_candidates if id(c.player_obj) not in assigned_player_ids and c.position_enum == Position.GOALKEEPER]
        if gk_cands:
            chosen = gk_cands[0]
            assigned_player_ids.add(id(chosen.player_obj))
            starting_xi_map[slot["slot_id"]] = (slot, chosen)

    # 2. Fill ATTACKER slots (Strict ATT category)
    # Give ST/LST/RST priority for pure Strikers first
    st_slots = [s for s in att_slots if "ST" in s.get("slot_id", "")]
    wing_slots = [s for s in att_slots if s not in st_slots]

    # 2a. Fill Central Striker slots with pure Strikers
    for slot in st_slots:
        preferred = slot.get("preferred", [Position.STRIKER, Position.CENTRAL_FORWARD])
        chosen = None
        for cand in sorted_candidates:
            if id(cand.player_obj) not in assigned_player_ids and cand.position_enum in preferred:
                chosen = cand
                break
        if chosen:
            assigned_player_ids.add(id(chosen.player_obj))
            starting_xi_map[slot["slot_id"]] = (slot, chosen)

    # 2b. Fill Wing Forward slots with Wingers (or best remaining Attackers)
    for slot in wing_slots:
        preferred = slot.get("preferred", [Position.LEFT_WING, Position.RIGHT_WING])
        chosen = None
        for cand in sorted_candidates:
            if id(cand.player_obj) not in assigned_player_ids and cand.position_enum in preferred:
                chosen = cand
                break
        if chosen:
            assigned_player_ids.add(id(chosen.player_obj))
            starting_xi_map[slot["slot_id"]] = (slot, chosen)

    # 2c. Fill any remaining unfilled ATT slots with remaining ATT category players
    for slot in att_slots:
        if slot["slot_id"] not in starting_xi_map:
            for cand in sorted_candidates:
                if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "ATT":
                    assigned_player_ids.add(id(cand.player_obj))
                    starting_xi_map[slot["slot_id"]] = (slot, cand)
                    break

    # 3. Fill MIDFIELDER slots (Strict MID category - balanced holding/defensive + central/offensive roles)
    # 3a. Holding / Defensive Midfield slots (CDM in 4-3-3, LDM/RDM in 4-2-3-1, LDM in 3-5-2, LCM in 3-4-3)
    holding_slots = [s for s in mid_slots if s.get("short_pos") == "CDM" or "DM" in s.get("slot_id", "")]
    for slot in holding_slots:
        # Step 1: Pure CENTRAL_DEFENSIVE_MIDFIELDER
        chosen = None
        for cand in sorted_candidates:
            if id(cand.player_obj) not in assigned_player_ids and cand.position_enum == Position.CENTRAL_DEFENSIVE_MIDFIELDER:
                chosen = cand
                break
        # Step 2: Fallback to defensive / central midfielder (CENTRAL_MIDFIELDER)
        if not chosen:
            for cand in sorted_candidates:
                if id(cand.player_obj) not in assigned_player_ids and cand.position_enum == Position.CENTRAL_MIDFIELDER:
                    chosen = cand
                    break
        # Step 3: Fallback to any remaining midfielder
        if not chosen:
            for cand in sorted_candidates:
                if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "MID":
                    chosen = cand
                    break
        if chosen:
            assigned_player_ids.add(id(chosen.player_obj))
            starting_xi_map[slot["slot_id"]] = (slot, chosen)

    # 3b. Offensive / Creative / Central Midfield slots (e.g. CAM, CM, LM, RM, LAM, RAM)
    remaining_mid_slots = [s for s in mid_slots if s["slot_id"] not in starting_xi_map]
    for slot in remaining_mid_slots:
        preferred = slot.get("preferred", [])
        chosen = None
        for cand in sorted_candidates:
            if id(cand.player_obj) not in assigned_player_ids and cand.position_enum in preferred:
                chosen = cand
                break
        if chosen:
            assigned_player_ids.add(id(chosen.player_obj))
            starting_xi_map[slot["slot_id"]] = (slot, chosen)

    # 3c. Fill any remaining unfilled MID slots with best remaining MID candidates
    for slot in mid_slots:
        if slot["slot_id"] not in starting_xi_map:
            for cand in sorted_candidates:
                if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "MID":
                    assigned_player_ids.add(id(cand.player_obj))
                    starting_xi_map[slot["slot_id"]] = (slot, cand)
                    break

    # 4. Fill DEFENDER slots (Strict DEF category)
    for slot in def_slots:
        preferred = slot.get("preferred", [])
        chosen = None
        for cand in sorted_candidates:
            if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "DEF" and cand.position_enum in preferred:
                chosen = cand
                break
        if chosen:
            assigned_player_ids.add(id(chosen.player_obj))
            starting_xi_map[slot["slot_id"]] = (slot, chosen)

    # 4b. Fill any remaining unfilled DEF slots with remaining DEF category players
    for slot in def_slots:
        if slot["slot_id"] not in starting_xi_map:
            for cand in sorted_candidates:
                if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "DEF":
                    assigned_player_ids.add(id(cand.player_obj))
                    starting_xi_map[slot["slot_id"]] = (slot, cand)
                    break

    # 5. Emergency fallback (only if fewer than 11 players in total exist in candidates)
    for slot in slot_templates:
        if slot["slot_id"] not in starting_xi_map:
            is_gk = (slot.get("category") == "GK")
            for cand in sorted_candidates:
                if id(cand.player_obj) not in assigned_player_ids:
                    if (is_gk and cand.position_enum == Position.GOALKEEPER) or (not is_gk and cand.position_enum != Position.GOALKEEPER):
                        assigned_player_ids.add(id(cand.player_obj))
                        starting_xi_map[slot["slot_id"]] = (slot, cand)
                        break

    # Identify MVP
    mvp_cand = None
    if sorted_candidates:
        mvp_cand = sorted_candidates[0]

    # Bench Selection: 7 Substitutes (1 GK, 2 DEF, 2 MID, 2 ATT)
    # Balanced distribution for MID bench (1 CDM/CM, 1 CAM/Wide MID if available)
    bench_players: list[dict] = []
    bench_index = 1

    # GK (1)
    for cand in sorted_candidates:
        if len([b for b in bench_players if b["category"] == "GK"]) >= 1:
            break
        if id(cand.player_obj) not in assigned_player_ids and cand.position_enum == Position.GOALKEEPER:
            assigned_player_ids.add(id(cand.player_obj))
            slot_info = {"slot_id": f"BENCH_{bench_index}", "name": "Bramkarz (Rez.)", "short_pos": "GK", "category": "GK", "row": 0, "col": 0}
            bench_players.append(candidate_to_dict(cand, slot_info, is_bench=True))
            bench_index += 1

    # DEF (2)
    def_picked = 0
    for cand in sorted_candidates:
        if def_picked >= 2:
            break
        if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "DEF":
            assigned_player_ids.add(id(cand.player_obj))
            slot_info = {"slot_id": f"BENCH_{bench_index}", "name": "Obrońca (Rez.)", "short_pos": "DEF", "category": "DEF", "row": 0, "col": 0}
            bench_players.append(candidate_to_dict(cand, slot_info, is_bench=True))
            bench_index += 1
            def_picked += 1

    # MID (2): Prioritize 1 CDM/CM and 1 CAM/Wide MID
    # 1. Central/Defensive MID
    for cand in sorted_candidates:
        if id(cand.player_obj) not in assigned_player_ids and cand.position_enum in (Position.CENTRAL_DEFENSIVE_MIDFIELDER, Position.CENTRAL_MIDFIELDER):
            assigned_player_ids.add(id(cand.player_obj))
            pos_label = "Def. Pomocnik (Rez.)" if cand.position_enum == Position.CENTRAL_DEFENSIVE_MIDFIELDER else "Pomocnik (Rez.)"
            slot_info = {"slot_id": f"BENCH_{bench_index}", "name": pos_label, "short_pos": "CDM" if cand.position_enum == Position.CENTRAL_DEFENSIVE_MIDFIELDER else "CM", "category": "MID", "row": 0, "col": 0}
            bench_players.append(candidate_to_dict(cand, slot_info, is_bench=True))
            bench_index += 1
            break

    # 2. Attacking/Wide MID or second MID
    mid_count = len([b for b in bench_players if b["category"] == "MID"])
    for cand in sorted_candidates:
        if mid_count >= 2:
            break
        if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "MID":
            assigned_player_ids.add(id(cand.player_obj))
            slot_info = {"slot_id": f"BENCH_{bench_index}", "name": "Pomocnik (Rez.)", "short_pos": "MID", "category": "MID", "row": 0, "col": 0}
            bench_players.append(candidate_to_dict(cand, slot_info, is_bench=True))
            bench_index += 1
            mid_count += 1

    # ATT (2)
    att_picked = 0
    for cand in sorted_candidates:
        if att_picked >= 2:
            break
        if id(cand.player_obj) not in assigned_player_ids and get_category_for_position(cand.position_enum) == "ATT":
            assigned_player_ids.add(id(cand.player_obj))
            slot_info = {"slot_id": f"BENCH_{bench_index}", "name": "Napastnik (Rez.)", "short_pos": "ATT", "category": "ATT", "row": 0, "col": 0}
            bench_players.append(candidate_to_dict(cand, slot_info, is_bench=True))
            bench_index += 1
            att_picked += 1

    # Fill remaining bench spots up to 7 if candidates available
    if len(bench_players) < 7:
        for cand in sorted_candidates:
            if len(bench_players) >= 7:
                break
            if id(cand.player_obj) not in assigned_player_ids:
                assigned_player_ids.add(id(cand.player_obj))
                cat = get_category_for_position(cand.position_enum)
                slot_info = {
                    "slot_id": f"BENCH_{bench_index}",
                    "name": f"{cat} (Rez.)",
                    "short_pos": cat,
                    "category": cat,
                    "row": 0,
                    "col": 0
                }
                bench_players.append(candidate_to_dict(cand, slot_info, is_bench=True))
                bench_index += 1

    # Format starting XI according to formation slot order
    formatted_starting_xi: list[dict] = []
    for slot in slot_templates:
        slot_id = slot.get("slot_id")
        if slot_id in starting_xi_map:
            slot_info, cand = starting_xi_map[slot_id]
            is_mvp = (mvp_cand is not None and id(cand.player_obj) == id(mvp_cand.player_obj))
            formatted_starting_xi.append(candidate_to_dict(cand, slot_info, is_bench=False, is_mvp=is_mvp))

    # Top Scorer in candidates
    top_scorer_cand = max(candidates, key=lambda c: (c.goals, c.rating), default=None) if candidates else None
    top_scorer_dict = candidate_to_dict(top_scorer_cand, {"slot_id": "AWD_GOAL", "name": "Najlepszy Strzelec", "short_pos": "ST"}) if (top_scorer_cand and top_scorer_cand.goals > 0) else None

    # Top Assister in candidates
    top_assister_cand = max(candidates, key=lambda c: (c.assists, c.rating), default=None) if candidates else None
    top_assister_dict = candidate_to_dict(top_assister_cand, {"slot_id": "AWD_AST", "name": "Najlepszy Asystent", "short_pos": "CAM"}) if (top_assister_cand and top_assister_cand.assists > 0) else None

    # Top Goalkeeper in candidates
    gk_cands = [c for c in candidates if c.position_enum == Position.GOALKEEPER]
    top_gk_cand = max(gk_cands, key=lambda c: (c.rating, c.clean_sheets, c.saves), default=None) if gk_cands else None
    top_gk_dict = candidate_to_dict(top_gk_cand, {"slot_id": "AWD_GK", "name": "Najlepszy Bramkarz", "short_pos": "GK"}) if top_gk_cand else None

    # Average rating of Starting XI
    if formatted_starting_xi:
        avg_rating = round(sum(p["rating"] for p in formatted_starting_xi) / len(formatted_starting_xi), 2)
    else:
        avg_rating = 0.0

    mvp_dict = candidate_to_dict(mvp_cand, {"slot_id": "MVP", "name": "Zawodnik Kolejki", "short_pos": mvp_cand.position_str}, is_mvp=True) if mvp_cand else None

    return {
        "starting_xi": formatted_starting_xi,
        "bench": bench_players,
        "mvp": mvp_dict,
        "top_scorer": top_scorer_dict,
        "top_assister": top_assister_dict,
        "top_goalkeeper": top_gk_dict,
        "average_rating": avg_rating
    }


def get_team_of_the_round(league: League, round_number: int, formation: str = "4-3-3") -> dict:
    if not league or not league.fixtures:
        return {
            "round_number": round_number,
            "total_rounds": 1,
            "formation": formation,
            "available_formations": list(SUPPORTED_FORMATIONS.keys()),
            "is_round_finished": False,
            "matches_played_in_round": 0,
            "total_matches_in_round": 0,
            "starting_xi": [],
            "bench": [],
            "mvp": None,
            "top_scorer": None,
            "top_assister": None,
            "top_goalkeeper": None,
            "best_team_name": None,
            "average_rating": 0.0
        }

    num_teams = len(league.teams)
    matches_per_round = max(1, num_teams // 2)
    total_rounds = max(1, len(league.fixtures) // matches_per_round)

    if round_number < 1:
        round_number = 1
    if round_number > total_rounds:
        round_number = total_rounds

    start_idx = (round_number - 1) * matches_per_round
    end_idx = min(len(league.fixtures), round_number * matches_per_round)
    round_matches = league.fixtures[start_idx:end_idx]

    total_in_round = len(round_matches)
    finished_in_round = sum(1 for m in round_matches if getattr(m, "is_finished", False))
    is_round_finished = (finished_in_round == total_in_round and total_in_round > 0)

    candidates = extract_round_candidates(league.fixtures, round_number, matches_per_round)
    squad_data = build_squad_selection(candidates, formation)

    # Best performing team in round (highest goal difference or team avg rating)
    best_team_name = None
    if candidates:
        team_ratings: dict[str, list[float]] = {}
        for c in candidates:
            team_ratings.setdefault(c.team_name, []).append(c.rating)
        best_team_name = max(team_ratings.keys(), key=lambda t: sum(team_ratings[t]) / len(team_ratings[t]))

    return {
        "round_number": round_number,
        "total_rounds": total_rounds,
        "formation": formation,
        "available_formations": list(SUPPORTED_FORMATIONS.keys()),
        "is_round_finished": is_round_finished,
        "matches_played_in_round": finished_in_round,
        "total_matches_in_round": total_in_round,
        "starting_xi": squad_data["starting_xi"],
        "bench": squad_data["bench"],
        "mvp": squad_data["mvp"],
        "top_scorer": squad_data["top_scorer"],
        "top_assister": squad_data["top_assister"],
        "top_goalkeeper": squad_data["top_goalkeeper"],
        "best_team_name": best_team_name,
        "average_rating": squad_data["average_rating"]
    }


def get_team_of_the_season(league: League, formation: str = "4-3-3", min_matches: int = 1) -> dict:
    if not league or not league.player_stats:
        return {
            "league_name": getattr(league, "name", "Liga"),
            "total_rounds": 1,
            "rounds_played": 0,
            "formation": formation,
            "available_formations": list(SUPPORTED_FORMATIONS.keys()),
            "is_season_finished": False,
            "starting_xi": [],
            "bench": [],
            "mvp": None,
            "top_scorer": None,
            "top_assister": None,
            "top_goalkeeper": None,
            "best_team_name": None,
            "average_rating": 0.0
        }

    num_teams = len(league.teams)
    matches_per_round = max(1, num_teams // 2)
    total_rounds = max(1, len(league.fixtures) // matches_per_round) if league.fixtures else 1

    total_fixtures = len(league.fixtures) if league.fixtures else 0
    finished_fixtures = sum(1 for m in league.fixtures if getattr(m, "is_finished", False)) if league.fixtures else 0
    is_season_finished = (finished_fixtures == total_fixtures and total_fixtures > 0)
    rounds_played = finished_fixtures // matches_per_round if matches_per_round > 0 else 0

    # Ensure all players from league teams are in player_stats with correct team_name
    for team_obj in league.teams:
        for player in team_obj.players:
            actual_player = getattr(player, 'player', player)
            if actual_player not in league.player_stats:
                league.player_stats[actual_player] = PlayerSeasonStats(actual_player, team_name=team_obj.name)
            elif not getattr(league.player_stats[actual_player], "team_name", None):
                league.player_stats[actual_player].team_name = team_obj.name

    # Dynamic match threshold: in mid/late season, players must have played a meaningful percentage of matches
    if min_matches is None or min_matches <= 1:
        if rounds_played >= 3:
            effective_min = max(2, int(rounds_played * 0.35))
        else:
            effective_min = 1
    else:
        effective_min = min_matches

    candidates = extract_season_candidates(league.player_stats, min_matches=effective_min, total_rounds_played=rounds_played)
    # If not enough candidates met the strict minimum matches, fall back to lower threshold
    if len(candidates) < 18 and effective_min > 1:
        candidates = extract_season_candidates(league.player_stats, min_matches=1, total_rounds_played=rounds_played)

    squad_data = build_squad_selection(candidates, formation)

    # Best team in the season: table leader / champion
    best_team_name = None
    if league.table:
        sorted_table = sorted(league.table.values(), key=lambda t: (-t.points, -t.goals_difference, -t.goals_scored))
        if sorted_table:
            best_team_name = sorted_table[0].team_name

    return {
        "league_name": getattr(league, "name", "Liga"),
        "total_rounds": total_rounds,
        "rounds_played": rounds_played,
        "formation": formation,
        "available_formations": list(SUPPORTED_FORMATIONS.keys()),
        "is_season_finished": is_season_finished,
        "starting_xi": squad_data["starting_xi"],
        "bench": squad_data["bench"],
        "mvp": squad_data["mvp"],
        "top_scorer": squad_data["top_scorer"],
        "top_assister": squad_data["top_assister"],
        "top_goalkeeper": squad_data["top_goalkeeper"],
        "best_team_name": best_team_name,
        "average_rating": squad_data["average_rating"]
    }
