"""PF Block Top Spammers plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "action,agateway_in,agateway_out,aliasaddr_in,aliasaddr_out,"
    "aliaslog,aliasports_in,aliasports_out,autoaddr_in,autoaddr_out,"
    "autoaddrnot_in,autoaddrnot_out,autonot_in,autonot_out,autoports_in,"
    "autoports_out,autoproto_in,autoproto_out,countries4,countries6"
)
WIDTHS = "40,20,20,20,20," "20,20,20,20,20," "20,20,20,20,20," "20,20,20,20,20"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "PF Block Top Spammers",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        pf_node = xml_findone(parsed_xml, "installedpackages,pfblockerngtopspammers")
        if pf_node is None:
            return
        self.report_unknown_node_elements(pf_node, "config".split(","))

        nodes = xml_findall(pf_node, "config")

        for node in nodes:
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
