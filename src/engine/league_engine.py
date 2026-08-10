import random
from src.models import League, LeagueTeamStats, MatchTeam, FORMATION_433, PlayerSeasonStats, get_formation_positions
from src.engine.engine import Match, MatchEngine, KickOff

class LeagueEngine:
    def __init__(self, league: League, match_engine: MatchEngine):
        self.league: League = league
        self.match_engine: MatchEngine = match_engine

    def generate_fixture(self, double_round: bool = False): 
        self.league.fixtures.clear()
        
        # Reset all player fitness levels to 100% (1.0) for the start of the season schedule
        for team in self.league.teams:
            if team:
                for player in team.players:
                    player.fitness = 1.0

        teams_list = list(self.league.teams)
        random.shuffle(teams_list)
        
        if len(teams_list) % 2 != 0:
            teams_list.append(None)

        number_of_teams = len(teams_list)
        leg1_rounds = []

        for i in range(0, number_of_teams - 1):
            round_matches = []
            for j in range(0, number_of_teams // 2):
                home_team = teams_list[j]
                away_team = teams_list[number_of_teams - 1 - j]
                if home_team is not None and away_team is not None:
                    if random.choice([True, False]):
                        home_team, away_team = away_team, home_team
                    home_form = get_formation_positions(getattr(home_team, "formation", "4-3-3"))
                    away_form = get_formation_positions(getattr(away_team, "formation", "4-3-3"))
                    home_mt = MatchTeam(home_team, home_form)
                    away_mt = MatchTeam(away_team, away_form)
                    round_matches.append(Match(home_mt, away_mt))
            
            random.shuffle(round_matches)
            leg1_rounds.append(round_matches)
    
            first_team = teams_list[0]
            rest_of_teams = teams_list[1:]
            rotate_rest = [rest_of_teams[-1]] + rest_of_teams[:-1]
            teams_list = [first_team] + rotate_rest

        random.shuffle(leg1_rounds)

        first_round_matches = []
        for r_matches in leg1_rounds:
            first_round_matches.extend(r_matches)

        second_round_matches = []
        if double_round:
            for r_matches in leg1_rounds:
                leg2_r_matches = []
                for match in r_matches:
                    old_home_team = match.home_team.team
                    old_away_team = match.away_team.team

                    new_home_form = get_formation_positions(getattr(old_away_team, "formation", "4-3-3"))
                    new_away_form = get_formation_positions(getattr(old_home_team, "formation", "4-3-3"))
                    new_home_mt = MatchTeam(old_away_team, new_home_form)
                    new_away_mt = MatchTeam(old_home_team, new_away_form)
                    new_match = Match(new_home_mt, new_away_mt)
                    leg2_r_matches.append(new_match)
                random.shuffle(leg2_r_matches)
                second_round_matches.extend(leg2_r_matches)

        # Reset player fitness and form at season start
        for team in self.league.teams:
            if team:
                for player in getattr(team, "players", []):
                    player.fitness = 1.0
                    player.form = 1.0

        self.league.fixtures = first_round_matches + second_round_matches
        
    def play_match(self, match: Match) -> None:
        # Re-select line-up right before kickoff using latest player fitness and form levels
        match.home_team = MatchTeam(match.home_team.team, match.home_team.formation)
        match.away_team = MatchTeam(match.away_team.team, match.away_team.formation)
        # Properly re-synchronize KickOff state with the refreshed home/away team instances
        match.current_state = KickOff(random.choice([match.home_team, match.away_team]))
        match.player_with_ball = None
        match.potential_assistant = None

        home_team = match.home_team
        away_team = match.away_team

        if hasattr(self.league, "table") and self.league.table:
            if home_team.team in self.league.table:
                home_team.form_modifier = self.league.table[home_team.team].form_modifier
            if away_team.team in self.league.table:
                away_team.form_modifier = self.league.table[away_team.team].form_modifier

        self.match_engine.play_match(match)

        # Update player fitness and rest recovery post-match
        for mt in (home_team, away_team):
            played_player_ids = set()
            for mp in mt.match_players:
                if mp in mt.played_players or mp.is_starter:
                    played_player_ids.add(id(mp.player))
                    # Minutes played scaling & physical attribute fatigue resistance
                    mins = getattr(mp, 'minutes_played', 90)
                    mins_ratio = min(1.0, max(0.1, mins / 90.0))
                    phys = getattr(mp.player, 'base_physical', getattr(mp.player, 'physical', 50))
                    phys_factor = 0.85 + (phys / 200.0)
                    
                    # Fatigue loss: between 0.04 and 0.08 per match start depending on minutes and physical
                    fatigue_loss = (0.04 + 0.05 * (1.0 - mp.current_stamina)) * mins_ratio / phys_factor
                    mp.player.fitness = max(0.68, round(mp.player.fitness - fatigue_loss, 3))
                else:
                    # Rested bench players who didn't play recover +16%
                    mp.player.fitness = min(1.0, round(mp.player.fitness + 0.16, 3))

            # Non-playing squad players recover fitness (+20%) and normalize form towards 1.0
            for p in mt.team.players:
                if id(p) not in played_player_ids:
                    p.fitness = min(1.0, round(p.fitness + 0.20, 3))
                    curr_f = getattr(p, "form", 1.0)
                    p.form = max(0.80, min(1.20, round((curr_f * 0.85) + (1.0 * 0.15), 3)))

        home_score = match.home_score
        away_score = match.away_score

        home_stats = self.league.table[home_team.team]
        home_stats.register_match_result(home_score, away_score)
        away_stats = self.league.table[away_team.team]
        away_stats.register_match_result(away_score, home_score)

        self.league.register_match_player_stats(match)
       
    def get_sorted_table(self) -> list[LeagueTeamStats]:
        return sorted(self.league.table.values(), key=lambda team: (-team.points, -team.goals_difference, -team.goals_scored))

    def get_top_scorers(self, limit: int = 10) -> list[PlayerSeasonStats]:
        return sorted(self.league.player_stats.values(), key=lambda stats: stats.goals, reverse=True)[:limit]

    def get_top_assists(self, limit: int = 10) -> list[PlayerSeasonStats]:
        return sorted(self.league.player_stats.values(), key=lambda stats: stats.assists, reverse=True)[:limit]

    def get_top_ratings(self, limit: int = 10, min_matches: int = 5) -> list[PlayerSeasonStats]:
        filtered = [s for s in self.league.player_stats.values() if s.matches_played > min_matches]
        if not filtered:
            filtered = [s for s in self.league.player_stats.values() if s.matches_played >= 1]
        return sorted(filtered, key=lambda stats: (stats.average_rating, stats.motm_awards, stats.goals), reverse=True)[:limit]

    def get_top_motm(self, limit: int = 10) -> list[PlayerSeasonStats]:
        return sorted(self.league.player_stats.values(), key=lambda stats: (stats.motm_awards, stats.average_rating), reverse=True)[:limit]

    def get_sorted_player_stats(self, sort_by: str = "goals") -> list[PlayerSeasonStats]:
        key_func = lambda stats: getattr(stats, sort_by, stats.goals)
        return sorted(self.league.player_stats.values(), key=key_func, reverse=True)

    def get_team_of_the_round(self, round_number: int, formation: str = "4-3-3") -> dict:
        from src.engine.team_of_the_round import get_team_of_the_round
        return get_team_of_the_round(self.league, round_number=round_number, formation=formation)

    def get_team_of_the_season(self, formation: str = "4-3-3", min_matches: int = 1) -> dict:
        from src.engine.team_of_the_round import get_team_of_the_season
        return get_team_of_the_season(self.league, formation=formation, min_matches=min_matches)