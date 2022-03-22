"""Test XML sanitizing."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import pytest

from netgate_xml_to_xlsx.elements import sanitize_xml


@pytest.mark.parametrize(
    "source,sanitized",
    [
        ("<bcrypt-hash>1233</bcrypt-hash>", "<bcrypt-hash>SANITIZED</bcrypt-hash>"),
        (
            "<bcrypt-hash>1233</bcrypt-hash></bcrypt-hash>",
            "<bcrypt-hash>SANITIZED</bcrypt-hash></bcrypt-hash>",
        ),
        (
            "<bcrypt-hash></bcrypt-hash></bcrypt-hash>",
            "<bcrypt-hash>SANITIZED</bcrypt-hash></bcrypt-hash>",
        ),
    ],
)
def test_sanitize(source, sanitized):
    result = sanitize_xml(source)
    assert result == sanitized
