"""Squid Auth plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "auth_method,auth_processes,auth_prompt,auth_server,auth_server_port,"
    "auth_ttl,ldap_basedomain,ldap_filter,ldap_pass,ldap_user,"
    "ldap_userattribute,ldap_version,no_auth_hosts,radius_secret,unrestricted_auth"
)


WIDTHS = "20,20,20,20,30,20,30,20,20,20,30,20,20,20,30"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Squid (auth)",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
            el_paths_to_sanitize=(
                [
                    "pfsense,installedpackages,squidauth,config,ldap_pass",
                    "pfsense,installedpackages,squidauth,config,radius_secret",
                ]
            ),
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        squid_node = xml_findone(parsed_xml, "installedpackages,squidauth")
        if squid_node is None:
            return
        self.report_unknown_node_elements(squid_node, "config".split(","))

        nodes = xml_findall(squid_node, "config")

        for node in nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))

            rows.append(self.sanity_check_node_row(node, row))

        rows.sort(key=lambda x: " ".join(x[0:1]).casefold())

        yield self.rotate_rows(
            SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )
        )
