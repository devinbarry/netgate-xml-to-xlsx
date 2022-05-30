"""Service Watchdog plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "name,description,rcfile,executable"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Service Watchdog",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        nodes = xml_findall(parsed_xml, "installedpackages,servicewatchdog,item")
        if nodes is None:
            return

        for node in nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))

            rows.append(self.sanity_check_node_row(node, row))

        rows.sort(key=lambda x: x[0].casefold())

        yield self.rotate_rows(
            SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
            )
        )
