"""Base Format class."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from abc import ABC, abstractmethod


class BaseFormat(ABC):
    """Base of all formats."""

    def __init__(self, ctx: dict) -> None:
        """
        Initialize base format.

        Args:
            ctx: Context containing necessary initialization information.
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """Do required report start-up based on data in ctx."""
        raise NotImplementedError

    @abstractmethod
    def out(self, rows: list[str]) -> None:
        """Generate a sheet/page/section."""
        raise NotImplementedError

    @abstractmethod
    def finish(self) -> None:
        """Perform cleanup, saving, etc."""
        raise NotImplementedError
