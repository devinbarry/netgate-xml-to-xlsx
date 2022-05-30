"""Test base plugin sanitize."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

import pytest
from lxml import etree

from netgate_xml_to_xlsx.plugins.base_plugin import BasePlugin

# IMPORTANT: The lxml parsing converts first element to the 'root'.
null_element = """\
<pfsense>
    <l1>
        <l1.1/>
    </l1>
</pfsense>
"""


one_element = """\
<pfsense>
    <l1>
        <l1.1>TARGET</l1.1>
    </l1>
</pfsense>
"""

multi_element = """\
<pfsense>
    <l1>
        <l1.1>TARGET</l1.1>
        <l1.1>TARGET</l1.1>
    </l1>
</pfsense>
"""


class LocalPlugin(BasePlugin):
    def __init__(
        self,
        display_name: str,
        field_names: str,
        el_paths_to_sanitize: list[str] | None,
    ) -> None:
        super().__init__(
            display_name, field_names, el_paths_to_sanitize=el_paths_to_sanitize
        )

    def run(self, pfsense):
        pass


@pytest.mark.parametrize(
    "name,xml,el_paths",
    (
        ("null_element", null_element, ["l1,l1.1"]),
        ("one_element", one_element, ["pfsense,l1,l1.1"]),
        ("multi_element", multi_element, ["l1,l1.1"]),
    ),
)
def test_sanitize_paths(name, xml: str, el_paths: list[str] | None):
    parsed_xml = etree.XML(xml)
    expected_xml = xml.replace("TARGET", "SANITIZED")
    plugin = LocalPlugin("name", "", el_paths)
    plugin.sanitize(parsed_xml)
    sanitized_xml = etree.tostring(parsed_xml, pretty_print=True).decode("utf8")
    assert sanitized_xml == expected_xml
