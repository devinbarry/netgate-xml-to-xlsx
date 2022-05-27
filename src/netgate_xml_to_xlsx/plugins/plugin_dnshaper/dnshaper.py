"""
DNS Shaper plugin.

Our example XML files do not yet have information for this element.
"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = ""
WIDTHS = ""


class Plugin(BasePlugin):
    """Gather dnshaper information."""

    def __init__(
        self,
        display_name: str = "DNS Shaper",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []
        node = xml_findone(parsed_xml, "dnshaper")
        if node is None:
            return

        # Report when data arrives.
        self.report_unknown_node_elements(node, [])

        # Need the yield so this is a generator
        yield None
