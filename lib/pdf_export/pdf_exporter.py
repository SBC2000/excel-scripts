import os

import pdfkit

from html_generator import HtmlGenerator
from lib.model.game import RankGame, ResultGame
from lib.model.pool import PoolType
from lib.model.game_schedule import GameSchedule


class PdfExporter:
    def __init__(self):
        self.generator = HtmlGenerator()

    def export_rankings(self, pools, page_layout=None):
        file_name = "Standen.pdf"

        ordered_pools = self.__order_pools(pools, page_layout) if page_layout else self.__get_default_pool_order(pools)

        body = self.__create_rankings_body(ordered_pools)
        html = self.__create_html(body)

        pdfkit.from_string(html, file_name, options={"quiet": ""})
        os.startfile(file_name, 'open')

    def export_schedule(self, game_schedule, export_saturday, export_sunday):
        file_name = "Schema.pdf"

        body = self.__create_schedule_body(game_schedule, export_saturday, export_sunday)
        html = self.__create_html(body)

        pdfkit.from_string(html, file_name, options={"quiet": ""})
        os.startfile(file_name, 'open')

    def __create_rankings_body(self, ordered_pools):
        """
        @type ordered_pools: list[list[Pool]]
        @rtype: str
        """
        return self.__create_page_separator().join(
            [self.__create_pool_separator().join(
                ["<h1>{0}<h1>{1}{2}".format(pool.name,
                                            self.__create_pool_tables(pool),
                                            self.__create_finals(pool))
                 for pool in pools]
            ) for pools in ordered_pools]
        )

    def __create_pool_tables(self, pool):
        result = ""
        for sub_pool in (pool.sub_pools if pool.sub_pools else [pool]):
            if sub_pool != pool:
                result += "<h2>{0}</h2>".format(sub_pool.name)

            table = self.__create_rankings_table(sub_pool.compute_ranking(), sub_pool.games)

            table_width = len(iter(table).next())
            column_info = {"width": [15, 150] + [40] * (table_width - 6) + [26] * 4,
                           "header-alignment": ["center", "left"] + ["center"] * (table_width - 2),
                           "content-alignment": ["center", "left"] + ["center"] * (table_width - 2),
                           "color": ["white"] * (table_width - 4) + ["lightgray"] + ["white"] * 3}
            result += self.generator.create_html_table(table, column_info, True, True)

        return result

    def __create_finals(self, pool):
        """
        @type pool: Pool
        @rtype: str
        """

        # warning: this does probably not scale well for generic pool formats!!
        if pool.pool_type in [PoolType.full_with_semi_finals, PoolType.split_with_semi_finals]:
            cross_finals = [final for final in pool.finals if isinstance(final, RankGame)]
            finals = [final for final in pool.finals if isinstance(final, ResultGame)]
        else:
            cross_finals = []
            finals = [final for final in pool.finals if isinstance(final, RankGame)]

        result = ""

        if cross_finals:
            result += "<h2>{0}</h2>".format("Kruisfinales")
            result += self.__create_finals_table(cross_finals)

        numbered_finals = zip(range(1, 2 * len(finals), 2), reversed(finals))
        for i, final in numbered_finals:
            result += "<h2>Om plaats {0} / {1}</h2>".format(i, i + 1)
            result += self.__create_finals_table([final])

        return result

    def __create_schedule_body(self, game_schedule, export_saturday, export_sunday):
        """
        @type game_schedule: GameSchedule
        @type export_saturday: bool
        @type export_sunday: bool
        @return:
        """
        dates = [date for date, include in zip(game_schedule.dates, [export_saturday, export_sunday]) if include]

        return self.__create_page_separator() \
            .join(["<h1>{0} &#8211; {1}<h1>{2}".format(pitch.name,
                                                 "Zaterdag" if date == game_schedule.dates[0] else "Zondag",
                                                 self.__create_schedule_table(
                                                     [game for game in game_schedule.get_games_by_pitch(pitch) if
                                                      game.datetime.date() == date])
                                                 ) for date in dates for pitch in game_schedule.pitches])

    @staticmethod
    def __create_finals_table(finals):
        result = ""
        result += "<table class=\"finals\">"
        for final in finals:
            result += "<tr>"
            result += "<td width=\"160\" class=\"finals\">" + final.get_home_team_name() + "</td>"
            result += "<td width=\"10\" class=\"finals\">-</td>"
            result += "<td width=\"160\" class=\"finals\">" + final.get_away_team_name() + "</td>"
            result += "<td width=\"20\" class=\"finals\"></td>"
            result += "<td align=\"center\" width=\"20\" class=\"finals\">" + str(
                int(final.result.home_score)) if final.result else "" + "</td>"
            result += "<td align=\"center\" width=\"10\" class=\"finals\">" + "-" if final.result else "" + "</td>"
            result += "<td align=\"center\" width=\"20\" class=\"finals\">" + str(
                int(final.result.away_score)) if final.result else "" + "</td>"
            result += "</tr>"
        result += "</table>"

        return result

    @staticmethod
    def __create_pool_separator():
        return "<br/><br/>"

    @staticmethod
    def __create_page_separator():
        return "<div style=\"page-break-after:always !important;\"></div>"

    @staticmethod
    def __create_html(body):
        style = "<style>" \
                "body { font-family: Helvetica }" \
                "@page { size: a4 portrait, margin: 2cm } " \
                "h1, tr, td, th {-pdf-keep-with-next: true; }" \
                "table { border: 2pt solid black; " \
                "border-spacing: 0; border-collapse: collapse; }" \
                "td, th { border: 1pt solid black; padding: 2pt;}" \
                "th.rotate {  height: 160px; width: 40px; white-space: nowrap; }" \
                "th.rotate > div { -webkit-transform: rotate(270deg) }" \
                "th.rotate > div > span { position: absolute; left:-64px; top: -16px; padding: 5px 10px; }" \
                "table.finals, td.finals { border: 0pt }" \
                "</style>"

        return "<html><head>{0}</head><body>{1}</body></html>".format(style, body)

    @staticmethod
    def __create_rankings_table(ranking, games):
        """
        Ranking is a tuple of (Team, points, score+, score-) tuples.
        @type ranking: tuple(tuple(Team, int, int, int))
        @param games:
        @return:
        """
        games_by_teams = {(game.home_team, game.away_team): game for game in games}

        table = [["", ""] + [r[0].name for r in ranking] + ["Punten", "Doelpunten voor", "Doelpunten tegen", "Saldo"]]
        for i, r in enumerate(ranking):
            home_team = r[0]
            row = [i + 1, home_team.name]
            for o in ranking:
                away_team = o[0]
                game = games_by_teams.get((home_team, away_team))
                row.append("{0}-{1}".format(int(game.result.home_score), int(game.result.away_score))
                           if game and game.result else "")
            row.extend([int(r[1]), int(r[2]), int(r[3]), int(r[2] - r[3])])
            table.append(row)

        return table

    @staticmethod
    def __order_pools(pools, page_layout):
        pools_by_abbreviation = {pool.abbreviation: pool for pool in pools}
        return [[pools_by_abbreviation[abbreviation] for abbreviation in page] for page in page_layout]

    @staticmethod
    def __get_default_pool_order(pools):
        return [[pool] for pool in pools]

    @staticmethod
    def __create_schedule_table(games):
        table = [["Tijd", "Nr.", "Wit", "Blauw", "Uitslag", "Scheidsrechters", "Jury"]]
        for game in games:
            row = [
                game.datetime.strftime("%H:%M"),
                game.name,
                game.get_home_team_name(),
                game.get_away_team_name(),
                "{0} - {1}".format(int(game.result.home_score), int(game.result.away_score)) if game.result else "",
                game.get_referees_string(),
                game.jury if game.jury else "",
            ]
            table.append(row)

        column_info = {"width": [60, 60, 160, 160, 60, 160, 160],
                       "header-alignment": ["center", "center", "left", "left", "center", "left", "left"],
                       "content-alignment": ["center", "center", "left", "left", "center", "left", "left"],
                       "color": ["white"] * 7}
        return HtmlGenerator().create_html_table(table, column_info, True, False)
