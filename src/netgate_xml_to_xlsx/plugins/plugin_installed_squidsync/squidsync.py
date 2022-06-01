"""Squid Sync Plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "synconchanges,synctimeout,row"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Squid (sync)",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Gather information."""
        super().__init__(display_name, node_names)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "row":
                # I expect this is going to have multiple rows in some installations.
                return self.load_cell(
                    node,
                    "syncprotocol,ipaddress,syncport,syncdestinenable,username,password".split(
                        ","
                    ),
                )

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        squidguard_node = xml_findone(parsed_xml, "installedpackages,squidsync")
        if squidguard_node is None:
            return
        self.report_unknown_node_elements(squidguard_node, "config".split("<"))

        node = xml_findone(squidguard_node, "config")
        self.report_unknown_node_elements(node)

        row = []
        for node_name in self.node_names:
            row.append(self.adjust_node(xml_findone(node, node_name)))

        rows.append(self.sanity_check_node_row(node, row))

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
