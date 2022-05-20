"""Main netgate converstion module."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import toml

from .parse_args import parse_args
from .pfsense import PfSense

# Hard-code. May make an argument later on.
# Eventually allow commandline argument to run additional plugins.
PLUGINS_TO_RUN = (
    "system,system_groups,system_users,aliases,rules,interfaces,gateways,"
    "openvpn_servers,installed_packages,unbound,"
    "haproxy"
).split(",")


def banner(pfsense: PfSense) -> None:
    """Tell people what we're doing."""
    print(f"Output: {pfsense.ss_output_path}.")


def main() -> None:
    """Driver."""
    args = parse_args()
    in_files = args.in_files
    config = toml.load("./plugins.toml")

    for in_filename in in_files:
        pfsense = PfSense(args, in_filename)
        banner(pfsense)

        if args.sanitize:
            pfsense.sanitize(PLUGINS_TO_RUN)
            continue

        # Run plugins in order.
        for plugin_to_run in config["plugins"]:
            print(f"    {plugin_to_run}")
            pfsense.run(plugin_to_run)
        pfsense.save()


if __name__ == "__main__":
    main()
