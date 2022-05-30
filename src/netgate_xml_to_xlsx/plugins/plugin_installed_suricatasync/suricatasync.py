"""Suricata Sync Plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "vardownloadrules,varsynconchanges,varsynctimeout,rule"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Suricata (sync)",
        node_names: str = NODE_NAMES,
        column_widths: str = "",
    ) -> None:
        """Gather information."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "row":
                # I expect this is going to have multiple rows in some installations.
                return self.load_cell(
                    node,
                    (
                        "varsyncprotocol,varsyncipaddress,varsyncport,varsyncpassword,"
                        "varsyncsuricatastart"
                    ).split(","),
                )

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        suricata_node = xml_findone(parsed_xml, "installedpackages,suricatasync")
        if suricata_node is None:
            return
        self.report_unknown_node_elements(suricata_node, "config".split("<"))

        node = xml_findone(suricata_node, "config")
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
