"""HTML Format"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import datetime
import logging
from html import escape

from netgate_xml_to_xlsx.sheetdata import SheetData

from .base_format import BaseFormat


class HtmlFormat(BaseFormat):
    def __init__(self, ctx: dict) -> None:
        self.ctx = ctx
        self.output_fh = 0
        self.sheet_data = SheetData()

        self.logger = logging.getLogger()
        self.header_row_length = 0
        self.logged_row_length_warning = False

    def start(self) -> None:
        """Create output file and write HTML boilerplate."""
        self.output_fh = open(self.ctx["output_path"], "w", encoding="utf-8")

        self.output_fh.write(HTML_TOP)

    def out(self, sheet_data: SheetData) -> None:
        if not len(sheet_data.data_rows):
            # Nothing to write
            return

        self.logged_row_length_warning = False
        self.header_row_length = len(sheet_data.header_row)
        self.sheet_data = sheet_data

        self._write_header(sheet_data)
        self._write_table(sheet_data)

    def finish(self) -> None:
        """Write HTML page bottom and save file."""
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        self.output_fh.write(f"""<div class="footer">Runtime: {now}.</div>\n""")

        self.output_fh.write(HTML_BOTTOM)
        self.output_fh.close()

    def _write_header(self, sheet_data: SheetData) -> None:
        """Write section header."""
        self.output_fh.write(f"<h2>{sheet_data.sheet_name}</h2>\n\n")

    def _write_table(self, sheet_data: SheetData) -> None:
        """
        HTML Table.

        Structure this like the .txt output showing node and value.
        """
        if sheet_data is None or not sheet_data.data_rows:
            return

        for row in sheet_data.data_rows:
            self.check_row_length(row)
            self.output_fh.write("<table>\n")
            for row in sheet_data.data_rows:
                self._write_row(row)
            self.output_fh.write("</table>\n")
            self.output_fh.write("<hr />\n\n")

    def _write_row(self, row) -> None:
        """
        Write one data row's information.

        Write each element on a single line in format:
            sheet_name: header: value (flattened into a single line)
        """
        # Flatten the data.
        data = [escape(x).replace("\n", "; ") for x in row]

        for node, value in zip(self.sheet_data.header_row, data):
            self.output_fh.write(f"<tr><td>{node}</td><td>{value}</td></tr>\n")
        self.output_fh.flush()


HTML_TOP = """\
<html>
  <header>
  </header>
  <body>
    <h1>pfSense Output</h1>
    <div>
       TODO: Information from configuration file.
    </div>

"""

HTML_BOTTOM = """\
  </body>
</html>
"""
