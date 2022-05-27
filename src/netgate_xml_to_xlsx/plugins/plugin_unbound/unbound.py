"""Unbound plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.errors import NodeError
from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

FIELD_NAMES = (
    "enable,hosts,domainoverrides,active_interface,outgoing_interface,"
    "custom_options,custom_options,hideversion,dnssecstripped,port,"
    "system_domain_local_zone_type,sslcertref,dnssec,tlsport,hideidentity,"
    "forwarding"
)
WIDTHS = "10,50,50,20,20,20,20,20,20,20,40,20,20,20,20,20"


class Plugin(BasePlugin):
    """Gather data Unbound."""

    def __init__(
        self,
        display_name: str = "Unbound",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def adjust_node(self, node: Node) -> str:
        """Custom node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "domainoverrides" | "hosts":
                if node.tag == "domainoverrides":
                    field_names = "domain,ip,tls_hostname,descr".split(",")
                else:
                    # hosts
                    field_names = "host,domain,ip,aliases,descr".split(",")

                result = []
                for field_name in field_names:
                    child = xml_findone(node, field_name)
                    if child is None:
                        value = ""
                    else:
                        value = child.text or ""
                    result.append(f"{field_name}: {value}")
                return "\n".join(result)

            case "hideidentity" | "hideversion" | "dnssecstripped" | "dnssec" | "tlsport" | "forwarding":  # NOQA
                # Existence of tag indicates 'yes'.
                # Sanity check there is no text.
                if node.text:
                    raise NodeError(
                        f"Node {node.tag} has unexpected text: {node.text}."
                    )

                return "YES"

        return super().adjust_node(node)

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document unbound elements.  One row."""
        rows = []

        node = xml_findone(parsed_xml, "unbound")
        if node is None:
            return

        self.report_unknown_node_elements(node)
        row = []

        for field_name in self.field_names:
            value = self.adjust_nodes(xml_findall(node, field_name))

            row.append(value)

        self.sanity_check_node_row(node, row)
        rows.append(row)

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
