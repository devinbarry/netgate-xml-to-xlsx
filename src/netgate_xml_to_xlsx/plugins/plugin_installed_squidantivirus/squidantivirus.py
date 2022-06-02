"""
Squid Antivirus plugin.

Our example XML files do not yet have information for this element.
"""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = ""


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Squid Antivirus",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        node = xml_findone(parsed_xml, "installedpackages,squid,squidantivirus")
        if node is None:
            return

        # Report when data arrives.
        self.report_unknown_node_elements(node, [])

        yield SheetData()
