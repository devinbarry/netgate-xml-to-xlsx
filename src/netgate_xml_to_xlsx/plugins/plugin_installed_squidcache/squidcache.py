"""Squid Cache plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "cache_dynamic_content,cache_replacement_policy,cache_swap_high,cache_swap_low,custom_refresh_patterns,"  # NOQA
    "donotcache,enable_offline,ext_cachemanager,harddisk_cache_location,harddisk_cache_size,"
    "harddisk_cache_system,level1_subdirs,maximum_object_size,maximum_objsize_in_mem,memory_cache_size,"  # NOQA
    "memory_replacement_policy,minimum_object_size"
)

WIDTHS = "30,40,30,30,30,30,30,30,60,30,30,30,30,40,30,40,30"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Squid (cache)",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        squid_node = xml_findone(parsed_xml, "installedpackages,squidcache")
        if squid_node is None:
            return
        self.report_unknown_node_elements(squid_node, "config".split(","))

        nodes = xml_findall(squid_node, "config")

        for node in nodes:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                row.append(self.adjust_node(xml_findone(node, node_name)))

            rows.append(self.sanity_check_node_row(node, row))

        yield self.rotate_rows(
            SheetData(
                sheet_name=self.display_name,
                header_row=self.node_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )
        )
