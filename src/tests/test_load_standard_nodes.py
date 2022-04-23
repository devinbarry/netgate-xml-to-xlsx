"""Test loading standard nodes."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from collections import OrderedDict

import pytest

from netgate_xml_to_xlsx.plugins.support.elements import load_standard_nodes


@pytest.mark.parametrize(
    "nodes,target",
    (
        (
            # Single OrderedDict
            (OrderedDict(field1="one", field2="two")),
            [["one", "two"]],
        ),
        (
            # List of OrderedDicts
            [
                (OrderedDict(field1="one", field2="two")),
                (OrderedDict(field1="three", field2="four")),
                (OrderedDict(field1="five", field2="six")),
            ],
            [
                ["one", "two"],
                ["three", "four"],
                ["five", "six"],
            ],
        ),
    ),
)
def test_load_standard_nodes(nodes, target):
    """Test source nodes as OrderedDict and lists of OrderedDicts.

    Hard code checking for 'field1, field2'.
    """
    result = load_standard_nodes(nodes=nodes, field_names="field1,field2".split(","))
    assert result == target
