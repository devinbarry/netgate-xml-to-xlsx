"""FreeRADIUS Clients Plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "description,varclientip,varclientipversion,varclientlogininput,varclientmaxconnections,"
    "varclientnastype,varclientpasswordinput,varclientproto,varclientsharedsecret,"
    "varclientshortname,varrequiremessageauthenticator"
)


WIDTHS = "60,30,30,30,30,30,30,30,30,40,30"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "FreeRADIUS Clients",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "sortable":
                return self.yes(node)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        radius_node = xml_findone(parsed_xml, "installedpackages,freeradiusclients")
        if radius_node is None:
            return
        self.report_unknown_node_elements(radius_node, "config".split(","))

        nodes = xml_findall(radius_node, "config")

        for node in nodes:
            self.report_unknown_node_elements(node)

            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))
            rows.append(row)

        rows.sort(key=lambda x: x[0].casefold())
        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
