import random 

from models import Team, Player


class Match:
    def __init__(self, home_team, away_team):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = 0
        self.away_score = 0
    
    def resolve_attack(self, attacking_team, defending_team):
        attacking_player = attacking_team.get_attacker()
        defending_player = defending_team.get_defender()

        attack_score = attacking_player.skill * random.randint(1,10)
        defence_score = defending_player.skill * random.randint(1,10)

        print(f"{attacking_player.name} VS {defending_player.name}")

        return attack_score > defence_score
        
    def ball_posseion(self):

        home_midfielder = self.home_team.get_midfielder()
        away_midfielder = self.away_team.get_midfielder()

        home_ball_possesion_chance = home_midfielder.skill * random.randint(1,10)
        away_ball_possesion_chance = away_midfielder.skill * random.randint(1,10)

        if home_ball_possesion_chance > away_ball_possesion_chance: 
            return self.home_team
        elif home_ball_possesion_chance < away_ball_possesion_chance:
            return  self.away_team
        else:
            return None
        
    def play_match(self, rounds):
        
        for minute in range(rounds):
            attacking_team = self.ball_posseion()
            defending_team = self.away_team if attacking_team is self.home_team else self.home_team
                
            if attacking_team is None:
                continue
            else:
                is_goal = self.resolve_attack(attacking_team, defending_team)
                if is_goal and attacking_team is self.home_team:
                    self.home_score += 1
                elif is_goal and attacking_team is self.away_team:
                    self.away_score +=1

    def show_score(self):
        print(f"{self.home_team.name}: {self.home_score}")
        print(f"{self.away_team.name}: {self.away_score}")