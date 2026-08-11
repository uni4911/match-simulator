import random
from src.models import League, LeagueTeamStats, MatchTeam, FORMATION_433, PlayerSeasonStats, get_formation_positions, Goalkeeper, Position
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

        # Reset player fitness, form, consecutive streaks, and suspensions at season start
        for team in self.league.teams:
            if team:
                for player in getattr(team, "players", []):
                    actual = getattr(player, "player", player)
                    actual.fitness = 1.0
                    actual.form = 1.0
                    actual.consecutive_matches_played = 0
                    actual.suspension_matches_remaining = 0

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

        # Update player fitness, consecutive streaks, and rest recovery post-match
        for mt in (home_team, away_team):
            played_player_ids = set()
            for mp in mt.match_players:
                if mp in mt.played_players or mp.is_starter:
                    played_player_ids.add(id(mp.player))
                    # Minutes played scaling & physical attribute fatigue resistance
                    mins = getattr(mp, 'minutes_played', 90)
                    mins_ratio = min(1.0, max(0.1, mins / 90.0))
                    phys = getattr(mp.player, 'base_physical', getattr(mp.player, 'physical', 50))
                    age = getattr(mp.player, 'age', 25)

                    # Update consecutive matches played streak
                    if mins >= 45:
                        mp.player.consecutive_matches_played = getattr(mp.player, "consecutive_matches_played", 0) + 1
                    else:
                        mp.player.consecutive_matches_played = max(0, getattr(mp.player, "consecutive_matches_played", 0) - 1)

                    consec = mp.player.consecutive_matches_played

                    # Physical attribute resistance to fatigue and consecutive workload
                    # High physical (85+) players resist consecutive match fatigue significantly
                    phys_factor = 0.85 + (phys / 180.0)
                    consec_fatigue_mult = 1.0 + max(0, consec - 2) * max(0.04, 0.22 - (phys / 450.0))

                    # Age recovery factor: Prime (22-29) = 1.0, Veterans (30+) recover slower, Young (<21) slight penalty
                    if age >= 30:
                        age_recovery_mult = max(0.70, 1.0 - (age - 29) * 0.035)
                    elif age < 21:
                        age_recovery_mult = 0.95 + (age - 17) * 0.012
                    else:
                        age_recovery_mult = 1.0

                    # Goalkeepers run much less and experience minimal in-match muscular fatigue
                    is_gk = isinstance(mp.player, Goalkeeper) or mp.assigned_position == Position.GOALKEEPER
                    gk_drain_mult = 0.20 if is_gk else 1.0

                    # Match fatigue loss based on in-game exhaustion, minutes played, and consecutive matches
                    fatigue_loss = (0.048 + 0.052 * (1.0 - mp.current_stamina)) * mins_ratio * consec_fatigue_mult * gk_drain_mult / phys_factor

                    # Inter-match recovery (rest period between weekly league matchdays)
                    weekly_recovery = (0.032 + 0.024 * (phys / 100.0)) * age_recovery_mult

                    net_fitness = mp.player.fitness - fatigue_loss + weekly_recovery
                    mp.player.fitness = max(0.68, min(1.0, round(net_fitness, 3)))
                else:
                    # Rested bench players who didn't play recover fitness & reset consecutive streak
                    mp.player.consecutive_matches_played = 0
                    mp.player.fitness = min(1.0, round(mp.player.fitness + 0.18, 3))

            # Non-playing squad players recover fitness (+20%), reset streaks, and form cools down towards 1.0
            for p in mt.team.players:
                actual = getattr(p, "player", p)
                if id(actual) not in played_player_ids:
                    actual.consecutive_matches_played = 0
                    actual.fitness = min(1.0, round(actual.fitness + 0.20, 3))
                    curr_f = getattr(actual, "form", 1.0)
                    actual.form = max(0.80, min(1.20, round((curr_f * 0.80) + (1.0 * 0.20), 3)))

            # Decrement suspension for banned players who served their match suspension in the stands
            for p in mt.team.players:
                actual = getattr(p, "player", p)
                if getattr(actual, "suspension_matches_remaining", 0) > 0 and id(actual) not in played_player_ids:
                    actual.suspension_matches_remaining -= 1

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
        return sorted(self.league.player_stats.values(), key=lambda stats: (stats.goals, stats.matches_played, stats.average_rating), reverse=True)[:limit]

    def get_top_assists(self, limit: int = 10) -> list[PlayerSeasonStats]:
        return sorted(self.league.player_stats.values(), key=lambda stats: (stats.assists, stats.matches_played, stats.average_rating), reverse=True)[:limit]

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