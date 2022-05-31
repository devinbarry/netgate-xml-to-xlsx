"""SquidGuard General plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "adv_blankimg,blacklist,blacklist_proxy,blacklist_url,enable_guilog,"
    "enable_log,ldapcachetime,ldap_enable,ldapbinddn,ldapbindpass,ldapversion,"
    "log_rotation,rewrite_children,rewrite_children_idle,rewrite_children_startup,"
    "squidguard_enable,stripntdomain,striprealm"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "SquidGuard (gen)",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        squid_node = xml_findone(parsed_xml, "installedpackages,squidguardgeneral")
        if squid_node is None:
            return
        self.report_unknown_node_elements(squid_node, "config".split(","))

        node = xml_findone(squid_node, "config")
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
            )
        )
