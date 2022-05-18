"""System Groups plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import get_element

FIELD_NAMES = "name,description,scope,gid,priv"
WIDTHS = "40,80,20,20,80"


class Plugin(BasePlugin):
    """Gather data for the System Groups."""

    def __init__(
        self,
        display_name: str = "System Groups",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: dict) -> Generator[SheetData, None, None]:
        """
        Sheet with system.group information.

        Multiple groups with multiple privileges.
        Display privileges alpha sorted.
        """
        rows = []
        nodes = get_element(pfsense, "system,group")
        if not nodes:
            return

        if isinstance(nodes, dict):
            # Only found one.
            nodes = [nodes]

        nodes.sort(key=lambda x: x["name"].casefold())

        for node in nodes:
            row = []
            for key in self.field_names:
                row.append(get_element(node, key))
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
