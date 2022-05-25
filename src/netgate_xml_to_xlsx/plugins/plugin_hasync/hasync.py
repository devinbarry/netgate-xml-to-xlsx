"""HA Sync plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = (
    "pfsyncenabled,pfsyncenabled,pfsyncinterface,synchronizetoip,username,password"
)
WIDTHS = "20,20,40,40,40,40"


class Plugin(BasePlugin):
    """Gather ca information."""

    def __init__(
        self,
        display_name: str = "HA Sync",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather hasync information."""
        rows = []

        ca_nodes = xml_findall(parsed_xml, "hasync")
        if ca_nodes is None:
            return

        for node in ca_nodes:
            row = []

            for field_name in self.field_names:
                value = self.adjust_node(xml_findone(node, field_name))
                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)
        rows.sort()

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
