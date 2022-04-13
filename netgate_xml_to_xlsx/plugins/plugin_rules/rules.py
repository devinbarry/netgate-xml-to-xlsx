"""System Groups plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict
from typing import Generator

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import (
    get_element,
    rules_destination,
    rules_source,
    rules_username_time,
    updated_or_created,
)

FIELD_NAMES = (
    "id,tracker,type,interface,ipprotocol,tag,tagged,max,max_src_nodes,"
    "max_src-conn,max-src-states,statetimeout,statetype,os,source,destination,"
    "log,descr,created,updated"
)
WIDTHS = "10,20,10,15,15,10,10,10,20,20,20,20,20,10,50,50,40,80,85,85"


class Plugin(BasePlugin):
    """Gather data for the System Groups sheet."""

    def __init__(
        self,
        display_name: str = "Rules",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> Generator[list[list[str]], None, None]:
        """Create the rules sheet."""
        rows = super().run(pfsense)
        source_index = self.field_names.index("source")
        destination_index = self.field_names.index("destination")
        created_index = self.field_names.index("created")
        updated_index = self.field_names.index("updated")

        nodes = get_element(pfsense, "filter,rule")
        if not nodes:
            return []

        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]

        # Sort rules so that latest changes are at the top.
        nodes.sort(
            key=updated_or_created,
            reverse=True,
        )

        for node in nodes:
            row = []
            for field_name in self.field_names:
                row.append(get_element(node, field_name))
            row = ["" if x is None else x for x in row]

            row[source_index] = rules_source(row, source_index)
            row[destination_index] = rules_destination(row, destination_index)
            row[created_index] = rules_username_time(row, created_index)
            row[updated_index] = rules_username_time(row, updated_index)

            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
