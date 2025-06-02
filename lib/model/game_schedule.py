from itertools import groupby


class GameSchedule:
    def __init__(self, games):
        self.__games = games
        self.__dates = self.__compute_dates(games)
        self.__games_by_pitch = self.__compute_games_by_pitch(games)
        self.__games_by_team = self.__compute_games_by_team(games)

    @property
    def dates(self):
        """
        Get all dates occurring in this schedule
        There are always exactly 2 dates
        @rtype: List[Date]
        """
        return self.__dates

    @property
    def games(self):
        return self.__games

    @property
    def pitches(self):
        return sorted(self.__games_by_pitch.keys(), key=lambda p: p.rank)

    def get_games_by_pitch(self, pitch):
        return self.__games_by_pitch[pitch]

    def get_games_by_team(self, team):
        return self.__games_by_team[team]

    def get_max_gap_by_team(self, team, start_time, end_time):
        games = filter(lambda g: g.datetime.date() == start_time.date(), self.get_games_by_team(team))
        times = [start_time] + sorted(map(lambda g: g.datetime, games)) + [end_time]
        gaps = [i - j for i, j in zip(times[1:], times)]
        return max(gaps)

    def get_games_with_gaps(self):
        sorted_games = sorted(self.__games, key=lambda g: g.datetime)
        start_time = sorted_games[0].datetime

        sorted_game_wrappers = [GameWrapper(game) for game in sorted_games if game.datetime.date() == start_time.date()]

        teams = self.__games_by_team.keys()

        last_time_by_team = {team: start_time for team in teams}

        for game_wrapper in sorted_game_wrappers:
            last_time = min(last_time_by_team[game_wrapper.game.home_team],
                            last_time_by_team[game_wrapper.game.away_team])
            game_wrapper.before = game_wrapper.game.datetime - last_time
            last_time_by_team[game_wrapper.game.home_team] = game_wrapper.game.datetime
            last_time_by_team[game_wrapper.game.away_team] = game_wrapper.game.datetime

        sorted_game_wrappers.sort(key=lambda g: g.game.datetime, reverse=True)
        end_time = sorted_game_wrappers[0].game.datetime

        last_time_by_team = {team: end_time for team in teams}

        for game_wrapper in sorted_game_wrappers:
            last_time = max(last_time_by_team[game_wrapper.game.home_team],
                            last_time_by_team[game_wrapper.game.away_team])
            game_wrapper.after = last_time - game_wrapper.game.datetime
            last_time_by_team[game_wrapper.game.home_team] = game_wrapper.game.datetime
            last_time_by_team[game_wrapper.game.away_team] = game_wrapper.game.datetime

        return sorted_game_wrappers

    def get_games_sorted_by_datetime(self, pitches):
        filtered_games = [game for game in self.__games if game.pitch in pitches]
        return sorted(filtered_games, key=lambda g: (g.datetime, g.pitch.rank))

    @classmethod
    def __compute_dates(cls, games):
        dates = set([game.datetime.date() for game in games])

        if len(dates) != 2:
            raise Exception("Invalid number of dates in schedule: " + len(dates))

        return sorted(dates)

    @classmethod
    def __compute_games_by_pitch(cls, games):
        games_sorted_by_pitch = sorted(games, key=lambda g: (g.pitch.rank, g.datetime))

        return {
            pitch: list(games) for pitch, games in groupby(games_sorted_by_pitch, lambda g: g.pitch)
            }

    @classmethod
    def __compute_games_by_team(cls, games):
        games_by_team = [(game.home_team, game) for game in games] + [(game.away_team, game) for game in games]
        return {
            team: list(map(lambda t: t[1], ts)) for team, ts in groupby(games_by_team, lambda t: t[0])
            }


class GameWrapper:
    def __init__(self, game):
        self.game = game
        self.before = None
        self.after = None
