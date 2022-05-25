"""OpenVPN Servers plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = (
    "vpnid,disable,mode,protocol,dev_mode,interface,ipaddr,local_port,"
    "description,custom_options,shared_key,digest,engine,tunnel_network,"
    "tunnel_networkv6,remote_network,remote_networkv6,gwredir,gwredir6,"
    "local_network,local_networkv6,maxclients,compression,compression_push,passtos,"
    "client2client,dynamic_ip,topology,serverbridge_dhcp,serverbridge_interface,"
    "serverbridge_routegateway,serverbridge_dhcp_start,serverbridge_dhcp_end,"
    "username_as_common_name,exit_notify,sndrcvbuf,netbios_enable,netbios_ntype,"
    "netbios_scope,create_gw,verbosity_level,ncp_enable,ping_method,keepalive_interval,"
    "keepalive_timeout,ping_seconds,ping_push,ping_action,ping_action_seconds,"
    "ping_action_push,inactive_seconds,data_ciphers,data_ciphers_fallback"
)
WIDTHS = (
    "20,20,20,20,20,30,20,20,30,20,"  # 10
    "40,20,20,30,30,30,30,20,20,30,"  # 20
    "20,20,20,30,20,20,20,20,40,40,"  # 30
    "40,40,40,50,20,20,20,20,20,20,"  # 40
    "20,20,20,30,30,20,20,20,30,30,"  # 50
    "20,20,50"
)


class Plugin(BasePlugin):
    """Gather data for the System Groups."""

    def __init__(
        self,
        display_name: str = "OpenVPN Servers",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document all OpenVPN servers."""
        rows = []

        openvpn_server_nodes = xml_findall(parsed_xml, "openvpn,openvpn-server")
        if not len(openvpn_server_nodes):
            return

        for node in openvpn_server_nodes:
            row = []

            for field_name in self.field_names:
                value = self.adjust_node(xml_findone(node, field_name))

                row.append(value)

            self.sanity_check_node_row(node, row)
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
