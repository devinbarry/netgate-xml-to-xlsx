"""Netgate module testing."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from importlib.metadata import version


def test_version_exists():
    """Confirm we can access version."""
    version("netgate_xml_to_xlsx")
