"""Interfaces plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict
from typing import Generator

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import get_element

FIELD_NAMES = (
    "name,descr,alias-address,alias-subnet,spoofmac,enable,"
    "blockpriv,blockbogons,ipaddr,subnet,gateway"
)
WIDTHS = "20,40,20,20,20,20,20,20,20,10,40"


class Plugin(BasePlugin):
    """Gather data for the Interfaces."""

    def __init__(
        self,
        display_name: str = "Interfaces",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> Generator[SheetData, None, None]:
        """
        Document all interfaces.

        TODO: Review blockbogons. Does existence == On?
        """
        rows = []

        # Prepend 'name' before calling _write_sheet.

        # Don't sort interfaces. Want them in the order they are encountered.
        # Interfaces is an OrderedDict
        nodes = get_element(pfsense, "interfaces")
        if not nodes:
            return

        # Don't put nodes in a list as we want a single element

        # Remove 'name' from field_names as we're adding it manually.
        # Put it back before exiting.
        del self.field_names[0]

        for name, node in nodes.items():
            row = [name]
            for field_name in self.field_names:
                row.append(get_element(node, field_name))
            rows.append(row)
        self.field_names.insert(0, "name")

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
