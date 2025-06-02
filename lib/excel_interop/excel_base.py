import collections


class ExcelBase:
    def __init__(self, workbook):
        count = 0

        try:
            self.pools_sheet = workbook.sheets("Poules")
            self.referees_sheet = workbook.sheets("Scheidsrechters")
            self.teams_sheet = workbook.sheets("Teams")
            self.games_sheet = workbook.sheets("Wedstrijden")
            self.sponsors_sheet = workbook.sheets("Sponsors")
            self.schedule_sheet = workbook.sheets("Schema")
            self.schedule_pitch4_sheet = workbook.sheets("Schema Veld 4")
            self.games_per_team_sheet = workbook.sheets("Wedstrijden per team")
            count += 1
        except:
            pass

        try:
            self.printable_schedule_saturday_sheet = workbook.sheets("Zaterdag")
            self.printable_schedule_saturday_pitch4_sheet = workbook.sheets("Zaterdag Veld 4")
            self.printable_schedule_sunday_sheet = workbook.sheets("Zondag")
            count += 1
        except:
            pass

        if count == 0:
            raise Exception("Not all required sheets are present in the workbook")

    @staticmethod
    def _load_sheet(sheet):
        """
        Get the contents of a sheet as a list of header-contents tuples
        @type sheet: xlwings.Sheet
        @rtype: list[tuple[str, list[str]]]
        """
        result = []

        values = sheet.range("A1:CZ100").value
        values = [list(i) for i in zip(*values)]  # transpose
        useful_columns = [column for column in values if column[0] is not None]
        for useful_column in useful_columns:
            # fetch all data in the column until the first non-empty cell
            for i, value in enumerate(reversed(useful_column)):
                if value is not None:
                    result.append((useful_column[0], useful_column[1:-i]))
                    break

        return result

    def _write_sheet(self, sheet, matrix, start_row=0, start_column=0, row_colors=[]):
        row_lens = set(len(row) for row in matrix)
        if len(row_lens) != 1:
            raise Exception("Only rectangular matrices are supported")
        sheet.clear()
        sheet.range(self.__excel_style(start_row, start_column)).value = matrix

        if row_colors:
            row_len = next(iter(row_lens))
            for i, color in enumerate(row_colors):
                color_range = "{0}:{1}".format(self.__excel_style(start_row + i, start_column),
                                               self.__excel_style(start_row + i, start_column + row_len - 1))
                sheet.range(color_range).color = color

        sheet.autofit("columns")

    @staticmethod
    def __excel_style(row, col):
        # excel is 1-based
        col += 1
        row += 1

        result = []
        while col:
            col, rem = divmod(col - 1, 26)
            result[:0] = chr(rem + ord('A'))
        return ''.join(result) + str(row)

    @staticmethod
    def __get_iterable(x):
        if isinstance(x, collections.Iterable) and not isinstance(x, basestring):
            return x
        else:
            return x,
