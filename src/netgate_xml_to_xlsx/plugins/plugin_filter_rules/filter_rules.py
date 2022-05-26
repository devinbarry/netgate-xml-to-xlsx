"""Filter rules plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

# Rules have both 'disabled' and 'enabled' entries.
# Looks like a difference between versions 21 and 22?
# TODO: Determine if they can be combined based on the version number.
FIELD_NAMES = (
    "disabled,enabled,descr,source,destination,"
    "interface,direction,type,protocol,ipprotocol,"
    "quick,icmptype,statetype,statetimeout,floating,"
    "max,max-src-conn,max-src-nodes,max-src-states,os,"
    "tag,tagged,tracker,id,created,"
    "updated"
)
WIDTHS = (
    "20,20,80,60,60,"
    "20,20,20,20,20,"
    "20,20,20,20,20,"
    "20,20,20,20,20,"
    "20,20,20,20,30,"
    "30"
)


class Plugin(BasePlugin):
    """Gather filter rules information."""

    def __init__(
        self,
        display_name: str = "Filter Rules",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "source" | "destination":
                data = self.extract_node_elements(node)
                if "any" in data:
                    return "any"

                # If there's not a network, and there's not "any" there _should_ be
                # an address.
                address = data["network"] if "network" in data else data["address"]
                port = f""":{data["port"]}""" if "port" in data else ""
                return f"{address}{port}"

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ssh data information."""
        rows = []

        rule_nodes = xml_findall(parsed_xml, "filter,rule")
        if rule_nodes is None:
            return

        for node in rule_nodes:
            self.report_unknown_node_elements(node)
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
