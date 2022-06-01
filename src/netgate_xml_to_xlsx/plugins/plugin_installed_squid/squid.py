"""Squid (config) plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "alert_log_limit_size,active_interface,admin_email,allow_interface,carpstatusvid,"
    "custom_options,custom_options_squid3,"
    "custom_options2_squid3,custom_options3_squid3,dca,defined_ip_proxy_off,defined_ip_proxy_off_dest,"  # NOQA
    "dhparams_size,disable_pinger,disable_squidversion,disable_via,dns_nameservers,"
    "dns_v4_first,enable_squid,error_language,extraca,icp_port,interception_adapt,"
    "interception_checks,keep_squid_data,listenproto,log_dir,log_enabled,log_rotate,"
    "log_sqd,outgoing_interface,private_subnet_proxy_off,proxy_port,ssl_active_interface,ssl_proxy,"  # NOQA
    "ssl_proxy_port,sslcrtd_children,sslproxy_compatibility_mode,sslproxy_mitm_mode,transparent_active_interface,"  # NOQA
    "transparent_proxy,uri_whitespace,visible_hostname,xforward_mode,update_notify"
)


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Squid (cfg)",
        node_names: str = NODE_NAMES,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
        )

    def adjust_node(self, node: Node) -> str:
        if node is None:
            return ""

        match node.tag:
            case "active_interface" | "ssl_active_interface" | "transparent_active_interface":  # NOQA
                return "\n".join(node.text.split(","))

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        suricata_node = xml_findone(parsed_xml, "installedpackages,squid")
        if suricata_node is None:
            return
        self.report_unknown_node_elements(suricata_node, "config".split(","))

        node = xml_findone(suricata_node, "config")
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
            )
        )
