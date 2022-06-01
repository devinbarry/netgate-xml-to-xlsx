"""Ntopng plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "enable,keepdata,interface_array,dns_mode,local_networks,row,redis_password,"
    "redis_passwordagain"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "ntopng",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(
            display_name,
            node_names,
            el_paths_to_sanitize=[
                "pfsense,installedpackages,ntopng,config,redis_password",
                "pfsense,installedpackages,ntopng,config,redis_passwordagain",
            ],
        )

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "enable":
                # Override system enable.
                return node.text if node.text is not None else ""

            case "row":
                return self.wip(node)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        ntopng_node = xml_findone(parsed_xml, "installedpackages,ntopng")
        if ntopng_node is None:
            return

        config_nodes = xml_findall(ntopng_node, "config")
        for config_node in config_nodes:
            self.report_unknown_node_elements(config_node)
            row = []
            for node_name in self.node_names:
                try:
                    node = xml_findone(config_node, node_name)
                    row.append(self.adjust_node(node))
                    continue
                except NodeError as err:
                    if "more than one result" not in str(err):
                        raise err from None

                # More than one, need to re-find all of them.
                cell = []
                cell_nodes = xml_findall(config_node, node_name)
                for cell_node in cell_nodes:
                    cell.append(cell_node.text)
                cell.sort()
                row.append("\n".join(cell))

            rows.append(self.sanity_check_node_row(node, row))

        yield self.rotate_rows(
            SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
            )
        )
