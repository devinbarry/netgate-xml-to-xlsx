"""SNMPD plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "rocommunity,syslocation,syscontact"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "SNMPD",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        node = xml_findone(parsed_xml, "snmpd")
        if node is None:
            return

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
