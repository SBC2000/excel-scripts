from observable import Observable
from pitch import Pitch
from team import Team


class Game(Observable):
    def __init__(self, identifier, pitch, datetime, home_team, away_team):
        """
        @type identifier: str
        @type pitch: Pitch
        @type datetime: Datetime
        @type home_team: Team
        @type away_team: Team
        @return:
        """
        super(Game, self).__init__()

        self.id = identifier
        self.pitch = pitch
        self.datetime = datetime
        self.home_team = home_team
        self.away_team = away_team
        self.result = None
        self.name = ""
        self.referee1 = None
        self.referee2 = None
        self.jury = ""

    def set_result(self, game_result):
        self.result = game_result
        self.update_observers()

    def get_winner(self):
        if self.result:
            return self.home_team if self.result.home_score > self.result.away_score else \
                self.away_team if self.result.home_score < self.result.away_score else None
        else:
            return None

    def get_loser(self):
        if self.result:
            return self.home_team if self.result.home_score < self.result.away_score else \
                self.away_team if self.result.home_score > self.result.away_score else None
        else:
            return None

    def get_home_team_name(self):
        return self.home_team.name

    def get_away_team_name(self):
        return self.away_team.name

    def get_referees_string(self):
        referees = [referee for referee in [self.referee1, self.referee2] if referee]
        if len(referees) == 0:
            return ""
        elif len(referees) == 1:
            return referees[0].get_first_name()
        else:
            return "{0} en {1}".format(referees[0].get_first_name(), referees[1].get_first_name())

    def to_json(self, pool):
        """
        Convert to a json string as needed by the app
        @type pool: Pool
        @rtype: str
        """

        # this is a little awkward but the app cannot deal with finals having the same id as pool games
        pool_id = pool.id if self not in pool.finals else -1

        return "{{\"id\": {0}, " \
               "\"field\": {1}, " \
               "\"date\": \"{2}\", " \
               "\"pool\": {3}, " \
               "\"poolAbbreviation\": \"{4}\", " \
               "\"homeTeam\": {5}, " \
               "\"homeTeamName\": \"{6}\", " \
               "\"awayTeam\": {7}, " \
               "\"awayTeamName\": \"{8}\", " \
               "\"referee1\": {9}, " \
               "\"referee1Name\": \"{10}\", " \
               "\"referee2\": {11}, " \
               "\"referee2Name\": \"{12}\"}}".format(self.id,
                                                     self.pitch.id,
                                                     self.datetime.strftime("%d-%m-%Y %H:%M:%S"),
                                                     pool_id,
                                                     pool.abbreviation,
                                                     self.home_team.id if self.home_team else -1,
                                                     self.get_home_team_name(),
                                                     self.away_team.id if self.away_team else -1,
                                                     self.get_away_team_name(),
                                                     self.referee1.id if self.referee1 else -1,
                                                     self.referee1.name if self.referee1 else "",
                                                     self.referee2.id if self.referee2 else -1,
                                                     self.referee2.name if self.referee2 else "")


class RankGame(Game):
    def __init__(self, identifier, pitch, datetime, home_pool, home_position, away_pool, away_position):
        super(RankGame, self).__init__(identifier, pitch, datetime, None, None)

        self.home_pool = home_pool
        self.home_position = home_position
        self.away_pool = away_pool
        self.away_position = away_position

        self.update()

    def update(self):
        self.home_team = self.home_pool.get_ranked_team(self.home_position)
        self.away_team = self.away_pool.get_ranked_team(self.away_position)

    def get_home_team_name(self):
        if self.home_team:
            return self.home_team.name
        else:
            return "Nr.{0} {1}".format(self.home_position, self.home_pool.abbreviation)

    def get_away_team_name(self):
        if self.away_team:
            return self.away_team.name
        else:
            return "Nr.{0} {1}".format(self.away_position, self.away_pool.abbreviation)


class ResultGame(Game):
    def __init__(self, identifier, pitch, datetime, home_game, home_type, away_game, away_type):
        super(ResultGame, self).__init__(identifier, pitch, datetime, None, None)

        self.home_game = home_game
        self.home_type = home_type
        self.away_game = away_game
        self.away_type = away_type

        self.update()

    def update(self):
        self.home_team = self.home_game.get_winner() if self.home_type == "W" else self.home_game.get_loser()
        self.away_team = self.away_game.get_winner() if self.away_type == "W" else self.away_game.get_loser()

    def get_home_team_name(self):
        if self.home_team:
            return self.home_team.name
        else:
            return self.home_type + ". " + self.home_game.name

    def get_away_team_name(self):
        if self.away_team:
            return self.away_team.name
        else:
            return self.away_type + ". " + self.away_game.name
