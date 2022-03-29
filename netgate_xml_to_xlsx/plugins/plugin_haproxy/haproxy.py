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

    yield SheetData(
        sheet_name="HAProxy",
        header_row=split_commas("Name,Value"),
        data_rows=rows,
        column_widths=split_commas(column_widths),
    )


def _haproxy_backends(nodes: OrderedDict | list[OrderedDict]) -> SheetData:
    """HAProxy backends can have 1 or more items."""
    rows = []
    # Add a_extaddr before returning
    field_names = split_commas(
        "name,status,type,primary_frontend,backend_serverpool,"  # 5
        "forwardfor,dontlognull,log-detailed,socket-stats,a_extaddr,"  # 10
        "ha_certificate,clientcert_ca,clientcert_crl,a_actionitems,a_errorfiles,"  # 15
        "dcertadv,ssloffloadcert,advanced,ha_acls,httpclose"  # 20
    )

    column_widths = split_commas(
        "20,20,20,25,25,20,20,20,20,40,20,20,20,20,20,80,20,20,20,20,20"
    )

    if isinstance(nodes, OrderedDict):
        nodes = [nodes]

    for node in nodes:
        row = load_standard_nodes(nodes=node, field_names=field_names)
        assert len(row) == 1
        row_dict = dict(zip(field_names, row[0]))

        a_extaddr = ""
        a_extaddr_nodes = get_element(node, "a_extaddr,item")
        if a_extaddr_nodes:
            a_ext_rows = load_standard_nodes(
                nodes=a_extaddr_nodes,
                field_names=split_commas("extaddr,extaddr_port,extaddr_ssl,_index"),
            )
            assert len(a_ext_rows) == 1
            a_extaddr += "\n".join(
                [
                    f"{x}: {y}"
                    for x, y in list(
                        zip("addr,port,ssl,_index".split(","), a_ext_rows[0])
                    )
                ]
            )
        row_dict["a_extaddr"] = a_extaddr + "\n"
        rows.append([row_dict[key] for key in field_names])

    yield SheetData(
        sheet_name="HAProxy Backends",
        header_row=field_names,
        data_rows=rows,
        column_widths=column_widths,
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
        field_names: str = "",
        column_widths: str = "",
    ):
        """Ignore field_names and column_widths as we create them individually."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> tuple[str, list[list]]:
        """Document unbound elements."""
        super().run(pfsense)

        haproxy = get_element(pfsense, "installedpackages,haproxy")
        for overview in _haproxy_overview(haproxy):
            yield overview

        backends = get_element(haproxy, "ha_backends,item")
        for backend in _haproxy_backends(backends):
            yield backend
