"""HAProxy plugin."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict
from typing import Generator, cast

from ..base_plugin import BasePlugin, SheetData, split_commas
from ..support.elements import (
    get_element,
    load_standard_nodes,
)


def _haproxy_overview(nodes: OrderedDict) -> Generator[SheetData, None, None]:
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
        header_row=cast(list[str], split_commas("Name,Value")),
        data_rows=rows,
        column_widths=cast(list[int], split_commas(column_widths)),
    )


def _haproxy_backends(
    nodes: OrderedDict | list[OrderedDict],
) -> Generator[SheetData, None, None]:
    """HAProxy backends can have 1 or more items."""
    rows = []
    field_names = cast(
        list[str],
        split_commas(
            "name,status,type,primary_frontend,backend_serverpool,"  # 5
            "forwardfor,dontlognull,log-detailed,socket-stats,a_extaddr,"  # 10
            "ha_certificate,clientcert_ca,clientcert_crl,a_actionitems,a_errorfiles,"  # 15
            "dcertadv,ssloffloadcert,advanced,ha_acls,httpclose"  # 20
        ),
    )

    column_widths = cast(
        list[int],
        split_commas("20,20,20,25,25,20,20,20,20,40,20,20,20,20,20,80,20,20,20,20,20"),
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


def _haproxy_pools(
    nodes: OrderedDict | list[OrderedDict],
) -> Generator[SheetData, None, None]:
    """HAProxy pools."""
    rows = []

    field_names = cast(
        list[str],
        split_commas(
            "name,id,servers,check_type,checkinter,log-health-checks,httpcheck_method,"
            "balance,balance_urilen,balance_uridepth,balance_uriwhole,"
            "a_acl,a_actionitems,errorfiles,advanced,advanced_backend,"
            "transparent_clientip,transparent_interface,"
            "monitor_uri,monitor_httpversion,monitor_username,monitor_domain,"
            "monitor_agentport,agent_check,agent_port,agent_port,"
            "connection_timeout,server_timeout,retries,"
            "stats_enabled,stats_username,stats_password,stats_uri,stats_scope,stats_realm,"
            "stats_admin,stats_node,stats_desc,stats_refresh,"
            "persist_stick_expire,persist_stick_tablesize,persist_stick_length,"
            "persist_stick_cookiename,persist_sticky_type,persist_cookie_enabled,"
            "persist_cookie_name,persist_cookie_mode,persist_cookie_cachable,"
            "persist_cookie_postonly,persist_cookie_httponly,persist_cookie_secure,"
            "haproxy_cookie_maxidle,haproxy_cookie_maxlife,haproxy_cookie_domains,"
            "haproxy_cookie_dynamic_cookie_key,strict_transport_security,"
            "cookie_attribute_secure,email_level,email_to"
        ),
    )
    column_widths = cast(
        list[int],
        split_commas(
            "20,20,80,20,20,30,25,20,20,25,"
            "25,20,20,20,20,25,25,30,20,25,"
            "25,25,20,25,20,20,20,25,20,20,"
            "25,30,25,30,25,40,25,25,30,25,"
            "30,30,30,30,30,30,30,30,30,30,"
            "30,30,30,30,30,30,30,20,20"
        ),
    )

    if isinstance(nodes, OrderedDict):
        nodes = [nodes]

    for node in nodes:
        row = load_standard_nodes(nodes=node, field_names=field_names)
        assert len(row) == 1
        row_dict = dict(zip(field_names, row[0]))

        ha_servers = ""
        server_nodes = get_element(node, "ha_servers,item")
        server_fieldnames = split_commas(
            "name,status,address,port,ssl,checkssl,id,_index"
        )
        for server_node in server_nodes:
            server_rows = load_standard_nodes(
                nodes=server_node, field_names=server_fieldnames
            )
            assert len(server_rows) == 1

            ha_servers += "\n".join(
                [f"{x}: {y}" for x, y in list(zip(server_fieldnames, server_rows[0]))]
            )
            ha_servers += "\n\n"
        row_dict["servers"] = ha_servers
        rows.append([row_dict[key] for key in field_names])

    yield SheetData(
        sheet_name="HAProxy Pools",
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
        display_name: str = "HAProxy",
        field_names: str = "",
        column_widths: str = "",
    ) -> None:
        """Ignore field_names and column_widths as we create them individually."""
        super().__init__(display_name, field_names, column_widths)

    def run(self, pfsense: OrderedDict) -> Generator[SheetData, None, None]:
        """Document unbound elements."""
        rows: list[SheetData] = []

        haproxy = get_element(pfsense, "installedpackages,haproxy")
        for overview in _haproxy_overview(haproxy):
            yield overview

        backends = get_element(haproxy, "ha_backends,item")
        for backend in _haproxy_backends(backends):
            yield backend

        pools = get_element(haproxy, "ha_pools,item")
        for pool in _haproxy_pools(pools):
            yield pool
