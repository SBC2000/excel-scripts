class HtmlGenerator:
    def __init__(self):
        pass

    @staticmethod
    def create_html_table(table, column_info, has_header=False, rotate_header=False):
        result = "<table>"

        if has_header:
            header, table = table[0], table[1:]
            result += "<tr>"
            for cell, width, alignment, color in zip(header,
                                                     column_info["width"],
                                                     column_info["header-alignment"],
                                                     column_info["color"]):
                if rotate_header:
                    result += "<th class=\"rotate\" width=\"" + str(width) + \
                              "\" style=\"text-align: " + alignment + "; background-color: " + color + "\" ><div><span>"
                    result += str(cell)
                    result += "</span></div></th>"
                else:
                    result += "<th width=\"{0}\" style=\"text-align: {1}; background-color: {2}\">{3}</th>".format(
                        width,
                        alignment,
                        color,
                        cell
                    )
            result += "</tr>"

        for row in table:
            result += "<tr>"
            for cell, width, alignment, color in zip(row,
                                                     column_info["width"],
                                                     column_info["content-alignment"],
                                                     column_info["color"]):
                result += "<td width=\"" + str(width) \
                          + "\" style=\"text-align: " + alignment \
                          + "; background-color: " + color + "\" >"
                result += str(cell)
                result += "</td>"
            result += "</tr>"

        result += "</table>"

        return result
