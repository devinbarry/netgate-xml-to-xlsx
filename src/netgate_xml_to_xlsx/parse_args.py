"""Parse commandline arguments."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import argparse
import sys
from importlib.metadata import version
from pathlib import Path


def filter_infiles(in_files: list[str], include: bool = True) -> list[Path]:
    """Return list of Paths that are files and include or exclude 'sanitized'."""
    files = [Path(x) for x in in_files]
    if include:
        return [x for x in files if "sanitized" in x.name and x.is_file()]
    return [x for x in files if "sanitized" not in x.name and x.is_file()]


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Process in_files and out_dir.
    """
    parser = argparse.ArgumentParser("Netgate XML to XLSX")
    default = "./output"
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=default,
        help=f"Output directory. Default: {default}",
    )
    parser.add_argument(
        "in_files", nargs="+", help="One or more Netgate .xml files to process."
    )

    parser.add_argument(
        "--sanitize",
        action="store_true",
        help="Sanitize the input xml files and save as <filename>-sanitized.",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Additional logging."
    )

    parser.add_argument("--debug", action="store_true", help="Debug logging.")

    default = "./logs"
    parser.add_argument(
        "--log-dir",
        type=str,
        default=default,
        help=f"Log directory. Default: {default}.",
    )

    __version__ = version("netgate_xml_to_xlsx")
    parser.add_argument(
        "--version",
        action="version",
        version=f"{__version__}",
        help="Show version number.",
    )

    args = parser.parse_args()

    # Filter files in/out.
    if args.sanitize:
        args.in_files = filter_infiles(args.in_files, include=False)
        msg = "All files already sanitized."
    else:
        args.in_files = filter_infiles(args.in_files)
        msg = (
            "No files contain 'sanitized' in the name.\n"
            "Run --sanitize before processing."
        )

    if not args.in_files:
        print(msg)
        sys.exit(-1)

    # Convert output-dir to path and optionally create path.
    out_dir = Path(args.output_dir)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        args.output_dir = out_dir
    except OSError as err:
        print(f"Error: {err}")
        sys.exit(-1)
    return args
