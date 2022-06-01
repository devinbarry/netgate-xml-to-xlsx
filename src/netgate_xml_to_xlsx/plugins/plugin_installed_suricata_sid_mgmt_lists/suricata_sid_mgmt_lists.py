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
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "name,modtime,content"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Suricata SID Mgmt",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
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

                match node.tag:
                    case "enable":
                        # Override base one as Suricata stores the value.
                        return node.value

                    case "libhtp_policy" | "host_os_policy":
                        return self.wip(node)

                return datetime.datetime.fromtimestamp(int(value)).strftime(
                    "%Y-%m-%d %H-%M-%S"
                )

            case "content":
                return b64decode(node.text).decode("utf-8")

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
            self.sanity_check_node_row(node, row)

            rows.append(self.sanity_check_node_row(node, row))

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
