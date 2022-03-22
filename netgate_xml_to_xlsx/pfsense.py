"""PfSense class."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import argparse
from collections import OrderedDict
import os
from pathlib import Path
import sys

from openpyxl import Workbook
from openpyxl.styles.alignment import Alignment
from openpyxl.styles import Border, Font, NamedStyle, PatternFill, Side
import xmltodict

from .elements import (
    format_privs,
    get_element,
    load_standard_nodes,
    rules_destination,
    rules_source,
    rules_username_time,
    sanitize_xml,
    unescape,
    updated_or_created,
)

from .spreadsheet import write_ss_row, sheet_header, sheet_footer


class PfSense:
    """Handle all pfSense parsing and conversion."""

    def __init__(self, args: argparse.Namespace, in_filename: str) -> None:
        """
        Initialize and load XML.

        Technically a bit too much work to do in an init (since it can fail).
        """
        self.args = args
        self.in_file = Path(in_filename)
        self.raw_xml: dict = {}
        self.pfsense: dict = {}
        self.workbook: Workbook = Workbook()

        # ss_filename is expected to be overwritten by
        self.ss_filename = "output.xlxs"
        self._init_styles()
        self.default_alignment = Alignment(wrap_text=True, vertical="top")

        self._load()

    def _init_styles(self) -> None:
        """Iniitalized worksheet styles."""
        xlsx_header_font = Font(name="Calibri", size=16, italic=True, bold=True)
        xlsx_body_font = Font(name="Calibri", size=16)
        xlsx_footer_font = Font(name="Calibri", size=12, italic=True)

        body_border = Border(
            bottom=Side(border_style="dotted", color="00000000"),
            top=Side(border_style="dotted", color="00000000"),
            left=Side(border_style="dotted", color="00000000"),
            right=Side(border_style="dotted", color="00000000"),
        )

        alignment = Alignment(wrap_text=True, vertical="top")

        header = NamedStyle(name="header")
        header.alignment = alignment
        header.fill = PatternFill(
            "lightTrellis", fgColor="00339966"
        )  # fgColor="000000FF")  #fgColor="0000FF00")
        header.font = xlsx_header_font
        header.border = Border(
            bottom=Side(border_style="thin", color="00000000"),
            top=Side(border_style="thin", color="00000000"),
            left=Side(border_style="dotted", color="00000000"),
            right=Side(border_style="dotted", color="00000000"),
        )

        normal = NamedStyle(name="normal")
        normal.alignment = alignment
        normal.border = body_border
        normal.fill = PatternFill("solid", fgColor="FFFFFFFF")
        normal.font = xlsx_body_font

        footer = NamedStyle("footer")
        footer.alignment = Alignment(wrap_text=False, vertical="top")
        footer.border = body_border
        normal.fill = PatternFill("solid", fgColor="FFFFFFFF")
        footer.font = xlsx_footer_font

        self.workbook.add_named_style(header)
        self.workbook.add_named_style(normal)
        self.workbook.add_named_style(footer)

    def _load(self) -> OrderedDict:
        """Load and parse Netgate xml firewall configuration.

        Return pfsense keys.
        """
        self.raw_xml = self.in_file.read_text(encoding="utf-8")
        data = xmltodict.parse(self.raw_xml)
        self.pfsense = data["pfsense"]

    def _write_sheet(
        self,
        *,
        name: str,
        field_names: list[str],
        column_widths: list[int],
        rows: list[list],
    ):
        sheet = self.workbook.create_sheet(name)
        sheet_header(sheet, field_names, column_widths)

        # Define starting row num in case there are no rows to display.
        row_num = 2
        for row_num, row in enumerate(rows, start=row_num):
            write_ss_row(sheet, row, row_num)
        sheet_footer(sheet, row_num)

    def sanitize(self) -> None:
        """
        Sanitize the raw XML and save as original filename + '-sanitized'.

        The Netgate configuration file XML is well ordered and thus searchable via regex.
        """
        self.raw_xml = sanitize_xml(self.raw_xml)

        # Save sanitized XML
        parts = os.path.splitext(self.in_file)
        if len(parts) == 1:
            out_path = Path(f"{parts[0]}-sanitized")
        else:
            out_path = Path(f"{parts[0]}-sanitized{parts[1]}")
        out_path.write_text(self.raw_xml, encoding="utf-8")
        print(f"Sanitized file written: {out_path}.")

        # Delete the unsanitized file.
        self.in_file.unlink()
        print(f"Deleted original file: {self.in_file}.")

    def save(self) -> None:
        """Delete empty first sheet and then save Workbook."""
        sheets = self.workbook.sheetnames
        del self.workbook[sheets[0]]
        out_path = self.args.output_dir / self.ss_filename
        self.workbook.save(out_path)

    def system(self) -> None:
        """
        Sheet with system-level information.

        Only showing interesting information (at least to me at the moment).
        """
        rows = []
        field_names = "name,value".split(",")
        column_widths = [int(x) for x in "40,40".split(",")]

        node = self.pfsense
        for key in "version,lastchange".split(","):
            rows.append([key, unescape(node.get(key, ""))])

        # Check version number.
        if (version := int(float(rows[0][1]))) != 21:
            assert version is not None
            print(
                f"Warning: File uses version {version}.x. "
                "Script is only tested on version 21 XML formats."
            )

        node = self.pfsense["system"]
        for key in "optimization,hostname,domain,timezone".split(","):
            rows.append([key, unescape(node.get(key, ""))])

        # Ugly getting this twice.
        self.ss_filename = (
            f"""{node.get("hostname", "")}.{node.get("domain", "")}.xlsx"""
        )

        time_servers = "\n".join(node.get("timeservers", "").split(" "))
        rows.append(["timeservers", time_servers])

        rows.append(["bogons", get_element(node, "bogons,interval", "TBD")])
        rows.append(["ssh", get_element(node, "ssh,enabled", "TBD")])
        rows.append(["dnsserver", "\n".join(node.get("dnsserver", ""))])

        self._write_sheet(
            name="System",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def system_groups(self) -> None:
        """
        Sheet with system.group information.

        Multiple groups with multiple privileges.
        Display privileges alpha sorted.
        """
        rows = []
        field_names = "name,description,scope,gid,priv".split(",")
        column_widths = [int(x) for x in "40,80,20,20,80".split(",")]

        nodes = get_element(self.pfsense, "system,group")
        if not nodes:
            return
        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]

        nodes.sort(key=lambda x: x["name"].casefold())

        for node in nodes:
            row = []
            for key in field_names:
                value = unescape(node.get(key, ""))
                if key == "priv":
                    value = format_privs(value)
                row.append(value)
            rows.append(row)

        self._write_sheet(
            name="System Groups",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def system_users(self) -> None:
        """
        Sheet with system.user information.

        Not all fields displayed as # column on dashboard and webguicss are uninteresting
        (at least to me at the moment).
        """
        rows = []
        field_names = "name,descr,scope,expires,ipsecpk,uid,cert".split(",")
        column_widths = [int(x) for x in "40,60,20,20,20,10,60".split(",")]

        nodes = get_element(self.pfsense, "system,user")
        if not nodes:
            return
        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]
        nodes.sort(key=lambda x: x["name"].casefold())

        for node in nodes:
            row = []
            for key in field_names:
                row.append(unescape(node.get(key, "")))
            rows.append(row)

        self._write_sheet(
            name="System Users",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def aliases(self) -> None:
        """Create the aliases sheet."""
        rows = []
        field_names = "name,type,address,url,updatefreq,descr,detail".split(",")
        column_widths = [int(x) for x in "40,40,40,80,20,80,80".split(",")]

        nodes = get_element(self.pfsense, "aliases,alias")
        if not nodes:
            return
        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]
        nodes.sort(key=lambda x: x["name"].casefold())

        rows = load_standard_nodes(nodes=nodes, field_names=field_names)
        self._write_sheet(
            name="Aliases",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def rules(self) -> None:
        """Create the rules sheet."""
        rows = []
        field_names = (
            "id,tracker,type,interface,ipprotocol,tag,tagged,max,max_src_nodes,"
            "max_src-conn,max-src-states,statetimeout,statetype,os,source,destination,"
            "log,descr,created,updated"
        ).split(",")
        column_widths = [
            int(x)
            for x in (
                "10,20,10,15,15,10,10,10,20,20,20,20,30,50,50,50,10,80,85,85".split(",")
            )
        ]
        source_index = field_names.index("source")
        destination_index = field_names.index("destination")
        created_index = field_names.index("created")
        updated_index = field_names.index("updated")

        nodes = get_element(self.pfsense, "filter,rule")
        if not nodes:
            return
        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]
        # Sort rules so that latest changes are at the top.
        nodes.sort(
            key=updated_or_created,
            reverse=True,
        )

        for node in nodes:
            row = []
            for field_name in field_names:
                row.append(unescape(node.get(field_name, "")))
            row = ["" if x is None else x for x in row]

            row[source_index] = rules_source(row, source_index)
            row[destination_index] = rules_destination(row, destination_index)
            row[created_index] = rules_username_time(row, created_index)
            row[updated_index] = rules_username_time(row, updated_index)

            rows.append(row)

        self._write_sheet(
            name="Rules",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def interfaces(self) -> None:
        """
        Document all interfaces.

        TODO: Review blockbogons. Does existence == On?
        """
        rows = []
        # Prepend 'name' before calling _write_sheet.
        field_names = (
            "descr,alias-address,alias-subnet,spoofmac,enable,"
            "blockpriv,blockbogons,ipaddr,subnet,gateway"
        ).split(",")
        column_widths = [int(x) for x in "20,40,20,20,20,20,20,20,20,40".split(",")]

        # Don't sort interfaces. Want them in the order they are encountered.
        # Interfaces is an OrderedDict
        nodes = get_element(self.pfsense, "interfaces")
        if not nodes:
            return
        # In this case we want a single OrderedDict.
        # Remove 'name' from the field_names as we're going to replace that with the key.
        del field_names[0]

        for name, node in nodes.items():
            row = [name]
            for field_name in field_names:
                row.append(unescape(node.get(field_name, "")))
            rows.append(row)
        field_names.insert(0, "name")

        self._write_sheet(
            name="Interfaces",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def gateways(self) -> None:
        """Document gateways."""
        rows = []
        # Append 'defaultgw4' and 'defaultgw6' before displaying.
        field_names = (
            "name,descr,interface,gateway,weight,ipprotocol,monitor_disable"
        ).split(",")
        column_widths = [int(x) for x in "20,40,20,20,10,30,30,20,20".split(",")]

        # Load default IPV4 and IPV6 gateways.
        # Don't want "None" for default gateway.
        default_gw4 = get_element(self.pfsense, "gateways,defaultgw4", "")
        default_gw6 = get_element(self.pfsense, "gateways,defaultgw6", "")

        # Which column has the gateway name.
        gw_name_col = 0

        # Don't sort nodes for now. Leave in order found.
        nodes = get_element(self.pfsense, "gateways,gateway_item")
        if not nodes:
            return
        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]

        for node in nodes:
            row = []
            for field_name in field_names:
                try:
                    row.append(unescape(node.get(field_name, "")))
                except AttributeError as err:
                    print(err)
                    sys.exit(-1)
            if default_gw4 == row[gw_name_col]:
                row.append("YES")
            else:
                row.append(None)
            if default_gw6 == row[gw_name_col]:
                row.append("YES")
            else:
                row.append(None)
            rows.append(row)

        field_names.extend(["defaultgw4", "defaultgw6"])
        self._write_sheet(
            name="Gateways",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def openvpn_server(self) -> None:
        """Document all OpenVPN servers."""
        rows = []
        field_names = (
            "vpnid,disable,mode,protocol,dev_mode,interface,ipaddr,local_port,"
            "description,custom_options,shared_key,digest,engine,tunnel_network,"
            "tunnel_networkv6,remote_network,remote_networkv6,gwredir,gwredir6,"
            "local_network,local_networkv6,maxclients,compression,compression_push,passtos,"
            "client2client,dynamic_ip,topology,serverbridge_dhcp,serverbridge_interface,"
            "serverbridge_routegateway,serverbridge_dhcp_start,serverbridge_dhcp_end,"
            "username_as_common_name,exit_notify,sndrcvbuf,netbios_enable,netbios_ntype,"
            "netbios_scope,create_gw,verbosity_level,ncp_enable,ping_method,keepalive_interval,"
            "keepalive_timeout,ping_seconds,ping_push,ping_action,ping_action_seconds,"
            "ping_action_push,inactive_seconds,data_ciphers,data_ciphers_fallback"
        ).split(",")
        column_widths = [
            int(x)
            for x in (
                "20,20,20,20,20,30,20,20,30,20,"  # 10
                "40,20,20,30,30,30,30,20,20,30,"  # 20
                "20,20,20,30,20,20,20,20,40,40,"  # 30
                "40,40,40,50,20,20,20,20,20,20,"  # 40
                "20,20,20,30,30,20,20,20,30,30,"  # 50
                "20,20,50"
            ).split(",")
        ]

        # Don't sort OpenVPN Servers. Want them in the order they are encountered.
        # Interfaces is an OrderedDict
        nodes = get_element(self.pfsense, "openvpn,openvpn-server")
        if not nodes:
            return
        if isinstance(nodes, OrderedDict):
            nodes = [nodes]

        rows = load_standard_nodes(nodes=nodes, field_names=field_names)
        self._write_sheet(
            name="OpenVPN Server",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def installed_packages(self) -> None:
        """Document all installed packages. Sort by name."""
        rows = []
        field_names = (
            "name,internal_name,descr,version,configuration_file,include_file,"
            "website,pkginfolink,filter_rule_function"
        ).split(",")
        column_widths = [int(x) for x in "40,40,50,20,50,50,80,80,50".split(",")]

        nodes = get_element(self.pfsense, "installedpackages,package")
        if not nodes:
            return
        if isinstance(nodes, OrderedDict):
            # Only found one.
            nodes = [nodes]
        nodes.sort(key=lambda x: x["name"].casefold())

        rows = load_standard_nodes(nodes=nodes, field_names=field_names)
        self._write_sheet(
            name="Installed Packages",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )

    def unbound(self) -> None:
        """Document unbound elements."""
        rows = []

        # field names for acquiring information
        field_names = (
            "enable,active_interface,outgoing_interface,custom_options,custom_options,"
            "hideversion,dnssecstripped,port,system_domain_local_zone_type,sslcertref,"
            "dnssec,tlsport"
        ).split(",")
        column_widths = [
            int(x) for x in "20,20,20,20,20,20,20,20,20,20,20,20,80,80".split(",")
        ]
        node = get_element(self.pfsense, "unbound")
        rows = load_standard_nodes(nodes=node, field_names=field_names)

        # Only expect one row returned.
        assert len(rows) <= 1

        if not rows:
            # No unbound values. Nothing to output.
            return

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
        field_names.extend(("domainoverrides", "hosts"))

        self._write_sheet(
            name="Unbound",
            field_names=field_names,
            column_widths=column_widths,
            rows=rows,
        )
