from enum import Enum
from .observable import Observable


class Pool(Observable):
    def __init__(self, factory, identifier, name, abbreviation, pool_type, rank):
        """
        @param factory: Factory
        @param identifier: str
        @param name: str
        @param abbreviation: str
        @param pool_type: PoolType
        @param rank: int
        @return:
        """
        super(Pool, self).__init__()

        self.id = identifier
        self.name = name
        self.abbreviation = abbreviation
        self.pool_type = pool_type
        self.rank = rank
        self.teams = []
        self.games = []
        self.finals = []
        self.rankings = []

        if pool_type in [PoolType.split_with_finals, PoolType.split_with_semi_finals]:
            pool_a = factory.create_pool(name + " A", abbreviation + "A", PoolType.single_round_robin)
            pool_b = factory.create_pool(name + " B", abbreviation + "B", PoolType.single_round_robin)

            pool_a.register(self)
            pool_b.register(self)

            self.sub_pools = [pool_a, pool_b]
        else:
            self.sub_pools = []

    def add_team(self, team):
        if self.sub_pools:
            smaller = 0 if len(self.sub_pools[0].teams) <= len(self.sub_pools[1].teams) else 1
            self.sub_pools[smaller].add_team(team)
        else:
            self.teams.append(team)

    @property
    def all_teams(self):
        return self.teams + list(t for sp in self.sub_pools for t in sp.teams)

    @property
    def own_games(self):
        """
        Return all games of this pool, both normal and finals
        @return:
        """
        return sorted(self.games + self.finals, key=lambda g: (g.datetime, g.pitch.rank))

    @property
    def all_games(self):
        """
        Return all games of this pool, normal, finals, and subpools
        @return:
        """
        return sorted(self.games + list(g for sp in self.sub_pools for g in sp.games) + self.finals,
                      key=lambda g: (g.datetime, g.pitch.rank))

    def all_pool_games(self):
        return sorted(self.games + list(g for sp in self.sub_pools for g in sp.games),
                      key=lambda g: (g.datetime, g.pitch.rank))

    def add_pool_game(self, game):
        if self.sub_pools:
            home_sub_pool = 0 if game.home_team in self.sub_pools[0].teams else \
                1 if game.home_team in self.sub_pools[1].teams else -1
            away_sub_pool = 0 if game.away_team in self.sub_pools[0].teams else \
                1 if game.away_team in self.sub_pools[1].teams else -1

            if home_sub_pool == -1 or away_sub_pool == -1 or home_sub_pool != away_sub_pool:
                raise Exception("Both teams of a game must come from the same subpool!")

            self.sub_pools[home_sub_pool].add_pool_game(game)
            game.name = "{0}-{1:02d}".format(self.sub_pools[home_sub_pool].abbreviation,
                                             len(self.sub_pools[home_sub_pool].games))
        else:
            self.games.append(game)
            game.name = "{0}-{1:02d}".format(self.abbreviation, len(self.games))

        game.register(self)

    def add_finals_game(self, game):
        self.finals.append(game)
        game.name = "{0}F-{1:02d}".format(self.abbreviation, len(self.finals))

        game.register(self)

    def update(self):
        """
        Compute the ranking of this pool when all results are there.
        Otherwise, do nothing
        @return:
        """
        if self.games and all(game.result for game in self.games):
            self.rankings = self.compute_ranking()
            self.update_observers()

        if self.finals:
            for final in self.finals:
                final.update()

    def compute_ranking(self):
        team_results = {team: (0, 0, 0) for team in self.teams}
        for game in (game for game in self.games if game.result):
            team_results[game.home_team] = tuple(map(lambda x, y: x + y,
                                                     team_results[game.home_team],
                                                     game.result.get_home_score()))
            team_results[game.away_team] = tuple(map(lambda x, y: x + y,
                                                     team_results[game.away_team],
                                                     game.result.get_away_score()))

        # add all results together (points, goal +, goal -)
        # sort by point, saldo, goal +, name
        return sorted(((team,) + results for team, results in team_results.items()),
                      key=lambda t: (-t[1], t[3] - t[2], -t[2], t[0].name))

    def get_ranked_team(self, rank):
        return self.rankings[rank - 1][0] if self.rankings else None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return other and self.id == other.id

    def to_json(self, category):
        """
        Convert to a json string as needed by the app
        @type category: Category
        @return: str
        """
        return "{{\"id\": {0}, " \
               "\"name\": \"{1}\", " \
               "\"abbreviation\": \"{2}\", " \
               "\"category\": {3}, " \
               "\"rank\": {4}}}".format(self.id, self.name, self.abbreviation, category.id, self.rank)


class PoolType(Enum):
    single_round_robin = 1
    full_round_robin = 2
    split_with_finals = 3
    split_with_semi_finals = 4
    full_with_semi_finals = 5
    full_with_finals = 6
    partial_round_robin = 7
