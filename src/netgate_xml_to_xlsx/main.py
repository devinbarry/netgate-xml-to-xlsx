"""Main netgate converstion module."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import sys
from importlib.metadata import version

import toml

from .errors import NodeError
from .logging import create_logger
from .parse_args import parse_args
from .pfsense import PfSense

LOGGER = None


def banner(pfsense: PfSense) -> None:
    """Tell people what we're doing."""
    script = "netgate-xml-to-xlsx"
    package = script.replace("-", "_")
    LOGGER.info(f"{script} version {version(package)}.")


def _main() -> None:
    """Driver."""
    global LOGGER

    args = parse_args()
    LOGGER = logger = create_logger(args)
    in_files = args.in_files
    config = toml.load("./plugins.toml")
    config["args"] = args

    if args.sanitize:
        logger.info("Sanitizing files.")
    else:
        LOGGER.info(f"Output format: {args.output_format}.")

    for in_filename in in_files:
        logger.info(f"Processing: {in_filename}")
        pfsense = PfSense(config, in_filename)

        if args.sanitize:
            pfsense.sanitize(config["plugins"])
            continue

        LOGGER.info(f"Output path: {pfsense.output_path}.")

        pfsense.run_all_plugins(config["plugins"])

    logger.info("Done.")


def main() -> None:
    """Drive and catch exceptions."""
    try:
        _main()
    except NodeError as err:
        if LOGGER is None:
            print(err)
        else:
            LOGGER.exception(err)
        sys.exit(-1)


if __name__ == "__main__":
    main()
