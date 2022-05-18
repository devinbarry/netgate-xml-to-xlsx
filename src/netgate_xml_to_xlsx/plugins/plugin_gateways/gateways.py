"""Gateways plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import sys
from typing import Generator

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import get_element

# Append 'defaultgw4' and 'defaultgw6' before finishing run.
FIELD_NAMES = "name,descr,interface,gateway,weight,ipprotocol,monitor_disable"
WIDTHS = "20,40,20,20,10,30,30,20,20"


class Plugin(BasePlugin):
    """Gather data for the Gateways."""

    def __init__(
        self,
        display_name: str = "Gateways",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: dict) -> Generator[SheetData, None, None]:
        """Gather data for Gateways."""
        rows = []

        # Load default IPV4 and IPV6 gateways.
        # Don't want "None" for default gateway.
        default_gw4 = get_element(pfsense, "gateways,defaultgw4")
        default_gw6 = get_element(pfsense, "gateways,defaultgw6")

        # Which column has the gateway name.
        gw_name_col = 0

        # Don't sort nodes for now. Leave in order found.
        nodes = get_element(pfsense, "gateways,gateway_item")
        if not nodes:
            return

        if isinstance(nodes, dict):
            # Only found one.
            nodes = [nodes]

        for node in nodes:
            row = []
            for field_name in self.field_names:
                try:
                    row.append(get_element(node, field_name))
                except AttributeError as err:
                    print(err)
                    sys.exit(-1)

            if default_gw4 == row[gw_name_col]:
                row.append("YES")
            else:
                row.append(None)
            if default_gw6 == row[gw_name_col]:
                row.append("YES")
            else:
                row.append(None)
            rows.append(row)

        self.field_names.extend(["defaultgw4", "defaultgw6"])

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
