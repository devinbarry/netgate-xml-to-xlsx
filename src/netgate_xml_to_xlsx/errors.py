"""Script-specific exceptions."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.


class ScriptError(Exception):
    """Generic script error."""


class UnknownField(ScriptError):
    """Parsing something new."""


class MissingField(ScriptError):
    """Expected field not found."""
