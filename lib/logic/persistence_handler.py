import os
import pickle

from lib.model.model import Model


class PersistenceHandler:
    def __init__(self, folder):
        self.__model_file_name = os.path.join("model.bin")

    def store_model(self, model):
        """
        @type model: Model
        @return: None
        """
        with open(self.__model_file_name, "wb") as output_file:
            pickle.dump(model, output_file)

    def load_model(self):
        """
        @rtype: Model
        """
        with open(self.__model_file_name, "rb") as input_file:
            return pickle.load(input_file)
