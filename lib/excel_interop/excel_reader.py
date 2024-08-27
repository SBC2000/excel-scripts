import re

from excel_base import ExcelBase
from lib.common.flat_data import FlatData
from lib.model.game_result import GameResult


class ExcelReader(ExcelBase):
    def __init__(self, workbook):
        ExcelBase.__init__(self, workbook)

    def read(self):
        categories, pools = self.__read_categories_and_pools()
        pool_info = self.__read_pool_infos()
        referees = self.__read_referees()
        pitches, games = self.__read_pitches_and_games()
        sponsors = self.__read_sponsors()
        referees_and_juries_by_game = self.__read_referees_and_jury(pitches)

        return FlatData(categories, pools, pool_info, referees, pitches, games, sponsors, referees_and_juries_by_game)

    def __read_referees_and_jury(self, pitches):
        """
        @type pitches:
        @rtype: Dict[str, Dict[str, str]]
        """
        result = {}
        try:
            all_columns = self._load_sheet(self.schedule_sheet) + self._load_sheet(self.schedule_pitch4_sheet)

            for pitch in pitches:
                result.update(self.__read_referees_and_jury_for_pitch(pitch, all_columns))
        finally:
            return result

    @staticmethod
    def __read_referees_and_jury_for_pitch(pitch, all_columns):
        """
        @type pitch: str
        @type all_columns: List[Tuple[str, List[str]]]
        @rtype: Dict[str, Dict[str, str]]
        """
        result = {}

        ids = []
        referees1 = []
        referees2 = []
        juries = []
        for column in all_columns:
            if ids:
                if column[0] == "Scheidsrechter 1":
                    referees1 = column[1]
                elif column[0] == "Scheidsrechter 2":
                    referees2 = column[1]
                elif column[0] == "Jury":
                    juries = column[1]

                    # warning: assuming very strict column ordering here!!
                    break
            elif column[0] == pitch:
                ids = column[1]

        for game_id, referee1, referee2, jury in map(None, ids, referees1, referees2, juries):
            if game_id:
                result[game_id] = {"referee1": referee1, "referee2": referee2, "jury": jury}

        return result

    def __read_categories_and_pools(self):
        categories = []
        pools_by_category = {}
        for h, v in self._load_sheet(self.pools_sheet):
            if h in pools_by_category:
                raise Exception("Duplicate header " + h)

            categories.append(h)
            pools = []
            for p in v:
                m = re.search('(.*) \((.*)\)', p)
                pool, abbreviation = m.group(1), m.group(2)
                pools.append((pool, abbreviation))
            pools_by_category[h] = pools
        return categories, pools_by_category

    def __read_pool_infos(self):
        result = {}
        for h, v in self._load_sheet(self.teams_sheet):
            if h in result:
                raise Exception("Duplicate header " + h)
            result[h] = (self.__convert_pool_type(v[0]), v[1:])
        return result

    @staticmethod
    def __convert_pool_type(pool_type):
        if pool_type == "Halve competitie":
            return "SRR"
        elif pool_type == "Hele competitie":
            return "FRR"
        elif pool_type == "Splits met halve finales":
            return "SWSF"
        elif pool_type == "Splits met finales":
            return "SWF"
        elif pool_type == "Poule met halve finales":
            return "FWSF"
        elif pool_type == "Poule met finales":
            return "FWF"
        elif pool_type == "Gedeeltelijke competitie":
            return "PRR"
        else:
            raise Exception("Unexpected pool type " + pool_type)

    def __read_referees(self):
        """
        @rtype: list[str]
        """
        return self._load_sheet(self.referees_sheet)[0][1]

    def __read_sponsors(self):
        columns = self._load_sheet(self.sponsors_sheet)

        names = []
        uris = []

        for column in columns:
            if column[0] == "Naam":
                names = column[1]
            elif column[0] == "Website":
                uris = column[1]

        return zip(names, uris)

    def __read_pitches_and_games(self):
        pitches = []
        games_by_pitch = {}
        timestamps = []
        for h, c in self._load_sheet(self.games_sheet):
            if h == "Tijd":
                timestamps = c
            else:
                if h in games_by_pitch:
                    raise Exception("Duplicate header " + h)
                if not timestamps:
                    raise Exception("Expected header 'Tijd' not found")
                pitches.append(h)
                games_by_pitch[h] = zip(timestamps, c)

        return pitches, games_by_pitch

    def load_results(self):
        result = {}
        result.update(self.__load_results(self.printable_schedule_saturday_sheet))
        result.update(self.__load_results(self.printable_schedule_saturday_pitch4_sheet))
        result.update(self.__load_results(self.printable_schedule_sunday_sheet))

        return result

    def load_referees_and_juries(self):
        result = {}
        result.update(self.__load_referees_and_juries(self.printable_schedule_saturday_sheet))
        result.update(self.__load_referees_and_juries(self.printable_schedule_saturday_pitch4_sheet))
        result.update(self.__load_referees_and_juries(self.printable_schedule_sunday_sheet))

        return result

    def __load_results(self, sheet):
        sheet_dict = {column[0]: column[1] for column in self._load_sheet(sheet)}

        return {game_id: GameResult(home, away)
                for game_id, home, away in zip(sheet_dict["Id"], sheet_dict["DW"], sheet_dict["DB"])
                if home is not None and away is not None}

    def __load_referees_and_juries(self, sheet):
        sheet_dict = {column[0]: column[1] for column in self._load_sheet(sheet)}

        return {game_id: {"referees": referees if referees else "", "jury": jury}
                for game_id, referees, jury
                in map(None, sheet_dict["Id"], sheet_dict["Scheidsrechters"], sheet_dict["Jury"])}
