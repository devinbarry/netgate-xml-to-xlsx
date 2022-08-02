"""OpenVPN Export plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "node,advancedoptions,blockoutsidedns,legacy,pass,"
    "pkcs11providers,proxyaddr,proxypass,proxyport,proxyuser,"
    "randomlocalport,server,useaddr,useaddr_hostname,usepass,"
    "usepkcs11,useproxy,useproxypass,useproxytype,usetoken,"
    "verifyservercn"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "OpenVPN Export",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []
        vpn_node = xml_findone(parsed_xml, "installedpackages/vpn_openvpn_export")
        if vpn_node is None:
            return

        self.report_unknown_node_elements(
            vpn_node, "defaultsettings,serverconfig,config".split(",")
        )

        # Default settings.
        node = xml_findone(vpn_node, "defaultsettings")
        if node is not None:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                if node_name == "node":
                    row.append("defaultsettings")
                    continue

                row.append(self.adjust_node(xml_findone(node, node_name)))
            rows.append(self.sanity_check_node_row(node, row))

        # Serverconfig. Allowing there to be more than one.
        nodes = xml_findall(vpn_node, "serverconfig,item")
        if nodes is not None:
            for node in nodes:
                self.report_unknown_node_elements(node)
                row = []
                for node_name in self.node_names:
                    if node_name == "node":
                        row.append("serverconfig")
                        continue

                    row.append(self.adjust_node(xml_findone(node, node_name)))
                rows.append(self.sanity_check_node_row(node, row))

        # Config.
        node = xml_findone(vpn_node, "config")
        if node is not None:
            self.report_unknown_node_elements(node)
            row = []
            for node_name in self.node_names:
                if node_name == "node":
                    row.append("defaultsettings")
                    continue

                row.append(self.adjust_node(xml_findone(node, node_name)))
            rows.append(self.sanity_check_node_row(node, row))

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
