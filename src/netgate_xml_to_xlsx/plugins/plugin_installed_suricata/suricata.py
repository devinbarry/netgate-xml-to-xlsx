"""Suricata (config) plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "alert_log_limit_size,alert_log_retention,auto_manage_sids,autogeoipupdate,autoruleupdate,"
    "autoruleupdatetime,block_log_limit_size,block_log_retention,clearlogs,enable_etopen_custom_url,"  # NOQA
    "enable_etopen_rules,enable_etpro_custom_url,enable_etpro_rules,enable_gplv2_custom_url,enable_log_mgmt,"  # NOQA
    "enable_snort_custom_url,enable_vrt_rules,et_iqrisk_enable,etopen_custom_rule_url,etpro_custom_rule_url,"  # NOQA
    "etprocode,eve_log_limit_size,eve_log_retention,extra_rules,file_store_limit_size,"
    "file_store_retention,forcekeepsettings,gplv2_custom_url,hide_deprecated_rules,http_log_limit_size,"  # NOQA
    "http_log_retention,live_swap_updates,log_to_systemlog,log_to_systemlog_facility,maxmind_geoipdb_key,"  # NOQA
    "oinkcode,rm_blocked,sid_changes_log_limit_size,sid_changes_log_retention,sid_list_migration,"
    "snort_custom_url,snort_rules_file,snortcommunityrules,stats_log_limit_size,stats_log_retention,"
    "suricata_config_ver,suricataloglimit,suricataloglimitsize,tls_certs_store_retention,tls_log_limit_size,"  # NOQA
    "tls_log_retention"
)

# Vertical list.
WIDTHS = "60,20"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "Suricata (cfg)",
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

        suricata_node = xml_findone(parsed_xml, "installedpackages,suricata")
        if suricata_node is None:
            return
        self.report_unknown_node_elements(
            suricata_node, "config,passlist,rule,sid_mgmt_lists".split(",")
        )

        node = xml_findone(suricata_node, "config")
        self.report_unknown_node_elements(node)

        for node_name in self.node_names:
            row = []
            row.append(node_name)
            row.append(self.adjust_node(xml_findone(node, node_name)))
            rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row="name,data".split(","),
            data_rows=rows,
            column_widths=self.column_widths,
        )