"""FreeRADIUS Plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findone

NODE_NAMES = (
    "description,qrcodetext,sortable,varusersacctinteriminterval,varusersamountoftime,"
    "varusersauthmethod,varuserscheckitemsadditionaloptions,varusersexpiration,"
    "varusersframedipaddress,varusersframedipnetmask,"
    "varusersframedroute,varuserslogintime,varusersmaxbandwidthdown,"
    "varusersmaxbandwidthup,varusersmaxtotaloctets,"
    "varusersmaxtotaloctetstimerange,varusersmotpenable,varusersmotpinitsecret,"
    "varusersmotpoffset,varusersmotppin,"
    "varuserspassword,varuserspasswordencryption,varuserspointoftime,"
    "varusersreplyitemsadditionaloptions,varuserssessiontimeout,varuserssimultaneousconnect,"
    "varuserstopadditionaloptions,varusersusername,varusersvlanid,varuserswisprredirectionurl"
)

# Display vertically.
WIDTHS = "60,60"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "FreeRADIUS",
        node_names: str = NODE_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Gather information."""
        super().__init__(display_name, node_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "sortable":
                return self.yes(node)

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        rows = []

        radius_node = xml_findone(parsed_xml, "installedpackages,freeradius")
        if radius_node is None:
            return
        self.report_unknown_node_elements(radius_node, "config".split("<"))

        node = xml_findone(radius_node, "config")
        self.report_unknown_node_elements(node)

        row = []
        for node_name in self.node_names:
            row.append(node_name)
            row.append(self.adjust_node(xml_findone(node, node_name)))
            rows.append(self.sanity_check_node_row(node, row))
            row = []

        yield SheetData(
            sheet_name=self.display_name,
            header_row="name,data".split(","),
            data_rows=rows,
            column_widths=self.column_widths,
        )
