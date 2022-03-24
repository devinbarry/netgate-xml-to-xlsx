"""Base plugin class."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict


def _split_commas(data: str | list, make_int=False) -> list:
    """
    Create list from comma-delimited string (or list).

    If make_int is True, ensure final list contents are integers.

    Args:
        data:
            String or list of data to process.

        make_int:
            True if final list must contain only integers.

    Returns:
        list

    """
    if isinstance(data, str):
        data = data.split(",")

    if make_int:
        return [int(x) for x in data]
    return data


class BasePlugin:
    """Base of all plugins."""

    def __init__(
        self,
        display_name: str,
        field_names: str,
        column_widths: str | list[int],
    ) -> None:
        """
        Initialize base plugin.

        field_names:
            Comma-delimited list of fields to obtain.
            Also used for the sheet's header row.

        column_widths:
            Comma-delimited list of sheet column widths.

        """
        self.display_name = display_name
        self.field_names = _split_commas(field_names)
        self.column_widths = _split_commas(column_widths, make_int=True)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """
        Run plugin.

        Args:
            pfsense:
                Root of the XML configuration file parsed to dictionary.

        Returns:
            List of rows to write to spreadsheet.

        """
        # Placeholder for future possible functionality.
        _ = pfsense
        return []
