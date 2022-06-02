"""Base Format class."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import logging
from abc import ABC, abstractmethod

from netgate_xml_to_xlsx.sheetdata import SheetData


class BaseFormat(ABC):
    """Base of all formats."""

    def __init__(self, ctx: dict) -> None:
        """
        Initialize base format.

        Args:
            ctx: Context containing necessary initialization information.
        """
        self.header_row_length: int = 0
        self.sheet_data: SheetData = SheetData()
        self.logged_row_length_warning: bool = False
        self.logger: logging.Logger = logging.getLogger()

    @abstractmethod
    def start(self) -> None:
        """Do required report start-up based on data in ctx."""
        raise NotImplementedError

    @abstractmethod
    def out(self, rows: SheetData) -> None:
        """Generate a sheet/page/section."""
        raise NotImplementedError

    @abstractmethod
    def finish(self) -> None:
        """Perform cleanup, saving, etc."""
        raise NotImplementedError

    def rotate_rows(self, data: SheetData) -> SheetData:
        """
        Rotate horizontal headers and rows into vertical columns.

        Set header_row to "name,data,..."
        Calculate proper number of column widths and header columns.

        """
        if not len(data.data_rows):
            # No data to process.
            return data
        data.data_rows = list(zip(data.header_row, *data.data_rows))

        data.header_row = ["name"]
        data.header_row.extend(["data" for x in range(len(data.data_rows[0]) - 1)])
        data.column_widths = [60]
        data.column_widths.extend([80 for x in range(len(data.data_rows[0]) - 1)])

        return data

    def check_row_length(self, row: list[str]) -> None:
        """Log warnings for any unmatched header_row/row lengths."""
        row_length = len(row)
        if row_length != self.header_row_length and not self.logged_row_length_warning:
            msg = (
                f"{self.sheet_data.sheet_name} has mismatched header "
                f"({self.header_row_length}) and row ({row_length})."
            )
            self.logger.warning("%s", msg)
            self.logged_row_length_warning = True
