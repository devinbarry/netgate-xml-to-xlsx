"""PfSense class."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import logging
import os
from pathlib import Path
from typing import cast

from lxml import etree  # nosec

from netgate_xml_to_xlsx.mytypes import Node

from .formats import HtmlFormat, TextFormat, XlsxFormat
from .plugin_tools import discover_plugins
from .plugins.support.elements import sanitize_xml


class PfSense:
    """Handle all pfSense parsing and conversion."""

    def __init__(self, config: dict, in_filename: str) -> None:
        """
        Initialize and load XML.

        Technically a bit too much work to do in an init (since it can fail).
        """
        self.config = config
        self.args = config["args"]
        self.input_path = (input_path := Path(in_filename))
        self.raw_xml: str = ""
        self.parsed_xml: Node = None

        self.output_path = self._get_output_path(input_path)

        self.plugins = discover_plugins()
        self.output_format = None
        self.logger = logging.getLogger()

        self._load()

    def _get_output_path(self, input_path: Path) -> Path:
        """Generate output path based on args and in_filename."""
        self.output_path = cast(Path, self.args.output_dir) / Path(
            f"{input_path.name}.{self.args.output_format}"
        )

        return self.output_path

    def _sanity_check_root_node(self) -> None:
        """Check for unknown root elements."""
        expected_nodes = set(
            (
                "version,lastchange,revision,aliases,ca,"
                "cert,cron,dhcpd,dhcpdv6,diag,"
                "dhcrelay,dhcrelay6,"
                "dnshaper,filter,gateways,hasync,ifgroups,"
                "installedpackages,interfaces,ipsec,nat,notifications,"
                "ntpd,openvpn,ovpnserver,ppps,proxyarp,"
                "rrd,shaper,snmpd,sshdata,staticroutes,"
                "switches,sysctl,syslog,system_groups,system_users,"
                "system,unbound,virtualip,vlans,widgets,"
                "wizardtemp,wol"
            ).split(",")
        )
        unknown = []
        for child in self.parsed_xml:
            if child.tag not in expected_nodes:
                unknown.append(child.tag)
        if len(unknown):
            self.logger.warning(f"""Unknown root node(s): {",".join(unknown)}""")

    def _load(self) -> None:
        """Load and parse Netgate xml firewall configuration.

        Return pfsense keys.
        """
        self.raw_xml = self.input_path.read_text(encoding="utf-8")
        self.parsed_xml = etree.XML(self.raw_xml)
        self._sanity_check_root_node()

    def sanitize(self, plugins_to_run) -> None:
        """
        Sanitize the raw XML and save as original filename + '-sanitized'.

        The Netgate configuration file XML is well ordered and thus searchable via regex.

        Parse the XML into a tree and call the individual plugin sanitizers.
        Call the individual plugin sanitizers.

        Args:
            plugins_to_run: List of active plugin names.

        """
        # Run generic sanitize.
        self.raw_xml = sanitize_xml(self.raw_xml)

        # Parse xml for plugin sanitizing.
        self.parsed_xml = etree.XML(self.raw_xml)

        for plugin_name in plugins_to_run:
            plugin = self.plugins[plugin_name]
            plugin.sanitize(self.parsed_xml)

        # Pretty format XML.
        self.raw_xml = etree.tostring(self.parsed_xml, pretty_print=True).decode("utf8")

        # Save sanitized XML
        parts = os.path.splitext(self.input_path)
        if len(parts) == 1:
            out_path = Path(f"{parts[0]}-sanitized")
        else:
            out_path = Path(f"{parts[0]}-sanitized{parts[1]}")
        out_path.write_text(f"{self.raw_xml}", encoding="utf-8")
        self.logger.info(f"Sanitized file written: {out_path}.")

        # Delete the unsanitized file.
        self.input_path.unlink()
        self.logger.info(f"Deleted original file: {self.input_path}.")

    def run_all_plugins(self, plugin_names: list[str]) -> None:
        """Run each plugin in order."""
        formats = {"txt": TextFormat, "xlsx": XlsxFormat, "html": HtmlFormat}
        self.output_format = formats[self.args.output_format](
            ctx={"input_path": self.input_path, "output_path": self.output_path}
        )
        self.output_format.start()

        for plugin_name in plugin_names:
            self.logger.verbose(f"Plugin: {plugin_name}")
            self.run_plugin(plugin_name)

        self.output_format.finish()

    def run_plugin(self, plugin_name: str) -> None:
        """Run specific plugin and generate output."""
        plugin = self.plugins[plugin_name]
        if plugin_name.startswith("report"):
            for sheet_data in plugin.run(self.parsed_xml, self.plugins):
                self.output_format.out(sheet_data)
        else:
            for sheet_data in plugin.run(self.parsed_xml):
                self.output_format.out(sheet_data)
