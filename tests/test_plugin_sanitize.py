"""Test base plugin sanitize."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

import pytest

from netgate_xml_to_xlsx.plugins.base_plugin import BasePlugin

base = OrderedDict(
    {
        "l1": OrderedDict(
            {
                "l1.1": "one.one",
                "l1.2": "one.two",
                "L1.3": [],
            }
        ),
        "l2": OrderedDict(
            {
                "l2.1": [OrderedDict({"l3": "l_31"}), OrderedDict({"l3": "l_32"})],
            },
        ),
    }
)

l_1_2 = OrderedDict(
    {
        "l1": OrderedDict(
            {
                "l1.1": "one.one",
                "l1.2": "SANITIZED",
                "L1.3": [],
            }
        ),
        "l2": OrderedDict(
            {
                "l2.1": [OrderedDict({"l3": "l_31"}), OrderedDict({"l3": "l_32"})],
            },
        ),
    }
)

l2_3 = OrderedDict(
    {
        "l1": OrderedDict(
            {
                "l1.1": "one.one",
                "l1.2": "one.two",
                "L1.3": [],
            }
        ),
        "l2": OrderedDict(
            {
                "l2.1": [
                    OrderedDict({"l3": "SANITIZED"}),
                    OrderedDict({"l3": "SANITIZED"}),
                ],
            },
        ),
    }
)


class LocalPlugin(BasePlugin):
    def __init__(
        self,
        display_name: str,
        field_names: str,
        column_widths: str,
        el_paths_to_sanitize: list[str] | None,
    ) -> None:
        super().__init__(display_name, field_names, column_widths, el_paths_to_sanitize)

    def run(self, pfsense):
        pass


@pytest.mark.parametrize(
    "name,pfsense,el_paths,expected",
    (
        #   ("none-none", None, ["abc"], None),
        #   ("base-none-base", base, None, base),
        #   ("base-empty-base", base, [], base),
        #   ("base-notfound-base", base, ["abc", "cde"], base),
        #  ("l1-l2", base, ["l1,l1.2"], l_1_2),
        ("l2_3", base, ["l2,l2.1,l3"], l2_3),
    ),
)
def test_sanitize_paths(
    name,
    pfsense: OrderedDict | None,
    el_paths: list[str] | None,
    expected: OrderedDict | None,
):
    plugin = LocalPlugin("name", "", "", el_paths)
    plugin.sanitize(pfsense)
    assert pfsense == expected
