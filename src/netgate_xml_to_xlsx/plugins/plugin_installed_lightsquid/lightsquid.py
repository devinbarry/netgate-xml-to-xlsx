"""Lightsquid plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "lightsquid_barcolor,lightsquid_ip2name,lightsquid_lang,lightsquid_refreshsheduler_time,"
    "lightsquid_skipurl,lightsquid_template,lighttpd_ls_password,lighttpd_ls_port,"
    "lighttpd_ls_ssl,lighttpd_ls_user"
)
WIDTHS = "40,60,20,60,60,60,60,20,20,20"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "LightSquid",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        lightsquid_node = xml_findone(parsed_xml, "installedpackages,lightsquid")
        if lightsquid_node is None:
            return
        self.report_unknown_node_elements(lightsquid_node, "config".split(","))

        node = xml_findone(lightsquid_node, "config")
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
