"""PF Blocker NG Sync plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "varsynconchanges,varsynctimeout,syncinterfaces,row"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "PF Blocker NG Sync",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(
            display_name,
            node_names,
            el_paths_to_sanitize=[
                "installedpackages,pfblockerngsync,config,varsyncpassword",
            ],
        )

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "row":
                names = (
                    "varsyncprotocol,varsyncipaddress,varsyncport,varsyncusername,"
                    "varsyncpassword"
                ).split(",")
                return self.load_cell(node, names)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        zabbix_node = xml_findone(parsed_xml, "installedpackages,pfblockerngsync")
        if zabbix_node is None:
            return

        self.report_unknown_node_elements(zabbix_node, "config".split(","))

        node = xml_findone(zabbix_node, "config")
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
