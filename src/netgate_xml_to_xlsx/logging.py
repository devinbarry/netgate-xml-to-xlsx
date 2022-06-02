"""Logging module."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import argparse
import logging
import logging.handlers as handlers
from pathlib import Path


def custom_log_level() -> None:
    """Create a custom verbose log level between info and debug."""
    verbose_level = logging.INFO - 5

    def verbose(self, message: str, *args, **kwargs) -> None:
        if self.isEnabledFor(verbose_level):
            # Yes, args vs. *args.
            self._log(  # pylint: disable=protected-access
                verbose_level, message, args, **kwargs
            )

    logging.addLevelName(verbose_level, "VERBOSE")
    logging.VERBOSE = verbose_level
    logging.Logger.verbose = verbose


def create_logger(args: argparse.Namespace) -> logging.Logger:
    """Create standard logger."""
    logger = logging.getLogger()

    custom_log_level()

    # Debug takes precedence over verbose.
    logger.setLevel(logging.INFO)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.verbose:
        logger.setLevel(logging.VERBOSE)

    # Create log path if it does not exist.
    log_dir = Path(args.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = handlers.TimedRotatingFileHandler(
        Path(args.log_dir) / "ngate.log",
        when="midnight",
        encoding="utf-8",
        backupCount=7,
    )
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%b %d %Y %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler()
    logger.addHandler(handler)

    return logger
