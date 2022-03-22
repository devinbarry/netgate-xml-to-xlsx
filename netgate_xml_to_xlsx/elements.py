"""Extract elements from XML."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict
import datetime
import html
import ipaddress
import re

from .errors import UnknownField


def sanitize_xml(raw_xml: str) -> str:
    """Sanitize the xml."""
    regexes = (
        re.compile("(<bcrypt-hash>).*?(</bcrypt-hash>)"),
        re.compile("(<radius_secret>).*?(</radios_secret>)"),
        re.compile("(<lighttpd_ls_password>).*?(</lighttpd_ls_password>)"),
        re.compile("(<stats_password>).*?(</stats_password>)"),
        re.compile("(<password>).*?(</password>)"),
        re.compile("(<tls>).*?(</tls>)"),
    )
    for regex in regexes:
        raw_xml = regex.sub(r"\1SANITIZED\2", raw_xml)
    return raw_xml


def unescape(value: str | None) -> str | None:
    """Unescape XML entities."""
    if value is None:
        return value
    assert value is not None

    return html.unescape(value)


def adjust_field_value(*, field_name: str, value: str | None) -> str | None:
    """Make adjustments based on field_name."""
    if value is None:
        return None
    assert value is not None

    # Convert XML escape codes
    assert value is not None

    if field_name == "descr":
        value = value.replace("<br />", "\n")
        lines = [x.strip() for x in value.split("\n")]
        return "\n".join(lines)

    # May be specific only to our environment. Details divided by ||
    if field_name == "detail":
        value = value.replace("||", "\n")
        lines = [x.strip() for x in value.split("\n")]
        return "\n".join(lines)

    if (
        field_name
        in "data_ciphers,local_network,local_networkv6,remote_network,remote_networkv6".split(
            ","
        )
    ):
        values = [x.strip() for x in value.split(",")]
        return "\n".join(values)

    if field_name in "custom_options".split(","):
        values = [x.strip() for x in value.split(";")]
        return "\n".join(values)

    if field_name in "shared_key".split(",") and len(value) > 30:
        # Sanitize the value
        return f"{value[:20]}\n......\n{value[-20:]}"

    if field_name == "address":
        return nice_address_sort(value)

    return value


def load_standard_nodes(
    *, nodes: OrderedDict | list | None, field_names: list[str]
) -> list[list]:
    """Load nodes that do not require special handling into rows."""
    rows = []
    if nodes is None:
        return rows
    assert nodes is not None

    # If a single dictionary, put it into a list
    if isinstance(nodes, OrderedDict):
        nodes = [nodes]

    for node in nodes:
        if node is None:
            # blank <openvpn-server></openvpn-server> for example.
            continue
        row = []
        for field_name in field_names:
            row.append(
                adjust_field_value(
                    field_name=field_name, value=node.get(field_name, "")
                )
            )
        rows.append(row)
    return rows


def get_element(
    root_node: OrderedDict, els: list[str] | str, default=""
) -> OrderedDict | str | None:
    """
    Iterate down the tree and return path.

    Use try/except for missing keys as None is a valid return value.
    """
    if isinstance(els, str):
        els = els.split(",")

    if root_node is None:
        return default

    node = root_node
    try:
        for el in els:
            node = node[el]
            if node is None:
                return default
        return node
    except KeyError:
        return default


def format_privs(privs: list[tuple[str, str | None]] | str | None) -> str | None:
    """Format privileges into a string paragraph.

    Single privileges are presented as a string.
    Multiple privileges as a list of string.
    """
    if privs is None:
        return None
    assert privs is not None

    if isinstance(privs, str):
        return privs

    privs.sort(key=lambda x: x.casefold())
    return "\n".join(privs)


def updated_or_created(node: OrderedDict) -> str:
    """Return "updated" or "created" value, or ""."""
    if updated := get_element(node, "updated,time"):
        return updated
    return get_element(node, "created,time")


def rules_username_time(row: list, field_index: int) -> str:
    """Extract username/time from created or updated."""
    field = row[field_index]

    # Not all records have an 'updated' so return "" if field is missing.
    if not field:
        return ""
    username = field.get("username")
    username = username if username is not None else ""

    time = field.get("time")
    if time is not None:
        timestamp = datetime.datetime.fromtimestamp(int(time)).strftime(
            "%Y-%m-%d %H-%M-%S"
        )
    else:
        timestamp = ""
    return f"{username} {timestamp}"


def rules_destination(row: list, field_index: int) -> str:
    """Extract destination address and port."""
    destination = row[field_index]
    if "any" in destination:
        return "any"

    if "network" in destination:
        address = destination["network"]
    elif "address" in destination:
        address = destination["address"]
    else:
        raise UnknownField(
            f"Destination missing address or network: {destination.keys()}"
        )

    try:
        port = destination["port"]
        return f"{address}:{port}"
    except KeyError:
        # Aliases don't always have ports.
        return address

    return f"{address}:{port}"


def rules_source(row: list, field_index: int) -> str:
    """Extract source or 'any'."""
    source = row[field_index]
    if "any" in source:
        return "any"

    if "address" in source:
        return source["address"]

    if "network" in source:
        return source["network"]

    raise UnknownField(f"Unknown filter/rules/source field: {source.keys()}")


def nice_address_sort(data: str) -> str:
    """
    Sort addresses that may consist of domains and IPv4/v6 addresses.

    Not all 'address' fields are proper IPs and domains.
    some are ports.

    TODO: Filter IPV4 and IPv6 separately.

    """
    try:
        addresses = [x.strip() for x in data.split(" ")]
        numeric = [x for x in addresses if len(x) > 1 and x[0] in ("0123456789")]
        numeric.sort(key=lambda x: ipaddress.ip_address(x.split("/")[0]))

        non_numeric = [
            x for x in addresses if len(x) > 1 and x[0] not in ("0123456789")
        ]
        non_numeric.sort(key=str.casefold)

        result = []
        result.extend(non_numeric)
        result.extend(numeric)
        return "\n".join(result)
    except (TypeError, ValueError):
        # Not an actual address (ValueError) or mixture of IPV4 and IPV6 (TypeError).
        return data
