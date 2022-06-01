"""HTML Format"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import datetime
from html import escape

from netgate_xml_to_xlsx.sheetdata import SheetData

from .base_format import BaseFormat


class HtmlFormat(BaseFormat):
    def __init__(self, ctx: dict) -> None:
        self.ctx = ctx
        self.output_fh = None

    def start(self):
        """Create output file and write HTML boilerplate."""
        self.output_fh = open(self.ctx["output_path"], "w", encoding="utf-8")

        self.output_fh.write(HTML_TOP)

    def out(self, sheet_data: SheetData) -> None:
        if sheet_data is None or not sheet_data.data_rows:
            return

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
        """HTML Table."""
        self.output_fh.write("<table>\n")
        self.output_fh.write("  <thead>\n")
        for header in sheet_data.header_row:
            self.output_fh.write(f"    <th>{escape(header)}</th>\n")

        for row in sheet_data.data_rows:
            self.output_fh.write("  <tr>\n")
            for col in row:
                self.output_fh.write("    <td>\n")
                sub_rows = "<br />".join([escape(x) for x in col.splitlines()])
                self.output_fh.write(f"      {sub_rows}")
                self.output_fh.write("\n    </td>\n\n")
            self.output_fh.write("  </tr>\n\n")

        self.output_fh.write("  </thead>\n")
        self.output_fh.write("</table>\n\n")


HTML_TOP = """\
<html>
  <header>
  </header>
  <body>
"""

HTML_BOTTOM = """\
  </body>
</html>
"""
