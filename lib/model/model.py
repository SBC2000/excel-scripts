class Model:
    def __init__(self):
        self.__categories = []
        self.__pitches = []
        self.__referees = []
        self.__game_schedule = None
        self.__sponsors = []

    @property
    def categories(self):
        """
        @rtype: list[Category]
        """
        return self.__categories

    def add_category(self, category):
        self.__categories.append(category)

    @property
    def pitches(self):
        """ 
        @return: list[Pitch]
        """
        return self.__pitches

    def add_pitch(self, pitch):
        self.__pitches.append(pitch)

    @property
    def pools(self):
        """
        @rtype: list[Pool]
        """
        return [pool for category in self.categories for pool in category.pools]

    @property
    def all_pools(self):
        """
        Return all pools, both main pools and sub pools
        @return:
        """
        return [pool for category in self.categories
                for main_pool in category.pools
                for pool in ([main_pool] + main_pool.sub_pools if main_pool.sub_pools else [main_pool])
                ]

    @property
    def relevant_pools(self):
        """
        Return pools or sub pools if a pool has those
        @return:
        """
        return [pool for category in self.categories
                for main_pool in category.pools
                for pool in (main_pool.sub_pools if main_pool.sub_pools else [main_pool])
                ]

    @property
    def teams(self):
        """
        @rtype: list[Team]
        """
        return [team for pool in self.pools for team in pool.all_teams]

    @property
    def referees(self):
        """
        @rtype: list[Referee]
        """
        return self.__referees

    def add_referee(self, referee):
        self.__referees.append(referee)

    @property
    def sponsors(self):
        """
        @rtype: list[Sponsor]
        """
        return self.__sponsors

    def add_sponsor(self, sponsor):
        self.__sponsors.append(sponsor)

    @property
    def game_schedule(self):
        """
        @rtype: GameSchedule
        """
        return self.__game_schedule

    @game_schedule.setter
    def game_schedule(self, value):
        self.__game_schedule = value

    @property
    def games(self):
        """
        @rtype: list[Game]
        """
        return [game for game in self.game_schedule.games]

    def get_json_database(self):
        """
        Get the database as needed by the app
        @rtype: str
        """
        category_by_pool = {pool: category
                            for category in self.categories
                            for main_pool in category.pools
                            for pool in (main_pool.sub_pools if main_pool.sub_pools else [main_pool])}
        pool_by_game = {game: pool
                        for pool in self.all_pools
                        for game in pool.own_games}

        return "\"categories\": [{0}], " \
               "\"pools\": [{1}]," \
               "\"teams\": [{2}], " \
               "\"fields\": [{3}]," \
               "\"referees\": [{4}]," \
               "\"games\": [{5}]".format(",".join(map(lambda c: c.to_json(), self.__categories)),
                                         ",".join(map(lambda p: p.to_json(category_by_pool[p]), self.relevant_pools)),
                                         ",".join(map(lambda t: t.to_json(), self.teams)),
                                         ",".join(map(lambda p: p.to_json(), self.pitches)),
                                         ",".join(map(lambda r: r.to_json(), self.referees)),
                                         ",".join(map(lambda g: g.to_json(pool_by_game[g]), self.games)))

    def get_json_sponsors(self):
        return "\"sponsors\": [{0}]".format(",".join(map(lambda s: s.to_json(), self.__sponsors)))

    def apply_new_game_results(self, all_game_results):
        """
        Update all games that have a new score
        Returns the new results (indexed by id, rather than name!) and a flag indicating
        that some final games are now known
        @type all_game_results: dict[str, GameResult]
        @rtype: tuple[dict[int, GameResult], boolean]
        """

        new_results = {}

        final_game_teams_before = [(game.get_home_team_name(), game.get_away_team_name())
                                   for pool in self.pools
                                   for game in pool.finals]

        for game in self.game_schedule.games:
            new_result = all_game_results.get(game.name, None)
            if game.result and not new_result:
                raise Exception("Cannot erase a result; not supported by app")
            elif game.result != new_result:
                game.set_result(new_result)
                new_results[game.id] = new_result

        final_game_teams_after = [(game.get_home_team_name(), game.get_away_team_name())
                                  for pool in self.pools
                                  for game in pool.finals]

        return new_results, final_game_teams_before != final_game_teams_after

    def apply_referees_and_juries(self, referees_and_juries):
        referees_have_changed = False
        juries_have_changed = False

        referees_by_first_name = {referee.get_first_name(): referee for referee in self.referees}

        for game in self.game_schedule.games:
            old_referees = ([game.referee1] if game.referee1 else []) + ([game.referee2] if game.referee2 else [])
            new_referees = [referees_by_first_name[name]
                            for name in referees_and_juries[game.name]["referees"].split(" ") if name and name != "en"]

            if old_referees != new_referees:
                new_referees += [None, None]
                game.referee1 = new_referees[0]
                game.referee2 = new_referees[1]
                referees_have_changed = True

            old_jury = game.jury
            new_jury = referees_and_juries[game.name]["jury"]

            if old_jury != new_jury:
                game.jury = new_jury
                juries_have_changed = True

        return referees_have_changed, juries_have_changed
