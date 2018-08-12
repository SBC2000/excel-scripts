from scheduler import Scheduler
from lib.model.model import Model
from lib.model.pool import PoolType


class Builder:
    def __init__(self, factory):
        """
        @type factory: Factory
        @rtype: None
        """
        self.__factory = factory

    def load(self, flat_data):
        """
        @type flat_data: FlatData
        @rtype: Model
        """
        model = Model()

        pools_by_abbreviation = {}

        for flat_category in flat_data.categories:
            category = self.__factory.create_category(flat_category)
            model.add_category(category)

            for flat_pool in flat_data.get_pools_by_category(flat_category):
                pool = self.__factory.create_pool(flat_pool[0], flat_pool[1], self.__convert_pool_type(flat_pool[2]))
                pools_by_abbreviation[pool.abbreviation] = pool
                category.add_pool(pool)

                for flat_team in flat_data.get_teams_by_pool_abbr(pool.abbreviation):
                    team = self.__factory.create_team(flat_team)
                    pool.add_team(team)

        for flat_referee in flat_data.referees:
            referee = self.__factory.create_referee(flat_referee)
            model.add_referee(referee)

        template_games = []
        for flat_pitch in flat_data.pitches:
            pitch = self.__factory.create_pitch(flat_pitch)
            model.add_pitch(pitch)

            for flat_game in flat_data.get_games_by_pitch(flat_pitch):
                if flat_game[1]:
                    template_games.append(
                        self.__factory.create_template_game(pitch, flat_game[0], pools_by_abbreviation[flat_game[1]]))

        for flat_sponsor in flat_data.sponsors:
            sponsor = self.__factory.create_sponsor(*flat_sponsor)
            model.add_sponsor(sponsor)

        model.game_schedule = Scheduler().build_schedule(template_games)

        referees_by_name = {}
        referees_by_name.update({referee.name: referee for referee in model.referees})
        referees_by_name.update({referee.get_first_name(): referee for referee in model.referees})
        
        for game in model.games:
            referees_and_jury = flat_data.get_referees_and_jury_by_game(game)
            if referees_and_jury:
                if referees_and_jury["referee1"]:
                    game.referee1 = referees_by_name[referees_and_jury["referee1"]]
                if referees_and_jury["referee2"]:
                    game.referee2 = referees_by_name[referees_and_jury["referee2"]]
                game.jury = referees_and_jury["jury"]

        return model

    @classmethod
    def __convert_pool_type(cls, pool_type):
        if pool_type == "SRR":
            return PoolType.single_round_robin
        elif pool_type == "FRR":
            return PoolType.full_round_robin
        elif pool_type == "SWSF":
            return PoolType.split_with_semi_finals
        elif pool_type == "SWF":
            return PoolType.split_with_finals
        elif pool_type == "FWSF":
            return PoolType.full_with_semi_finals
        elif pool_type == "FWF":
            return PoolType.full_with_finals
        else:
            raise Exception("Unexpected pool type " + pool_type)
