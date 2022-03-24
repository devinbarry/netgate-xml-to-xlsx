"""System Users plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

from ..base_plugin import BasePlugin
from ..support.elements import (
    get_element,
)

FIELD_NAMES = "name,descr,scope,expires,ipsecpk,uid,cert"
WIDTHS = "40,60,20,20,20,10,60"


class Plugin(BasePlugin):
    """Gather data for the System Users sheet."""

    def __init__(
        self,
        display_name="System Users",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ):
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """
        Sheet with system.user information.

        Not all fields displayed as # column on dashboard and webguicss are uninteresting
        (at least to me at the moment).
        """
        rows = super().run(pfsense)

        nodes = get_element(pfsense, "system,user")
        if not nodes:
            return []

        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]
        nodes.sort(key=lambda x: x["name"].casefold())

        for node in nodes:
            row = []
            for key in self.field_names:
                row.append(get_element(node, key))
            rows.append(row)

        return rows
