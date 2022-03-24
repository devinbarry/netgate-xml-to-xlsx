"""OpenVPN Servers plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

from ..base_plugin import BasePlugin
from ..support.elements import (
    get_element,
    load_standard_nodes,
)

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
        display_name="OpenVPN Servers",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ):
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """Document all OpenVPN servers."""
        rows = super().run(pfsense)

        # Don't sort OpenVPN Servers. Want them in the order they are encountered.
        nodes = get_element(pfsense, "openvpn,openvpn-server")
        if not nodes:
            return []

        if isinstance(nodes, OrderedDict):
            nodes = [nodes]

        rows.extend(load_standard_nodes(nodes=nodes, field_names=self.field_names))
        return rows
