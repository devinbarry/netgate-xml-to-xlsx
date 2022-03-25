"""Unbound plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

from ..base_plugin import BasePlugin, SheetData
from ..support.elements import (
    get_element,
    load_standard_nodes,
)

FIELD_NAMES = (
    "enable,active_interface,outgoing_interface,custom_options,custom_options,"
    "hideversion,dnssecstripped,port,system_domain_local_zone_type,sslcertref,"
    "dnssec,tlsport"
)
WIDTHS = "20,20,20,20,20,20,20,20,20,20,20,20,80,80"


class Plugin(BasePlugin):
    """Gather data Unbound."""

    def __init__(
        self,
        display_name="Unbound",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ):
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """Document unbound elements."""
        rows = super().run(pfsense)

        node = get_element(pfsense, "unbound")
        rows = load_standard_nodes(nodes=node, field_names=self.field_names)

        # Only expect one row returned.
        assert len(rows) <= 1

        if not rows:
            # No unbound values. Nothing to output.
            return []

        # Load multi-element items.
        domain_overrides_fieldnames = "domain,ip,descr,tls_hostname".split(",")
        domain_overrides = load_standard_nodes(
            nodes=get_element(node, "domainoverrides"),
            field_names=domain_overrides_fieldnames,
        )

        hosts_fieldnames = "host,domain,ip,descr,aliases".split(",")
        hosts = load_standard_nodes(
            nodes=get_element(node, "hosts"), field_names=hosts_fieldnames
        )

        subrows = []
        for domain_override in domain_overrides:
            zipped = OrderedDict(zip(domain_overrides_fieldnames, domain_override))
            subrows.append(
                "\n".join([f"{key}: {value}" for key, value in zipped.items()])
            )

        rows[0].append("\n\n".join(subrows))

        subrows = []
        for host in hosts:
            zipped = OrderedDict(zip(hosts_fieldnames, host))
            subrows.append(
                "\n".join([f"{key}: {value}" for key, value in zipped.items()])
            )

        rows[0].append("\n\n".join(subrows))

        # Add the two subrows columns to the field names.
        self.field_names.extend(("domainoverrides", "hosts"))

        yield SheetData(
            sheet_name=self.display_name,
            header_row=self.field_names,
            data_rows=rows,
            column_widths=self.column_widths,
        )
