from lib.model.game import Game, RankGame, ResultGame
from lib.model.game_schedule import GameSchedule
from lib.model.pool import PoolType


class Scheduler:
    def __init__(self):
        pass

    def build_schedule(self, template_games):
        template_games_by_pool = self.__get_games_by_pool(template_games)

        all_games = []

        for pool in template_games_by_pool.keys():
            all_games.extend(self.__build_schedule_for_pool(pool, template_games_by_pool[pool]))

        return GameSchedule(all_games)

    @classmethod
    def __build_schedule_for_pool(cls, pool, template_games):
        """
        @param pool: Pool
        @param template_games: TemplateGame
        @return: list[Game]
        """
        pool_schedule = cls.__game_template[(len(pool.all_teams), pool.pool_type)]

        if len(template_games) != len(pool_schedule):
            raise Exception("Incorrect number of games for pool {0}. Expected: {1}, Got: {2}".format(
                pool.abbreviation, len(pool_schedule), len(template_games)
            ))

        all_pool_games = []

        for template_game, template in zip(template_games, pool_schedule):

            template_type, template_home, template_away = template

            if template_type == "Pool":
                game = cls.__create_pool_game(pool, template_game, template_home, template_away)
                pool.add_pool_game(game)
            else:
                if template_type == "Rank":
                    game = cls.__create_rank_game(pool, template_game, template_home, template_away)
                elif template[0] == "Result":
                    game = cls.__create_result_game(pool, template_game, template_home, template_away)
                else:
                    raise Exception("Unrecognized template type " + template[0])

                pool.add_finals_game(game)

            all_pool_games.append(game)

        return all_pool_games

    @classmethod
    def __create_pool_game(cls, pool, template_game, home_index, away_index):
        return Game(template_game.id,
                    template_game.pitch,
                    template_game.datetime,
                    pool.all_teams[home_index],
                    pool.all_teams[away_index])

    @classmethod
    def __create_rank_game(cls, pool, template_game, template_home, template_away):
        if pool.pool_type in [PoolType.split_with_finals, PoolType.split_with_semi_finals]:
            template_home_pool, template_home_rank = template_home[0], template_home[1:]
            template_away_pool, template_away_rank = template_away[0], template_away[1:]

            home_pool = pool.sub_pools[0] if template_home_pool == "A" else \
                pool.sub_pools[1] if template_home_pool == "B" else None
            home_rank = int(template_home_rank)
            away_pool = pool.sub_pools[0] if template_away_pool == "A" else \
                pool.sub_pools[1] if template_away_pool == "B" else None
            away_rank = int(template_away_rank)
        else:
            home_pool = pool
            home_rank = template_home
            away_pool = pool
            away_rank = template_away

        return RankGame(template_game.id,
                        template_game.pitch,
                        template_game.datetime,
                        home_pool,
                        home_rank,
                        away_pool,
                        away_rank)

    @classmethod
    def __create_result_game(cls, pool, template_game, template_home, template_away):
        template_home_type, template_home_game = template_home[0], template_home[1:]
        template_away_type, template_away_game = template_away[0], template_away[1:]

        return ResultGame(template_game.id,
                          template_game.pitch,
                          template_game.datetime,
                          pool.finals[int(template_home_game)],
                          template_home_type,
                          pool.finals[int(template_away_game)],
                          template_away_type)

    @classmethod
    def __get_games_by_pool(cls, games):
        result = {}
        for game in games:
            if game.pool not in result:
                result[game.pool] = []

            result[game.pool].append(game)

        # we sort first on time, then on pitch descending
        # this is relevant for finals: we want the most important
        # games (which come later in the schedule) on the best pitch
        for gs in result.values():
            gs.sort(key=lambda g: (g.datetime, -g.pitch.rank))

        return result

    __game_template = {
        (1, PoolType.split_with_finals): [],
        (2, PoolType.single_round_robin): [
            ("Pool", 0, 1),
        ],
        (2, PoolType.full_with_finals): [
            ("Pool", 0, 1),
            ("Rank", 1, 2),
        ],
        (3, PoolType.single_round_robin): [
            ("Pool", 0, 1),
            ("Pool", 2, 0),
            ("Pool", 1, 2)
        ],
        (3, PoolType.full_round_robin): [
            ("Pool", 0, 1),
            ("Pool", 2, 0),
            ("Pool", 1, 2),
            ("Pool", 0, 2),
            ("Pool", 1, 0),
            ("Pool", 2, 1)
        ],
        (4, PoolType.single_round_robin): [
            ("Pool", 0, 1), ("Pool", 3, 2),
            ("Pool", 2, 0), ("Pool", 1, 3),
            ("Pool", 0, 3), ("Pool", 1, 2)
        ],
        (4, PoolType.full_with_semi_finals): [
            ("Pool", 0, 1), ("Pool", 3, 2),
            ("Pool", 2, 0), ("Pool", 1, 3),
            ("Pool", 0, 3), ("Pool", 1, 2),
            ("Rank", 1, 4), ("Rank", 2, 3),
            ("Result", "V0", "V1"), ("Result", "W0", "W1")
        ],
        (6, PoolType.single_round_robin): [
            ("Pool", 0, 1), ("Pool", 3, 2), ("Pool", 4, 5),
            ("Pool", 2, 0), ("Pool", 1, 4), ("Pool", 5, 3),
            ("Pool", 0, 4), ("Pool", 2, 5), ("Pool", 1, 3),
            ("Pool", 3, 0), ("Pool", 5, 1), ("Pool", 4, 2),
            ("Pool", 0, 5), ("Pool", 3, 4), ("Pool", 1, 2)
        ],
        (6, PoolType.split_with_finals): [
            ("Pool", 0, 1), ("Pool", 3, 4),
            ("Pool", 2, 0), ("Pool", 5, 3),
            ("Pool", 1, 2), ("Pool", 4, 5),
            ("Rank", "A3", "B3"), ("Rank", "A2", "B2"), ("Rank", "A1", "B1")
        ],
        (8, PoolType.split_with_finals): [
            ("Pool", 0, 1), ("Pool", 3, 2), ("Pool", 4, 5), ("Pool", 7, 6),
            ("Pool", 2, 0), ("Pool", 1, 3), ("Pool", 6, 4), ("Pool", 5, 7),
            ("Pool", 0, 3), ("Pool", 1, 2), ("Pool", 4, 7), ("Pool", 5, 6),
            ("Rank", "A4", "B4"), ("Rank", "A3", "B3"), ("Rank", "A2", "B2"), ("Rank", "A1", "B1"),
        ],
        (8, PoolType.split_with_semi_finals): [
            ("Pool", 0, 1), ("Pool", 3, 2), ("Pool", 4, 5), ("Pool", 7, 6),
            ("Pool", 2, 0), ("Pool", 1, 3), ("Pool", 6, 4), ("Pool", 5, 7),
            ("Pool", 0, 3), ("Pool", 1, 2), ("Pool", 4, 7), ("Pool", 5, 6),
            ("Rank", "A4", "B3"), ("Rank", "A3", "B4"), ("Rank", "A2", "B1"), ("Rank", "A1", "B2"),
            ("Result", "V0", "V1"), ("Result", "W0", "W1"), ("Result", "V2", "V3"), ("Result", "W2", "W3"),
        ],
        (8, PoolType.partial_round_robin): [
            ("Pool", 0, 1), ("Pool", 3, 2), ("Pool", 4, 5), ("Pool", 7, 6),
            ("Pool", 2, 0), ("Pool", 1, 4), ("Pool", 6, 3), ("Pool", 5, 7),
            ("Pool", 3, 0), ("Pool", 5, 1), ("Pool", 7, 2), ("Pool", 4, 6),
            ("Pool", 4, 0), ("Pool", 1, 6), ("Pool", 2, 5), ("Pool", 7, 3),
            ("Pool", 0, 5), ("Pool", 1, 7), ("Pool", 6, 2), ("Pool", 3, 4)
        ]
    }
