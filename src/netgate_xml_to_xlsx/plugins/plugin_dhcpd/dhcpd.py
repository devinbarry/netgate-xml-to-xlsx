"""DHCPD plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "name,enable,range,ddnsclientupdates,ddnsdomain,"
    "ddnsdomainkey,ddnsdomainkeyalgorithm,ddnsdomainkeyname,ddnsdomainprimary,defaultleasetime,"
    "dhcpleaseinlocaltime,domain,domainsearchlist,failover_peerip,filename,"
    "filename32,filename64,gateway,ldap,mac_allow,"
    "mac_deny,maxleasetime,netmask,nextserver,numberoptions,"
    "rootpath,tftp"
)
WIDTHS = (
    "20,20,40,40,20,"
    "40,40,40,40,40,"
    "40,40,40,40,40,"
    "40,40,40,40,20,"
    "20,20,20,20,20,"
    "40,40"
)


class Plugin(BasePlugin):
    """Gather dhcpd information."""

    def __init__(
        self,
        display_name: str = "DHCPD",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "mac_allow" | "mac_deny":
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"

            case "range":
                node_names = "from,to".split(",")
                self.report_unknown_node_elements(node, node_names)
                cell = []
                for node_name in node_names:
                    cell.append(
                        f"{node_name}: {self.adjust_node(xml_findone(node, node_name))}"
                    )
                return "\n".join(cell)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather ntpd information."""
        rows = []
        dhcpd_node = xml_findone(parsed_xml, "dhcpd")
        if dhcpd_node is None:
            return

        for node in dhcpd_node.getchildren():
            self.report_unknown_node_elements(node)
            row = []

            for node_name in self.node_names:
                if node_name == "name":
                    row.append(node.tag)
                    continue
                row.append(self.adjust_node(xml_findone(node, node_name)))

            self.sanity_check_node_row(node, row)
            rows.append(row)
        rows.sort()

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
