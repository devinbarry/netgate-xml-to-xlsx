"""System Groups plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = (
    "disabled,interface,type,ipprotocol,protocol,"
    "source,destination,tag,tagged,max,"
    "max_src_nodes,max_src-conn,max-src-states,statetimeout,statetype,"
    "os,log,descr,created,updated,"
    "id,tracker,uuid"
)
WIDTHS = (
    "15,15,15,20,40," "50,50,20,20,20," "20,20,20,20,20," "10,10,85,80,80," "10,20,20"
)


class Plugin(BasePlugin):
    """Gather data for the System Groups sheet."""

    def __init__(
        self,
        display_name: str = "Filter Rules",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def _updated_or_created(self, node: Node) -> str:
        """Return "updated" or "created" value, or ""."""
        if updated := self.adjust_node(xml_findone(node, "updated,time")):
            return updated
        return self.adjust_node(xml_findone(node, "created,time"))

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Create the rules sheet.

        Many elements have children that need to be processed.
        """
        rows = []

        rule_nodes = xml_findall(parsed_xml, "filter,rule")

        # Sort rules so that latest changes are at the top.
        rule_nodes.sort(
            key=self._updated_or_created,
            reverse=True,
        )

        for node in rule_nodes:
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
