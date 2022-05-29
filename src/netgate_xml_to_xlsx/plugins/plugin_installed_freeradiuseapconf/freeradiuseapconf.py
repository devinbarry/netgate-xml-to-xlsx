"""FreeRADIUS AP Configuration."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "ssl_ca_cert,ssl_server_cert"
WIDTHS = "40,40"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "FreeRADIUS AP",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        radius_node = xml_findone(parsed_xml, "installedpackages,freeradiuseapconf")
        if radius_node is None:
            return
        self.report_unknown_node_elements(radius_node, "config".split(","))

        nodes = xml_findall(radius_node, "config")

        for node in nodes:
            self.report_unknown_node_elements(node)
            row = []

            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))

            rows.append(self.sanity_check_node_row(node, row))

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
