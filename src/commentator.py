from src.engine import Match

class Commentator:
    def __init__(self):
        pass

    def comment(self, match: Match) -> None:
        if len(match.match_events[-1]) > 0:
            print(match.match_events[-1])