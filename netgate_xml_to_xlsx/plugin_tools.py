"""Plugin support tools."""
# Copyright © 2022 Appropriate Solutions, Inc. All rights reserved.

import importlib
import pkgutil

from . import plugins


def iter_namespace(ns_pkg):
    """Gather all modules in namespace."""
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def discover_plugins():
    """Discover and initialize plugins."""
    discovered_plugins = {}
    for _, long_name, _ in iter_namespace(plugins):
        if (name := long_name.split(".")[-1]).startswith("plugin_"):
            name = name.replace("plugin_", "", 1)
            discovered_plugins[name] = importlib.import_module(long_name).Plugin()

    return discovered_plugins
