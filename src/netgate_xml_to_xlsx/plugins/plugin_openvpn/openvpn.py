"""OpenVPN plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = (
    "vpnid,description,disable,mode,protocol,dev_mode,interface,ipaddr,local_port,"
    "custom_options,shared_key,digest,engine,tunnel_network,"
    "tunnel_networkv6,remote_network,remote_networkv6,gwredir,gwredir6,"
    "local_network,local_networkv6,maxclients,compression,compression_push,passtos,"
    "client2client,dynamic_ip,topology,serverbridge_dhcp,serverbridge_interface,"
    "serverbridge_routegateway,serverbridge_dhcp_start,serverbridge_dhcp_end,"
    "username_as_common_name,exit_notify,sndrcvbuf,netbios_enable,netbios_ntype,"
    "netbios_scope,create_gw,verbosity_level,ncp_enable,ping_method,keepalive_interval,"
    "keepalive_timeout,ping_seconds,ping_push,ping_action,ping_action_seconds,"
    "ping_action_push,inactive_seconds,data_ciphers,data_ciphers_fallback,"
    "authmode,tls,tls_type,tlsauth_keydir,caref,certref,crlref,dh_length,"
    "ocspurl,ecdh_curve,dns_server1,cert_depth,strictusercn,allow_compression,"
    "dns_server2,dns_server3,dns_server4"
)


class Plugin(BasePlugin):
    """Gather data for the System Groups."""

    def __init__(
        self,
        display_name: str = "OpenVPN",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, node_names)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "stricusercn":
                return self.yes(node)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document all OpenVPN servers."""
        rows = []

        openvpn_server_nodes = xml_findall(parsed_xml, "openvpn,openvpn-server")
        if not len(openvpn_server_nodes):
            return

        for node in openvpn_server_nodes:
            self.report_unknown_node_elements(node)
            row = []

            for node_name in self.node_names:
                value = self.adjust_node(xml_findone(node, node_name))

                row.append(value)

            rows.append(self.sanity_check_node_row(node, row))

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
