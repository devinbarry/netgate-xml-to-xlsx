"""Notifications plugin.

A two-column format to handle multiple notification types.
"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

FIELD_NAMES = "type,settings"
WIDTHS = "20,100"


class Plugin(BasePlugin):
    """Gather notifications information."""

    def __init__(
        self,
        display_name: str = "Notifications",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments.

        Only type we know about at the moment is smtp.
        """
        if node is None or node.text is None:
            return ""

        match node.tag:
            case "smtp":
                field_names = (
                    "disable,ipaddress,port,timeout,notifyemailaddress,username,password,"
                    "authentication_mechanism,fromaddress"
                ).split(",")
                cell = []
                for field_name in field_names:
                    cell.append(
                        f"{field_name}: {self.adjust_node(xml_findone(node, field_name))}"
                    )

                return "\n".join(cell)

            case "disable":
                # Existence indicates YES.
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )
                return "YES"
            case _:
                print("Unknown Notifications type.")

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []

        node = xml_findone(parsed_xml, "notifications")
        if node is None:
            return

        self.report_unknown_node_elements(node)
        children = node.getchildren()
        if len(children) == 0:
            return

        row = []

        for child in children:
            row.append(child.tag)
            value = self.adjust_node(child)
            row.append(value)

        self.sanity_check_node_row(node, row)
        rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
