"""PF Block erng plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "autorule_suffix,credits,database_cc,enable_agg,enable_cb,"
    "enable_dup,enable_float,enable_log,inbound_deny_action,inbound_interface,"
    "ipsec_action,killstates,log_maxlines,maxmind_key,maxmind_locale,"
    "openvpn_action,outbound_deny_action,outbound_interface,pass_order,pfb_dailystart,"
    "pfb_hour,pfb_interval,pfb_keep,pfb_min,skipfeed,"
    "suppression"
)
WIDTHS = "40,40"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "PF Block RNG",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(
            display_name,
            node_names,
            column_widths,
            el_paths_to_sanitize=[
                "pfsense,installedpackages,pfblockerng,config,maxmind_key"
            ],
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """
        Gather information.

        Display vertically.
        Bools appear to be stored. Existence of bool field does not(?) imply YES/True.
        """
        rows = []

        pf_node = xml_findone(parsed_xml, "installedpackages,pfblockerng")
        if pf_node is None:
            return
        self.report_unknown_node_elements(pf_node, "config".split(","))

        node = xml_findone(pf_node, "config")
        self.report_unknown_node_elements(node)

        for node_name in self.node_names:
            row = []
            row.append(node_name)
            row.append(self.adjust_node(xml_findone(node, node_name)))
            rows.append(self.sanity_check_node_row(node, row))

        yield SheetData(
            sheet_name=self.display_name,
            header_row="name,data".split(","),
            data_rows=rows,
            column_widths=self.column_widths,
        )
