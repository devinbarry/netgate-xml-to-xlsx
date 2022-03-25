"""Installed Packages plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import (
    get_element,
    load_standard_nodes,
)

FIELD_NAMES = (
    "name,internal_name,descr,version,configuration_file,include_file,"
    "website,pkginfolink,filter_rule_function"
)
WIDTHS = "40,40,50,20,50,50,80,80,50"


class Plugin(BasePlugin):
    """Gather data for the Installed Packages."""

    def __init__(
        self,
        display_name="Installed Packages",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ):
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """Gather data for Installed Packages. Sort by name."""
        rows = super().run(pfsense)

        nodes = get_element(pfsense, "installedpackages,package")
        if not nodes:
            return []

        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]
        nodes.sort(key=lambda x: x["name"].casefold())

        rows = load_standard_nodes(nodes=nodes, field_names=self.field_names)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
