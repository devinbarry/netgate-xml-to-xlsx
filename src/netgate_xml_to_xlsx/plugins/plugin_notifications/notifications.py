"""Notifications plugin.

A two-column format to handle multiple notification types.
"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "type,disable,ipaddress,port,timeout,notifyemailaddress,username,password,"
    "authentication_mechanism,fromaddress"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Notifications",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments.

        Only type we know about at the moment is smtp.
        """
        if node is None or node.text is None:
            return ""

        match node.tag:
            case "disable":
                return self.yes(node)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        node = xml_findone(parsed_xml, "notifications")
        if node is None:
            return

        self.report_unknown_node_elements(node, "smtp".split(","))
        children = node.getchildren()
        if len(children) == 0:
            return

        for child in children:
            row = []
            for name in self.node_names:
                row.append(self.adjust_node(xml_findone(child, name)))

            rows.append(self.sanity_check_node_row(node, row))

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
