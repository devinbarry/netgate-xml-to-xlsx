"""Report: Unknown installed packages."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = "Package Name"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Unknown Packages",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def run(
        self, parsed_xml: Node, installed_plugins: dict | None
    ) -> Generator[SheetData, None, None]:
        """
        Gather information.

        Compare all children of the 'installedpackages' node and report on unrecognized nodes.

        """
        rows = []
        node = xml_findone(parsed_xml, "installedpackages")
        if node is None:
            self.logger.warning("No packages are installed.")
            yield None

        child_tags = set([x.tag for x in node.getchildren()])
        plugin_tags = set(installed_plugins.keys())

        for child_tag in child_tags:
            if child_tag in ("package",):
                continue

            if (
                f"installed_{child_tag}" in plugin_tags
                or f"report_{child_tag}" in plugin_tags
            ):
                continue
            rows.append([child_tag])

        rows.sort(key=lambda x: x[0].casefold())

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
