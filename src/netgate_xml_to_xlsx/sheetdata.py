"""SheetData."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.


class SheetData:
    """All information required to display a worksheet."""

    def __init__(
        self,
        *,
        sheet_name: str,
        header_row: list[str],
        data_rows: list[list],
        column_widths: list[int] | None = None,
    ) -> None:
        """Gather all necessary information."""
        self.sheet_name = sheet_name
        self.header_row = header_row
        self.data_rows = data_rows
        self.column_widths = [] if column_widths is None else column_widths
        self.column_widths = [int(x) for x in self.column_widths]
