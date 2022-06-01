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
        ok_to_rotate: bool = True,
    ) -> None:
        """
        Sheet display information.

        Sheet nomenclature retained even though we now have non-ss formats.

        Args:
            sheet_name:
                Name of this sheet/section.

            header_row:
                Top row.

            data_rows:
                Data to output.

            column_widths:
                With of the spreadsheet columns.

            ok_to_rotate:
                True if it is OK for the output format to rotate the data.
                Defaults to True as most of the data has so far been rotatable.

        """
        self.sheet_name = sheet_name
        self.header_row = header_row
        self.data_rows = data_rows
        self.column_widths = [] if column_widths is None else column_widths
        self.column_widths = [int(x) for x in self.column_widths]
        self.ok_to_rotate = ok_to_rotate
