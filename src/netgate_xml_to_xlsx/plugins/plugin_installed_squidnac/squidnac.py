"""Squid NAC plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from base64 import b64decode
from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import nice_address_sort, xml_findone

NODE_NAMES = (
    "allowed_subnets,unrestricted_hosts,banned_hosts,blacklist,whitelist,"
    "addtl_ports,addtl_sslports,block_reply_mime_type,block_user_agent,"
    "google_accounts,youtube_restrict"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Squid NAC",
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
            case "blacklist" | "whitelist":
                decode = b64decode(node.text).decode("utf-8")
                els = decode.splitlines()

                return nice_address_sort(" ".join(els), " ")

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        squid_node = xml_findone(parsed_xml, "installedpackages,squidnac")
        if squid_node is None:
            return
        self.report_unknown_node_elements(squid_node, "config".split(","))

        node = xml_findone(squid_node, "config")
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
