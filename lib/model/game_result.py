class GameResult:
    def __init__(self, home_score, away_score):
        self.home_score = home_score
        self.away_score = away_score

    def get_home_score(self):
        points = 3 if self.home_score > self.away_score else \
            1 if self.home_score == self.away_score else 0
        return points, self.home_score, self.away_score

    def get_away_score(self):
        points = 3 if self.home_score < self.away_score else \
            1 if self.home_score == self.away_score else 0
        return points, self.away_score, self.home_score

    def __eq__(self, other):
        return other and (self.home_score, self.away_score) == (other.home_score, other.away_score)
