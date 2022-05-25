"""System Groups plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall

FIELD_NAMES = "name,description,scope,gid,priv"
WIDTHS = "40,80,20,20,80"


class Plugin(BasePlugin):
    """Gather data for the System Groups."""

    def __init__(
        self,
        display_name: str = "System Groups",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Sheet with system.group information.

        Multiple groups with multiple privileges.
        Display privileges alpha sorted.
        """
        rows = []
        system_group_nodes = xml_findall(parsed_xml, "system,group")
        if not system_group_nodes:
            return

        system_group_nodes.sort(key=lambda x: x.text.casefold())

        for node in system_group_nodes:
            row = []
            for field_name in self.field_names:
                values = [self.adjust_node(x) for x in xml_findall(node, field_name)]
                values.sort()

                row.append("\n".join(values))
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
