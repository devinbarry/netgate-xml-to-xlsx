"""RRD plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import unescape, xml_findone

FIELD_NAMES = "enable,category"
WIDTHS = "10,40"


class Plugin(BasePlugin):
    """Gather ca information."""

    def __init__(
        self,
        display_name: str = "RRD",
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
            case "category":
                category = unescape(node.text)
                categories = category.split("&")
                return "\n".join(categories)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather rrd information."""
        rows = []

        node = xml_findone(parsed_xml, "rrd")
        if node is None:
            return

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
