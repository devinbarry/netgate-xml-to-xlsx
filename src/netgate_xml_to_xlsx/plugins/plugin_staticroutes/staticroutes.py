"""Static Routes plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = "descr,network,gateway"
WIDTHS = "60,40,40"


class Plugin(BasePlugin):
    """Gather staticroutes information."""

    def __init__(
        self,
        display_name: str = "Static Routes",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []

        routes_nodes = xml_findall(parsed_xml, "staticroutes,route")
        if routes_nodes is None:
            return

        for routes_node in routes_nodes:
            row = []
            for field_name in self.field_names:
                row.append(self.adjust_node(xml_findone(routes_node, field_name)))

            self.sanity_check_node_row(routes_node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
