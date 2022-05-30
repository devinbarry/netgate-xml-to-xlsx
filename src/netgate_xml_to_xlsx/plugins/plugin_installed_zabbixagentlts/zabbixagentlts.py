"""Zabbix Agent LTS plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "agentenabled,buffersend,buffersize,hostname,listenip,"
    "listenport,refreshactchecks,server,serveractive,startagents,"
    "timeout,tlsaccept,tlscafile,tlscaso,tlscertfile,"
    "tlsconnect,tlscrlfile,tlspskfile,tlspskidentity,userparams"
)
WIDTHS = "20,20,20,40,20,20,20,20,20,20,20,20,20,20,20,20,20,20,40,20"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Zabbix Agent",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
            el_paths_to_sanitize=[
                "installedpackages,zabbixagentlts,config,tlspskfile",
                "installedpackages,zabbixagentlts,config,userparams",
            ],
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        zabbix_node = xml_findone(parsed_xml, "installedpackages,zabbixagentlts")
        if zabbix_node is None:
            return

        self.report_unknown_node_elements(zabbix_node, "config".split(","))

        node = xml_findone(zabbix_node, "config")
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
