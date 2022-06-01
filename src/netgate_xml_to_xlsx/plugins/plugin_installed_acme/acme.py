"""ACME Certificates Authority plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import xml_findall, xml_findone

NODE_NAMES = "accountkeys,enable,writecerts"


class Plugin(BasePlugin):
    """Gather information."""

    def __init__(
        self,
        display_name: str = "ACME",
        node_names: str = NODE_NAMES,
    ) -> None:
        super().__init__(
            display_name,
            node_names,
            el_paths_to_sanitize=[
                "pfsense,installedpackages,acme,accountkeys,item,accountkey",
                "pfsense,installedpackages,acme,certificates,item,a_domainlist,item,dns_cfcf_key",
                "pfsense,installedpackages,acme,certificates,item,a_domainlist,item,dns_cfcf_token",  # NOQA
            ],
        )

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Gather information."""
        acme_node = xml_findone(parsed_xml, "installedpackages,acme")
        if acme_node is None:
            return

        for sheet in self._overview(acme_node):
            yield sheet

        for sheet in self._certificates(acme_node):
            yield sheet

    def adjust_node(self, node: Node) -> str:
        """Local node adjustment."""
        if node is None:
            return ""

        match node.tag:
            case "a_domainlist":
                self.report_unknown_node_elements(node, "item".split(","))
                node_names = (
                    "name,status,status,method,dns_cfcf_email,dns_cfcf_key,dns_cfcf_token,"
                    "dns_cfcf_account_id,dns_cfcf_zone_id,_index"
                ).split(",")
                item_nodes = xml_findall(node, "item")
                return self.load_cells(item_nodes, node_names)

            case "a_actionlist":
                self.report_unknown_node_elements(node, "item".split(","))
                node_names = "status,command,method,_index".split(",")
                item_nodes = xml_findall(node, "item")
                return self.load_cells(item_nodes, node_names)

            case "accountkeys":
                names = "name,descr,email,acmeserver,renewafter,accountkey".split(",")
                cell = []
                nodes = xml_findall(node, "item")
                for node in nodes:
                    self.report_unknown_node_elements(node, names)
                    cell.append(self.load_cell(node, names))
                    cell.append("")

                if len(cell) > 0 and cell[-1] == "":
                    cell = cell[:-1]
                return "\n".join(cell)

            case "enable":
                # Override sys-level tag.
                return node.text

            case "lastrenewal":
                return self.decode_datetime(node)

        return super().adjust_node(node)

    def _overview(self, node: Node) -> Generator[SheetData, None, None]:
        """Top-level elements."""
        rows = []

        node_names: list[str] = ("enable,accountkeys,writecerts").split(",")

        all_node_names = node_names[:]

        all_node_names.extend("certificates".split(","))
        self.report_unknown_node_elements(node, all_node_names)

        row = []

        for node_name in node_names:
            row.append(self.adjust_node(xml_findone(node, node_name)))

        self.sanity_check_node_row(node, row)
        rows.append(row)

        yield SheetData(
            sheet_name="ACME",
            header_row=node_names,
            data_rows=rows,
        )

    def _certificates(self, node: Node) -> Generator[SheetData, None, None]:
        """Certificates."""
        self.node_names = (
            "name,descr,status,acmeaccount,keylength,keypaste,ocspstaple,dnssleep,renewafter,"
            "lastrenewal,a_actionlist,a_domainlist"
        ).split(",")

        rows = []
        certs_nodes = xml_findall(node, "certificates")
        for certs_node in certs_nodes:
            self.report_unknown_node_elements(certs_node, "item".split(","))
            item_nodes = xml_findall(certs_node, "item")

            for item_node in item_nodes:
                self.report_unknown_node_elements(item_node)
                row = []
                for node_name in self.node_names:
                    row.append(self.adjust_node(xml_findone(item_node, node_name)))

            self.sanity_check_node_row(item_node, row)
            rows.append(row)

        rows.sort()

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.node_names,
            data_rows=rows,
        )
