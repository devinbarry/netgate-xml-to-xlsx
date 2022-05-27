"""Widgets plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import unescape, xml_findone

FIELD_NAMES = "sequence,period,traffic_graphs"
WIDTHS = "40,10,80"


class Plugin(BasePlugin):
    """Gather widgets information."""

    def __init__(
        self,
        display_name: str = "Widgets",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustements."""
        if node is None:
            return ""

        match node.tag:
            case "sequence":
                sequence = unescape(node.text)
                sequences = sequence.split(",")
                return "\n".join(sequences)

            case "traffic_graphs":
                field_names = (
                    "refreshinterval,invert,backgroundupdate,smoothfactor,size,filter"
                ).split(",")
                self.report_unknown_node_elements(node, field_names)
                cell = []
                for field_name in field_names:
                    cell.append(
                        f"{field_name}: {self.adjust_node(xml_findone(node, field_name))}"
                    )
                return "\n".join(cell)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather widgets information."""
        rows = []

        node = xml_findone(parsed_xml, "widgets")
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
