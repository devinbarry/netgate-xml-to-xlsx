"""Text Format"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import datetime
import logging
from html import escape

from netgate_xml_to_xlsx.sheetdata import SheetData

from .base_format import BaseFormat


class TextFormat(BaseFormat):
    """
    Structured text format.

    Allows convenience "diffing" between versions.
    Each line starts with the display name.
    All elements are flattened (\n removed) and separated by tab.
    """

    def __init__(self, ctx: dict) -> None:
        self.ctx = ctx
        self.output_fh = None
        self.sheet_data = None

        self.logger = logging.getLogger()
        self.header_row_length = 0
        self.logged_row_length_warning = False

    def start(self):
        """Create output file."""
        self.output_fh = open(self.ctx["output_path"], "w", encoding="utf-8")

    def out(self, sheet_data: SheetData) -> None:
        """
        Generate one chunk of data.

        Log warning if length of header_row and any data_row differs.
        """
        if sheet_data is None or not sheet_data.data_rows:
            return

        row_separator = f"""{"-"*20}\n\n"""
        section_separator = f"""{"="*20}\n\n"""
        self.logged_row_length_warning = False
        self.header_row_length = len(sheet_data.header_row)
        self.sheet_data = sheet_data
        for row in sheet_data.data_rows:
            self.check_row_length(row)
            self._write_row(row)
            self.output_fh.write(row_separator)

        self.output_fh.write(section_separator)

    def finish(self) -> None:
        """Write trailer and save file."""
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        self.output_fh.write(f"Runtime: {now}.\n")
        self.output_fh.close()

    def _write_row(self, row: list[str]) -> None:
        """
        Write one data row's information.

        Write each element on a single line in format:
            sheet_name: header: value (flattened into a single line)
        """
        # Flatten the data.
        data = [escape(x).replace("\n", "; ") for x in row]

        for node, value in zip(self.sheet_data.header_row, data):
            self.output_fh.write(f"{self.sheet_data.sheet_name}: {node}: {value}\n")
        self.output_fh.flush()
