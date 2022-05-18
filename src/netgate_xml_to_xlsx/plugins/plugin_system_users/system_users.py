"""System Users plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import get_element

FIELD_NAMES = "name,enabled,descr,scope,expires,ipsecpk,uid,cert"
WIDTHS = "40,10,60,20,20,20,10,60"


class Plugin(BasePlugin):
    """Gather data for the System Users sheet."""

    def __init__(
        self,
        display_name: str = "System Users",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: dict) -> Generator[SheetData, None, None]:
        """
        Sheet with system.user information.

        Not all fields displayed as # column on dashboard and webguicss are uninteresting
        (at least to me at the moment).
        """
        rows = []
        nodes = get_element(pfsense, "system,user")
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
            # The existence of the disabled element indicates user is disabled.
            row[1] = "No" if "disabled" in node else "Yes"
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
