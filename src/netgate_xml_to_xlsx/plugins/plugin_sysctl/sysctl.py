"""Sysctl plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "descr,tunable,value"
WIDTHS = "100,100,40"


class Plugin(BasePlugin):
    """Gather sysctl information."""

    def __init__(
        self,
        display_name: str = "SYSCTL Tuning",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather sysctl information."""
        rows = []

        sysctl_nodes = xml_findall(parsed_xml, "sysctl,item")
        if sysctl_nodes is None:
            return

        for node in sysctl_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                value = self.adjust_node(xml_findone(node, node_name))
                row.append(value)

            rows.append(self.sanity_check_node_row(node, row))

        yield self.rotate_rows(
            SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )
        )
