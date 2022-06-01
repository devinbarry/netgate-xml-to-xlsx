"""Installed Packages list plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "tag"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Installed Packages List",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document the installed packages by node tag."""
        ip_list = []

        ip_node = xml_findone(parsed_xml, "installedpackages")
        for node in ip_node.getchildren():
            if node.tag == "package":
                continue

            ip_list.append(node.tag)

        ip_list = list(set(ip_list))
        ip_list.sort(key=str.casefold)
        rows = [[x] for x in ip_list]

        yield SheetData(
            sheet_name=self.display_name,
            header_row=["Package"],
            data_rows=rows,
            column_widths=[
                60,
            ],
            ok_to_rotate=False,
        )
