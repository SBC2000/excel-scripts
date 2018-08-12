class FlatData:

    def __init__(self,
                 categories,
                 pools_by_category,
                 pool_info_by_pool,
                 referees,
                 pitches,
                 games_by_pitch,
                 sponsors,
                 referees_and_jury_by_game):
        """
        @type categories: list[str]
        @type pools_by_category: dict[str, (str, str)]
        @type pool_info_by_pool: dict[str, (str, list[str]]
        @type referees: list[str]
        @type pitches: list[str]
        @type games_by_pitch: dict[str, (str, str)]
        @type sponsors: list[tuple(str, str)]
        @type referees_and_jury_by_game: Dict[str, Dict[str, str]]
        @rtype: None
        """
        self.__categories = categories
        self.__pools_by_category = pools_by_category
        self.__pool_info_by_pool_abbr = pool_info_by_pool
        self.__referees = referees
        self.__pitches = pitches
        self.__games_by_pitch = games_by_pitch
        self.__sponsors = sponsors
        self.__referees_and_jury_by_game = referees_and_jury_by_game

    @property
    def categories(self):
        """
        @rtype: list[str]
        """
        return self.__categories

    def get_pools_by_category(self, category):
        """
        @type category: str
        @rtype: list[(str, str, str)]
        """
        return [
            (pool, abbr, self.__pool_info_by_pool_abbr[abbr][0])
            for pool, abbr in self.__pools_by_category[category]
        ]

    def get_teams_by_pool_abbr(self, pool_abbr):
        """
        @param pool_abbr: str
        @return: list[str]
        """
        return self.__pool_info_by_pool_abbr[pool_abbr][1]

    @property
    def referees(self):
        """
        @rtype: list[str]
        """
        return self.__referees

    @property
    def pitches(self):
        """
        @rtype: list[str]
        """
        return self.__pitches

    def get_games_by_pitch(self, pitch):
        """
        @type pitch: str
        @rtype: list[(str, str)]
        """
        return self.__games_by_pitch[pitch]

    @property
    def sponsors(self):
        """
        @rtype: list[str]
        """
        return self.__sponsors

    def get_referees_and_jury_by_game(self, game):
        """
        @type game: Game
        @rtype: Dict[str, str]
        """
        if game.name in self.__referees_and_jury_by_game:
            return self.__referees_and_jury_by_game[game.name]
        else:
            return {}
