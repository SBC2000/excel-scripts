import os

import xlwings

from lib.excel_interop.excel_reader import ExcelReader
from lib.excel_interop.excel_writer import ExcelWriter
from lib.logic.builder import Builder
from lib.logic.persistence_handler import PersistenceHandler
from lib.model.factory import Factory
from lib.pdf_export.pdf_exporter import PdfExporter
from lib.server.upload_handler import UploadHandler


def generate_schedule():
    """
    Reads categories, pools, teams, pitches, and the template game schedule
    and generates complete games schedules.
    The model is NOT persisted, only written to Excel
    @return:
    """
    workbook = xlwings.Book.caller()

    reader = ExcelReader(workbook)
    writer = ExcelWriter(workbook)
    builder = Builder(Factory())

    model = builder.load(reader.read())

    writer.write_game_schedule(model.game_schedule)
    writer.write_games_per_team(model.relevant_pools, model.game_schedule)


def export_model():
    """
    Reads all information in the Excel (including potential referees/jury)
    and serializes everything to a binary database.
    This method does NOT write anything to Excel.
    @return:
    """
    workbook = xlwings.Book.caller()

    reader = ExcelReader(workbook)
    builder = Builder(Factory())

    model = builder.load(reader.read())

    PersistenceHandler(os.path.dirname(__file__)).store_model(model)


def upload_model():
    """
    Upload the model that is serialized to disk to the server.
    This method does NOT communicate with Excel at all.
    @return:
    """
    model = PersistenceHandler(os.path.dirname(__file__)).load_model()

    uploader = UploadHandler()
    uploader.upload_database(model)
    uploader.upload_sponsors(model)


# def print_database():
#    model = PersistenceHandler(os.path.dirname(__file__)).load_model()
#    print model.get_json_database()


def load_printable_schedule():
    """
    Load a database that is serialized to disk and loads it into Excel.
    @return:
    """

    workbook = xlwings.Book.caller()

    model = PersistenceHandler(os.path.dirname(__file__)).load_model()

    __write_printable_schedule(workbook, model)


def __write_printable_schedule(workbook, model):
    pool_by_game = {game: pool
                    for pool in model.all_pools
                    for game in pool.own_games}
    ExcelWriter(workbook).write_printable_game_schedule(model.game_schedule, pool_by_game)


def handle_results():
    workbook = xlwings.Book.caller()

    persistence_handler = PersistenceHandler(os.path.dirname(__file__))
    upload_handler = UploadHandler()
    reader = ExcelReader(workbook)

    model = persistence_handler.load_model()

    all_game_results = reader.load_results()

    new_results, schedule_has_changed = model.apply_new_game_results(all_game_results)

    upload_handler.upload_results(new_results)

    if schedule_has_changed:
        # if the schedule has changed, we need to update Excel and app
        __write_printable_schedule(workbook, model)
        upload_handler.upload_database(model)

    persistence_handler.store_model(model)


def handle_referees_and_jury():
    workbook = xlwings.Book.caller()

    persistence_handler = PersistenceHandler(os.path.dirname(__file__))
    upload_handler = UploadHandler()
    reader = ExcelReader(workbook)

    model = persistence_handler.load_model()

    all_referees_and_juries = reader.load_referees_and_juries()

    referees_have_changed, juries_have_changed = model.apply_referees_and_juries(all_referees_and_juries)

    # we only need to update the app if the referees have changed, because jury is not in there
    if referees_have_changed:
        upload_handler.upload_database(model)

    if referees_have_changed or juries_have_changed:
        persistence_handler.store_model(model)


def generate_rankings_pdf():
    model = PersistenceHandler(os.path.dirname(__file__)).load_model()

    # there is no way to generalize this; that's why this setting is top-level. It is not needed
    page_layout = [["H1"], ["H2"], ["H3"], ["H4"], ["D1"], ["D2"], ["JB", "MBC", "JC"], ["GD"], ["GE"]]

    PdfExporter().export_rankings(model.pools, page_layout)


def generate_schedule_pdf(export_saturday, export_sunday):
    model = PersistenceHandler(os.path.dirname(__file__)).load_model()

    PdfExporter().export_schedule(model.game_schedule, export_saturday, export_sunday)

if __name__ == '__main__':
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Voor toernooi.xlsm'))
    xlwings.Book(path).set_mock_caller()

    # handle_referees_and_jury()
    # UploadHandler().upload_message("Test", "Dit is een test")
    export_model()

