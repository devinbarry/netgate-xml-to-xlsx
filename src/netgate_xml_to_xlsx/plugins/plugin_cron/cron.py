"""Cron plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "minute,hour,mday,month,wday,who,command"
WIDTHS = "20,20,20,20,20,20,200"


class Plugin(BasePlugin):
    """Gather cron information."""

    def __init__(
        self,
        display_name: str = "Cron",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []

        cron_nodes = xml_findall(parsed_xml, "cron,item")
        if cron_nodes is None:
            return

        for node in cron_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
