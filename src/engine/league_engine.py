import random
from src.models import League, LeagueTeamStats, MatchTeam, FORMATION_433, PlayerSeasonStats
from src.engine.engine import Match, MatchEngine

class LeagueEngine:
    def __init__(self, league: League, match_engine: MatchEngine):
        self.league: League = league
        self.match_engine: MatchEngine = match_engine

    def generate_fixture(self, double_round: bool = False): 
        self.league.fixtures.clear()
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
                    home_mt = MatchTeam(home_team, FORMATION_433)
                    away_mt = MatchTeam(away_team, FORMATION_433)
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

                    new_home_mt = MatchTeam(old_away_team, FORMATION_433)
                    new_away_mt = MatchTeam(old_home_team, FORMATION_433)
                    new_match = Match(new_home_mt, new_away_mt)
                    leg2_r_matches.append(new_match)
                random.shuffle(leg2_r_matches)
                second_round_matches.extend(leg2_r_matches)

        self.league.fixtures = first_round_matches + second_round_matches
        
    def play_match(self, match: Match) -> None:
        home_team = match.home_team
        away_team = match.away_team

        if self.league and home_team.team in self.league.table:
            home_team.form_modifier = self.league.table[home_team.team].form_modifier
        if self.league and away_team.team in self.league.table:
            away_team.form_modifier = self.league.table[away_team.team].form_modifier

        self.match_engine.play_match(match)

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

    def get_sorted_player_stats(self, sort_by: str = "goals") -> list[PlayerSeasonStats]:
        key_func = lambda stats: getattr(stats, sort_by, stats.goals)
        return sorted(self.league.player_stats.values(), key=key_func, reverse=True)