"""
Suricata SID Management plugin.

Our XML examples clearly do not use the urlsafe b64 encoding as they contain '+'s.

"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import datetime
from base64 import b64decode
from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall,xml_findone

NODE_NAMES = "name,modtime,content"

WIDTHS = "40,40,100"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Suricata SID Mgmt",
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
            case "modtime":
                value = node.text.strip()
                if value == "":
                    return ""

                return datetime.datetime.fromtimestamp(
                    int(value)
                ).strftime("%Y-%m-%d %H-%M-%S")


            case "content":
                return b64decode(node.text)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        suricata_node = xml_findone(parsed_xml, "installedpackages,suricata")
        if suricata_node is None:
            return
        self.report_unknown_node_elements(
            suricata_node, "config,passlist,rule,sid_mgmt_lists".split(",")
        )

        nodes = xml_findall(suricata_node, "sid_mgmt_lists,item")

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
