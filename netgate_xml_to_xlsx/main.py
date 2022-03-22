"""Main netgate converstion module."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

from .parse_args import parse_args
from .pfsense import PfSense


def banner(pfsense: PfSense) -> None:
    """Tell people what we're doing."""
    print(f"Output will be: {pfsense.args.output_dir / pfsense.ss_filename}.")


def main() -> None:
    """Driver."""
    args = parse_args()

    in_files = args.in_files

    for in_filename in in_files:
        pfsense = PfSense(args, in_filename)

        if args.sanitize:
            pfsense.sanitize()
            continue

        # Worksheet creation order.
        pfsense.system()

        # Need to parse system before banner has the information it needs.
        banner(pfsense)
        pfsense.system_groups()
        pfsense.system_users()
        pfsense.aliases()
        pfsense.rules()
        pfsense.interfaces()
        pfsense.gateways()
        pfsense.openvpn_server()
        pfsense.installed_packages()
        pfsense.unbound()
        pfsense.save()


if __name__ == "__main__":
    main()
