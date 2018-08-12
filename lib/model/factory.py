from category import Category
from sponsor import Sponsor
from pitch import Pitch
from pool import Pool
from referee import Referee
from team import Team
from template_game import TemplateGame


class Factory:
    def __init__(self):
        self.__id = 0
        self.__category_rank = 1
        self.__pitch_rank = 1
        self.__pool_rank = 1

    def __next_id(self):
        result = self.__id
        self.__id += 1
        return result

    def __next_category_rank(self):
        result = self.__category_rank
        self.__category_rank += 1
        return result

    def __next_pitch_rank(self):
        result = self.__pitch_rank
        self.__pitch_rank += 1
        return result

    def __next_pool_rank(self):
        result = self.__pool_rank
        self.__pool_rank += 1
        return result

    def create_category(self, name):
        return Category(self.__next_id(), name, self.__next_category_rank())

    def create_pool(self, name, abbreviation, pool_type):
        return Pool(self, self.__next_id(), name, abbreviation, pool_type, self.__next_pool_rank())

    def create_team(self, name):
        return Team(self.__next_id(), name)

    def create_referee(self, name):
        return Referee(self.__next_id(), name)

    def create_pitch(self, name):
        return Pitch(self.__next_id(), name, self.__next_pitch_rank())

    def create_template_game(self, pitch, datetime, pool):
        return TemplateGame(self.__next_id(), pitch, datetime, pool)

    def create_sponsor(self, name, uri):
        return Sponsor(self.__next_id(), name, uri)