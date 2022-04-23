"""System plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict
from typing import Generator

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import get_element

FIELD_NAMES = "name,value"
WIDTHS = "80,80"


class Plugin(BasePlugin):
    """Gather data for the System sheet."""

    def __init__(
        self,
        display_name: str = "System",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> Generator[SheetData, None, None]:
        """
        System-level information.

        Only showing interesting information (at least to me at the moment).
        """
        rows = []

        # Version and change information.
        node = pfsense
        for key in "version,lastchange".split(","):
            rows.append([key, get_element(node, key)])

        # Check version number.
        if (version := int(float(rows[0][1]))) != 21:
            assert version is not None
            print(
                f"Warning: File uses version {version}.x. "
                "Script is only tested on version 21 XML formats."
            )

        node = get_element(pfsense, "system", None)
        if node is not None:
            for key in "optimization,hostname,domain,timezone".split(","):
                rows.append([key, get_element(node, key)])

        time_servers = "\n".join(get_element(node, "timeservers").split(" "))
        rows.append(["timeservers", time_servers])

        rows.append(["bogons", get_element(node, "bogons,interval")])
        rows.append(["ssh", get_element(node, "ssh,enabled")])
        rows.append(["dnsserver", "\n".join(get_element(node, "dnsserver"))])

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
