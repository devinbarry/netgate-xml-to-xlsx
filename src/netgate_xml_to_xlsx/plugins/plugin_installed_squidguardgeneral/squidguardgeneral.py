"""SquidGuard General plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "adv_blankimg,blacklist,blacklist_proxy,blacklist_url,enable_guilog,"
    "enable_log,ldap_enable,ldapbinddn,ldapbindpass,ldapversion,"
    "log_rotation,squidguard_enable,stripntdomain,striprealm"
)


# Vertical list.
WIDTHS = ""


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "SquidGuard (gen)",
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
        vertical_rows = self.rotate_rows(rows)

        col_widths = [60]
        col_widths.extend([40 for x in range(len(vertical_rows[0]) - 1)])
        header_row = ["name"]
        header_row.extend(["data" for x in range(len(vertical_rows[0]) - 1)])

        yield SheetData(
            sheet_name=self.display_name,
            header_row=header_row,
            data_rows=vertical_rows,
            column_widths=col_widths,
        )
