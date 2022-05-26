"""NTPD plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

FIELD_NAMES = "gps,orphan,statsgraph,interface,restrictions,ispool"
WIDTHS = "20,20,20,20,20,40"


class Plugin(BasePlugin):
    """Gather ca information."""

    def __init__(
        self,
        display_name: str = "NTPD",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None or node.text is None:
            return ""

        match node.tag:
            case "gps":
                return self.wip(node)

            case "interface":
                # Order is important? Don't sort.
                return "\n".join(node.text.split(","))

            case "ispool":
                # Order is important. Don't sort.
                return "\n".join(node.text.split(" "))

            case "restrictions":
                return self.wip(node)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []

        node = xml_findone(parsed_xml, "ntpd")
        if node is None:
            return

        self.report_unknown_node_elements(node)
        row = []

        for field_name in self.field_names:
            value = self.adjust_node(xml_findone(node, field_name))
            row.append(value)

        self.sanity_check_node_row(node, row)
        rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
