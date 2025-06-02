import datetime
import requests

from lib.model.game_result import GameResult
from lib.model.model import Model

from .password import password


class UploadHandler:
    results_url = "https://app.sbctoernooien.nl/upload.php"
    password = password

    def __init__(self):
        pass

    def upload_results(self, results):
        """
        @type results: list[GameResult]
        @rtype: None
        """
        upload_string = self.__create_results_upload_string(results)

        self.__upload({"type": "results", "data": upload_string})

    def upload_database(self, model):
        """
        @type model: Model
        @rtype: None
        """
        upload_string = model.get_json_database()

        self.__upload({"type": "database", "data": upload_string})

    def upload_sponsors(self, model):
        """
        @type model: Model
        @rtype: None
        """
        upload_string = model.get_json_sponsors()

        self.__upload({"type": "sponsors", "data": upload_string})

    def upload_message(self, title, message):
        """
        @type message: str
        @return: None
        """
        now = datetime.datetime.now()
        upload_string = "{{\"id\": {0}, \"title\": \"{1}\", \"message\": \"{2}\", \"date\": \"{3}\"}}".format(
            now.strftime("%Y%m%d%H%M%S"),
            title,
            message,
            now.strftime("%d-%m-%Y %H:%M:%S"),
        )

        self.__upload({"type": "message", "data": upload_string})

    def __upload(self, data):
        """
        @type data: dict[str, str]
        @rtype: None
        """
        data["password"] = self.password
        r = requests.post(self.results_url, data)

        if r.status_code // 100 != 2:
            raise Exception("Upload failed! Error code {0}. Response: {1}".format(r.status_code, r.text))

    def __create_results_upload_string(self, game_results):
        """
        @type game_results: list[GameResult]
        @rtype: None
        """
        upload_strings = []
        for identifier, game_result in game_results.items():
            upload_strings.append(self.__create_result_upload_string(identifier, game_result))

        return ",".join(upload_strings)

    @staticmethod
    def __create_result_upload_string(identifier, game_result):
        """
        @type game_result: GameResult
        @rtype: None
        """
        return "{{\"gameId\": {0}, \"homeScore\": {1}, \"awayScore\": {2}}}" \
            .format(identifier, game_result.home_score, game_result.away_score)
