"""System Groups plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

from ..base_plugin import BasePlugin
from ..support.elements import (
    get_element,
    load_standard_nodes,
)

FIELD_NAMES = "name,type,address,url,updatefreq,descr,detail"
WIDTHS = "40,40,40,80,20,80,80"


class Plugin(BasePlugin):
    """Gather data for the System Groups."""

    def __init__(
        self,
        display_name="Aliases",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ):
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """Aliases sheet."""
        rows = super().run(pfsense)

        nodes = get_element(pfsense, "aliases,alias")
        if not nodes:
            return []

        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]
        nodes.sort(key=lambda x: x["name"].casefold())

        rows.extend(load_standard_nodes(nodes=nodes, field_names=self.field_names))

        return rows
