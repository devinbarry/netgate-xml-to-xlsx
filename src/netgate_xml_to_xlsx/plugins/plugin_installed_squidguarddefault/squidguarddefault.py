"""SquidGuard Default plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "dest,deniedmessage,enablelog,notallowingip,redirect,"
    "redirect_mode,rewrite,safesearch"
)

WIDTHS = "40,40,30,30,30,30,30,30"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "SquidGuard (default)",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
        )

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "dest":
                els = node.text.split(" ")
                return "\n".join(els)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        squid_node = xml_findone(parsed_xml, "installedpackages,squidguarddefault")
        if squid_node is None:
            return
        self.report_unknown_node_elements(squid_node, "config".split(","))

        node = xml_findone(squid_node, "config")

        self.report_unknown_node_elements(node)
        row = []
        for node_name in self.node_names:
            row.append(self.adjust_node(xml_findone(node, node_name)))

        rows.append(self.sanity_check_node_row(node, row))

        yield self.rotate_rows(
            SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )
        )
