"""System Users plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall

NODE_NAMES = (
    "disabled,name,groupname,scope,expires,"
    "descr,ipsecpk,uid,cert,bcrypt-hash,"
    "authorizedkeys,ipsecpsk,priv,dashboardcolumns,webguicss"
)


class Plugin(BasePlugin):
    """Gather data for the System Users sheet."""

    def __init__(
        self,
        display_name: str = "System Users",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Sheet with system.user information.

        Not all nodes displayed as # column on dashboard and webguicss are uninteresting
        (at least to me at the moment).
        """
        rows = []

        system_user_nodes = xml_findall(parsed_xml, "system,user")
        if not system_user_nodes:
            return

        system_user_nodes.sort(key=lambda x: x.text.casefold())

        for node in system_user_nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                values = [self.adjust_node(x) for x in xml_findall(node, node_name)]
                values.sort()

                row.append("\n".join(values))

            rows.append(self.sanity_check_node_row(node, row))

        yield self.rotate_rows(
            SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
            )
        )
