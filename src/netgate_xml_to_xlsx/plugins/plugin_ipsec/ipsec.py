"""IPSEC plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from typing import Generator

from netgate_xml_to_xlsx.mytypes import Node

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import unescape, xml_findall, xml_findone

TOP_FIELD_NAMES = "async_crypto,logging,uniqueids,vtimaps"
TOP_WIDTHS = "30,30,30,30"

CLIENT_FIELDNAMES = ""
CLIENT_WIDTHS = ""

PHASE1_FIELDNAMES = (
    "descr,authentication_method,caref,certref,closeaction,"
    "dpd_delay,dpd_maxfail,encryption,ikeid,iketype,"
    "interface,lifetime,mobike,myid_data,myid_type,"
    "nat_traversal,peerid_data,peerid_type,pre-shared-key,private-key,"
    "protocol,remote-gateway"
)
PHASE1_WIDTHS = (
    "40,30,10,10,20,"  # 5
    "20,20,20,10,10,"  # 10
    "30,10,10,20,20,"  # 15
    "20,20,20,20,20,"  # 20
    "20,30"
)

PHASE2_FIELDNAMES = (
    "descr,encryption-algorithm-option,hash-algorithm-option,ikeid,lifetime,"
    "localid,mode,pfsgroup,pinghost,protocol,"
    "remoteid,reqid,uniqid"
)

PHASE2_WIDTHS = "40,40,30,20,20,20,20,20,20,20,20,20,30"


class Plugin(BasePlugin):
    """Gather data Unbound."""

    def __init__(
        self,
        display_name: str = "IPSEC",
        field_names: str = TOP_FIELD_NAMES,
        column_widths: str = TOP_WIDTHS,
    ) -> None:
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def should_process(self, node: Node) -> bool:
        """
        Should we process the element?

        Element needs to have at least the top number of field name children + 1.
        Netgate will store several empty items.
        This seems like a quick and reasonable check.
        """
        assert node.tag in ("ipsec", "client")
        children = node.getchildren()
        if len(children) < len(self.field_names) + 1:
            return False
        return True

    def adjust_node(self, node: Node) -> str:
        """Local node adjustments."""
        if node is None:
            return ""

        match node.tag:
            case "encryption" | "localid" | "remoteid" | "encryption-algorithm-option":
                return self.wip(node)

            case "encryption-algorithm-option":
                return self.wip(node)

            case "logging":
                cell = []
                children = node.getchildren()
                for child in children:
                    cell.append(f"{child.tag}: {unescape(child.text)}")
                cell.sort()
                return "\n".join(cell)

            case "vtimaps":
                cell = []
                field_names = "reqid,index,ifnum".split(",")
                item_nodes = xml_findall(node, "item")
                for item_node in item_nodes:
                    for field_name in field_names:
                        cell.append(
                            f"{field_name}: {self.adjust_node(xml_findone(item_node, field_name))}"
                        )
                    cell.append("")

                if len(cell) and cell[-1] == "":
                    cell = cell[:-1]

                return "\n".join(cell)

        return super().adjust_node(node)

    def gather_top(self, node: Node) -> list[str]:
        """Gather single row of top-level ipsec data."""
        rows = []

        if node is None or not self.should_process(node):
            return rows

        row = []

        for field_name in self.field_names:
            value = self.adjust_node(xml_findone(node, field_name))

            row.append(value)

        self.sanity_check_node_row(node, row)

        if len(row):
            rows.append(row)

        return rows

    def gather_client(self, node_in: Node) -> list[str]:
        """Not implemented, but check if there's data."""
        if self.should_process(node_in):
            print("WARNING: IPSEC child data found and not processed.")

        return []

    def gather_phase1s(self, node_in: Node) -> list[str]:
        """IPSEC Phase 1 information."""
        rows = []

        phase1_nodes = xml_findall(node_in, "phase1")

        for phase1_node in phase1_nodes:
            row = []
            for field_name in self.field_names:
                row.append(self.adjust_node(xml_findone(phase1_node, field_name)))
            self.sanity_check_node_row(phase1_node, row)
            rows.append(row)
        return rows

    def gather_phase2s(self, node_in: Node) -> list[str]:
        """IPSEC Phase 2 information."""
        rows = []

        phase2_nodes = xml_findall(node_in, "phase2")

        for phase2_node in phase2_nodes:
            row = []
            for field_name in self.field_names:
                row.append(self.adjust_nodes(xml_findall(phase2_node, field_name)))
            self.sanity_check_node_row(phase2_node, row)
            rows.append(row)

        return rows

    def run(self, parsed_xml: Node) -> Generator[SheetData, None, None]:
        """Document unbound elements.  One row."""

        node = xml_findone(parsed_xml, "ipsec")
        if node is None:
            return

        keep_processing = False
        rows = self.gather_top(node)
        if rows is not None and len(rows) > 0:
            keep_processing = True
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.field_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )

        if not keep_processing:
            return

        self.display_name = "IPSEC Client"
        self.field_names = CLIENT_FIELDNAMES.split(",")
        self.column_widths = CLIENT_WIDTHS.split(",")
        rows = self.gather_client(node)
        if rows is not None and len(rows) > 0:
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.field_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )

        self.display_name = "IPSEC Phase 1"
        self.field_names = PHASE1_FIELDNAMES.split(",")
        self.column_widths = PHASE1_WIDTHS.split(",")
        rows = self.gather_phase1s(node)
        if rows is not None and len(rows) > 0:
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.field_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )

        self.display_name = "IPSEC Phase 2"
        self.field_names = PHASE2_FIELDNAMES.split(",")
        self.column_widths = PHASE2_WIDTHS.split(",")
        rows = self.gather_phase2s(node)
        if rows is not None and len(rows) > 0:
            yield SheetData(
                sheet_name=self.display_name,
                header_row=self.field_names,
                data_rows=rows,
                column_widths=self.column_widths,
            )
