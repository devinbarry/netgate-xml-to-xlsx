"""Installed Packages plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import unescape, xml_findall, xml_findone

FIELD_NAMES = (
    "name,internal_name,version,descr,plugins,"
    "noembedded,logging,website,pkginfolink,filter_rule_function,"
    "configuration_file,include_file"
)
WIDTHS = "40,40,20,80,40," "20,40,80,80,80," "80,80"


def name_sort(node: Node) -> str:
    """Extract element name for sorting."""
    if node is None:
        return ""
    value = unescape(xml_findone(node, "name").text).casefold()
    return value


class Plugin(BasePlugin):
    """Gather data for the Installed Packages."""

    def __init__(
        self,
        display_name: str = "Installed Packages",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node customizations."""
        if node is None:
            return ""

        match node.tag:
            case "logging":
                return "WIP"  # TODO: logsocket, facilityname, logfilename

            case "plugins":
                # Get 'item'.
                children = node.getchildren()
                plugins = []
                for child in children:
                    assert child.tag == "item"
                    plugins.append(self.adjust_node(xml_findone(child, "type")))
                plugins.sort()
                return "\n".join(plugins)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document installed packages. Sort by name."""
        rows = []

        package_nodes = xml_findall(parsed_xml, "installedpackages,package")

        package_nodes.sort(
            key=name_sort,
            # key=lambda x: x.name.casefold(),
            reverse=False,
        )

        for node in package_nodes:
            row = []

            for field_name in self.field_names:
                value = self.adjust_node(xml_findone(node, field_name))

                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
