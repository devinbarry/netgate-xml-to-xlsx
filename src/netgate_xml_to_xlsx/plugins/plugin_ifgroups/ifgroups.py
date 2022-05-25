"""Gateways plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = "ifname,members,descr"
WIDTHS = "40,40,40"


class Plugin(BasePlugin):
    """Gather ifgroups information."""

    def __init__(
        self,
        display_name: str = "IF Groups",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "members":
                cell = node.text.split(" ")
                return "\n".join(cell)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ifgroups information."""
        rows = []

        ifgroups_nodes = xml_findall(parsed_xml, "ifgroups,ifgroupentry")
        if ifgroups_nodes is None:
            return

        for node in ifgroups_nodes:
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
