"""HAProxy plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

from ..base_plugin import BasePlugin, SheetData, split_commas
from ..support.elements import (
    get_element,
    load_standard_nodes,
)


def _haproxy_overview(nodes: OrderedDict) -> SheetData:
    """Top-level haproxy elements.

    Return two columns: Name/Value.
    """
    field_names = (
        "enable,configversion,nbproc,nbthread,maxconn,carpdev,"
        "logfacility,loglevel,log-send-hostname,remotesyslog,"
        "localstats_refreshtime,localstats_sticktable_refreshtime"
        ",dns_resolvers,resolver_retries,resolver_timeoutretry,resolver_holdvalid,"
        "hard_stop_after,ssldefaultdhparam,"
        "email_mailers,email_level,email_myhostname,email_from,email_to,"
        "files,advanced"
    ).split(",")
    column_widths = "50,80"

    rows = load_standard_nodes(nodes=nodes, field_names=field_names)
    rows = list(zip(field_names, rows[0]))

    return SheetData(
        sheet_name="HAProxy",
        header_row=split_commas("Name,Value"),
        data_rows=rows,
        column_widths=split_commas(column_widths),
    )


class Plugin(BasePlugin):
    """
    Gather HAProxy data.

    Generates multiple sheets of data:
      * Overview
      * ha_backends
      * ha_pools
    """

    def __init__(
        self,
        display_name="HAProxy",
        field_names: str = FIELD_NAMES,
        column_widths: str = WIDTHS,
    ):
        """Initialize."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """Document unbound elements."""
        super().run(pfsense)

        nodes = get_element(pfsense, "installedpackages,haproxy")

        yield _haproxy_overview(nodes)
