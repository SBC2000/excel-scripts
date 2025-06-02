from itertools import groupby

from .excel_base import ExcelBase


class ExcelWriter(ExcelBase):
    def __init__(self, workbook):
        ExcelBase.__init__(self, workbook)

    def write_game_schedule(self, game_schedule):
        """
        @type game_schedule: GameSchedule
        @return: None
        """

        # the last pitch is special: it has a different timing scheme
        normal_pitches, special_pitches = game_schedule.pitches[:-1], [game_schedule.pitches[-1]]

        self.__write_game_schedule_for_pitches(self.schedule_sheet, normal_pitches, game_schedule)
        self.__write_game_schedule_for_pitches(self.schedule_pitch4_sheet, special_pitches, game_schedule)

    def __write_game_schedule_for_pitches(self, sheet, pitches, game_schedule):
        """
        Write the game schedule for the given pitches on the given sheet
        @type sheet: str
        @type pitches: list[Pitch]
        @type game_schedule: GameSchedule
        @return:
        """

        sorted_games = sorted([g for pitch in pitches for g in game_schedule.get_games_by_pitch(pitch)],
                              key=lambda g: g.datetime)
        games_by_datetime_by_pitch = [
            {game.pitch: game for game in games}
            for datetime, games in groupby(sorted_games, lambda g: g.datetime)
            ]

        header = ["Tijd"]
        for pitch in pitches:
            header.extend([pitch.name, "Wit", "Blauw", "Scheidsrechter 1", "Scheidsrechter 2", "Jury"])
        number_of_columns = 6

        previous_date = next(iter(games_by_datetime_by_pitch[0].values())).datetime

        matrix = [header]
        for game_by_pitch in games_by_datetime_by_pitch:
            current_date = next(iter(game_by_pitch.values())).datetime

            # add an empty line when the date changes
            if current_date.date() != previous_date.date():
                row = [""] * (1 + len(pitches) * number_of_columns)
                previous_date = current_date
                matrix.append(row)

            row = [current_date.strftime("%H:%M")]
            for pitch in pitches:
                if pitch in game_by_pitch:
                    game = game_by_pitch[pitch]
                    row.extend([game.name, game.get_home_team_name(), game.get_away_team_name(), "", "", ""])
                else:
                    row.extend([""] * number_of_columns)

            matrix.append(row)

        self._write_sheet(sheet, matrix)

    def write_colored_game_schedule(self, game_schedule):
        """
        Write the game schedule together with "before" and "after" gaps
        The actual coloring has to be done in Excel for the moment...
        @type game_schedule: GameSchedule
        @return: None
        """

        # the last pitch is special
        normal_pitches = game_schedule.pitches[0:-1]
        normal_games = [g for g in game_schedule.get_games_with_gaps() if g.game.pitch in normal_pitches]
        normal_games.sort(key=lambda g: (g.game.datetime, g.game.pitch.rank))

        normal_games_by_datetime = [
            {game.game.pitch: game for game in games}
            for datetime, games in groupby(normal_games, lambda g: g.game.datetime)
            ]

        header = ["Tijd"]
        for pitch in normal_pitches:
            header.extend([pitch.name, "Wit", "Blauw", "Voor", "Na"])

        matrix = [header]
        for game_by_pitch in normal_games_by_datetime:
            row = [next(iter(game_by_pitch.values())).game.datetime.strftime("%H:%M")]
            for pitch in normal_pitches:
                if pitch in game_by_pitch:
                    wrapper = game_by_pitch[pitch]
                    game = wrapper.game
                    row.extend([game.name, game.get_home_team_name(), game.get_away_team_name(),
                                str(wrapper.before), str(wrapper.after)])
                else:
                    row.extend(["", "", "", "", ""])

            matrix.append(row)

        self._write_sheet(self.schedule_sheet, matrix)

    def write_games_per_team(self, relevant_pools, game_schedule):
        """
        @type relevant_pools: list[Pool]
        @type game_schedule: GameSchedule
        @return:
        """
        matrix = []
        required_length = 12

        for pool in relevant_pools:
            pool_name = pool.name
            for team in pool.teams:
                row = [pool_name, team.name]
                pool_name = ""  # only show pool name in front of first team
                for game in sorted(game_schedule.get_games_by_team(team), key=lambda g: g.datetime):
                    row.extend([game.pitch.name, game.datetime.strftime("%H:%M")])

                # make sure that all rows have the same length by appending ""
                # and then taking the starting slice of the right size
                row.extend([""] * required_length)
                matrix.append(row[:required_length])

        self._write_sheet(self.games_per_team_sheet, matrix)

    def write_printable_game_schedule(self, game_schedule, pool_by_game):
        """
        @type game_schedule: GameSchedule
        @type pool_by_game: Dict[Game, Pool]
        @return:
        """

        # the last pitch is special: it has a different timing scheme
        normal_pitches, special_pitches = game_schedule.pitches[:-1], [game_schedule.pitches[-1]]

        normal_games = game_schedule.get_games_sorted_by_datetime(normal_pitches)
        normal_games_saturday = [game for game in normal_games if game.datetime.date() == game_schedule.dates[0]]
        normal_games_sunday = [game for game in normal_games if game.datetime.date() == game_schedule.dates[1]]
        special_games = game_schedule.get_games_sorted_by_datetime(special_pitches)

        self.__write_printable_game_schedule(self.printable_schedule_saturday_sheet, normal_games_saturday, pool_by_game)
        self.__write_printable_game_schedule(self.printable_schedule_sunday_sheet, normal_games_sunday, pool_by_game)
        self.__write_printable_game_schedule(self.printable_schedule_saturday_pitch4_sheet, special_games, pool_by_game)

    def __write_printable_game_schedule(self, sheet, games, pool_by_game):
        matrix = [["Tijd", "Veld", "Poule", "Wit", "", "Blauw", "Scheidsrechters", "Jury", "DW", "", "DB", "Id"]]

        alternate_colors = (None, (200, 200, 200))
        previous_color_index = 0
        previous_date_time = games[0].datetime

        colors = [alternate_colors[0]]

        for game in games:
            matrix.append([
                game.datetime.strftime("%H:%M"),
                game.pitch.name,
                pool_by_game[game].abbreviation,
                game.get_home_team_name(),
                "-",
                game.get_away_team_name(),
                game.get_referees_string(),
                game.jury,
                game.result.home_score if game.result else "",
                "-",
                game.result.away_score if game.result else "",
                game.name
            ])
            color_index = previous_color_index
            if game.datetime != previous_date_time:
                color_index = 1 - previous_color_index
                previous_date_time = game.datetime
                previous_color_index = color_index
            colors.append(alternate_colors[color_index])

        self._write_sheet(sheet, matrix, row_colors=colors)
