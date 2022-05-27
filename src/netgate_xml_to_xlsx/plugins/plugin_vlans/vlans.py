"""VLANS plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = "descr,vlanif,if,tag,pcp"
WIDTHS = "40,20,20,20,20"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "VLANs",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        cron_nodes = xml_findall(parsed_xml, "vlans,vlan")
        if cron_nodes is None:
            return

        for node in cron_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for field_name in self.field_names:
                row.append(self.adjust_node(xml_findone(node, field_name)))

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
