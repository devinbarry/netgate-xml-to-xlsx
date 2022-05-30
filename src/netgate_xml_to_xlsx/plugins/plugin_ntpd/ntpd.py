"""NTPD plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "gps,orphan,statsgraph,interface,restrictions,ispool"


class Plugin(BasePlugin):
    """Gather ca information."""

    def __init__(
        self,
        display_name: str = "NTPD",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None or node.text is None:
            return ""

        match node.tag:
            case "acl_network":
                return self.yes(node)

            case "gps":
                field_names = "type".split(",")
                return self.load_cell(node, field_names)

            case "interface":
                # Order is important? Don't sort.
                result = node.text.split(",")
                result.sort()
                return "\n".join(result)

            case "ispool":
                # Order is important. Don't sort.
                return "\n".join(node.text.split(" "))

            case "restrictions":
                node_names = "acl_network,mask".split(",")
                row_nodes = xml_findall(node, "row")
                cell = []
                for row_node in row_nodes:
                    cell.append(self.load_cell(row_node, node_names))
                    cell.append("")
                if len(cell) > 0 and cell[-1] == "":
                    cell = cell[:-1]

                return "\n".join(cell)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []

        node = xml_findone(parsed_xml, "ntpd")
        if node is None:
            return

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
            )
        )
