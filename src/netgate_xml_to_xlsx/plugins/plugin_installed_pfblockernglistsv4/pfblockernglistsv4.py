"""PF Block Lists v4 plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "aliasname,description,action,agateway_in,agateway_out,"
    "aliasaddr_in,aliasaddr_out,aliaslog,aliasports_in,aliasports_out,"
    "autoaddr_in,autoaddr_out,autoaddrnot_in,autoaddrnot_out,autonot_in,"
    "autonot_out,autoports_in,autoports_out,autoproto_in,autoproto_out,"
    "cron,custom,custom_update,dow,format,"
    "header,row,state,stateremoval,url,"
    "whois_convert"
)
WIDTHS = (
    "40,60,20,20,20,"
    "20,20,20,20,20,"
    "20,20,20,20,20,"
    "20,20,20,20,20,"
    "20,20,20,20,20,"
    "30,60,30,30,60,"
    "40"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "PF Block Lists v4",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
        )

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "row":
                node_names = "state,format,header,url".split(",")
                return self.load_cell(node, node_names)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Gather information.

        Display vertically.
        Bools appear to be stored. Existence of bool field does not(?) imply YES/True.
        """
        rows = []

        pf_node = xml_findone(parsed_xml, "installedpackages,pfblockernglistsv4")
        if pf_node is None:
            return
        self.report_unknown_node_elements(pf_node, "config".split(","))

        nodes = xml_findall(pf_node, "config")

        for node in nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
