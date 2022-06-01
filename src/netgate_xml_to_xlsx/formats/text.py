"""Text Format"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import datetime
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

    def start(self):
        """Create output file."""
        self.output_fh = open(self.ctx["output_path"], "w", encoding="utf-8")

    def out(self, sheet_data: SheetData) -> None:
        if sheet_data is None or not sheet_data.data_rows:
            return

        self.sheet_data = sheet_data
        for row in sheet_data.data_rows:
            self._write_row(row)

        # Add a separator
        separator = "-" * 20
        self.output_fh.write(f"\n{separator}\n\n")

    def finish(self) -> None:
        """Write trailer and save file."""
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
        self.output_fh.write(f"Runtime: {now}.\n")
        self.output_fh.close()

    def _write_row(self, row: list[str]) -> None:
        """Write one data row of information."""
        cols = [f"{self.sheet_data.sheet_name}:"]
        cols.extend([escape(x).replace("\n", "; ") for x in row])
        self.output_fh.write("\t".join(cols))
        self.output_fh.write("\n")
        self.output_fh.flush()
