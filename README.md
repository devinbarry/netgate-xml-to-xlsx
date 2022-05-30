# Convert Netgate XML Firewall Exports

## Note
 This project has no relationship with Netgate, the company.
It is an internal project developed by Appropriate Solutions, Inc.

## Overview

The `netgate-xml-to-xlsx` application converts a standard Netgate firewall .xml configuration file to an .xlsx spreadsheet with multiple tabs.

We've run the current implementation on a handful of our own XML firewall rules, however there's are probably some complex XML elements that will throw warnings when you run on your own files.

If you have a piece of XML that doesn't parse please extract a minimal portion (starting at the pfsense root) and open a ticket (better yet, modify the plugin and provide a pull request).

## What is implemented?
* First pass of XML elements in the base Netgate firewall installation.
* Installed packages:
  * FreeRADIUS components
  * haproxy
  * lightsquid
  * menu
  * pf components
  * service
  * servicewatchdog
  * Squid and SquidGuard components
  * Suricata components
  * vpn\_openvpn\_export
  * zabbixagentlts

Note there are a number of nodes not implemented as they do not appear in our internal XML samples.

## Requirements
* Python 3.10+.
* Netgate firewall XML version 21.x or 22.x.


## Installation

Recommend installing this with pipx:
```
pipx install netgate-xml-to-xlsx
```

Or into a virtual environment.

```
python -m pip install netgate-xml-to-xlsx
```

Once installed, the `netgate-xml-to-xlsx` command is available on your path.

## Configuration file

The script requires a configuration file called `plugins.toml` in the current working directory when you run the script.
Download the sample from the GitLab [repository](https://gitlab.com/appropriate-solutions-inc/netgate-xml-to-xlsx/-/blob/main/plugins.toml).
The `plugins.toml` file defines the plugins to run as well as the order in which they are run.
The default order to to run all standard plugins in alphabetical order followed by the installed packages in alphabetical order.

## Usage

### Help

```
# Display help
netgate-xml-to-xlsx --help
```

### Sanitize Before Use
Netgate configuration files contains sensitive information.
The XML file must be sanitized before processing.
The original (unsanitized) file is deleted.

```
# Sanitize Netgate configuration file(s) for review.
netgate-xml-to-xlsx --sanitize firewall-config.xml
netgate-xml-to-xlsx --sanitize dir/*.xml
```

### Convert to Spreadsheet
* By default, output is sent to the `./output` directory.
* Use the `--output-dir` parameter to set a specific output directory.
* The output filename is the input filename with `.xlsx` attached to the end.

```
# Convert a Netgate firewall configuration file.
netgate-xml-to-xlsx firewall-config.xml

# Convert all files in a directory.
netgate-xml-to-xlsx /fwalls/*-sanitized.xml
```

## Implementation Notes

### Plugins

Each top-level (or installed package) element is implemented in a separate plugin.
The plugin name matches the XML element being processed.

Some advantages to implementing plugins:

* Simplifies testing.
  Plugins parse XML and return a list of rows to be output.
  Plugins do not do their own output.
  Test provide source XML and check the returned rows.
* There are numerous Netgate plugins which I'll probably never see.
  You can add your own plugins, along with tests.


## Nosec on lxml imports
The `#nosec` flag is added to the lxml imports as the lxml parsing is not a security concern in this environment.

## asserts
Asserts are used throughout to:
1. provide mypy guidance
1. check for unexpected data as we're working from XML samples and not a specification.


### Cookiecutter References
* [cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python)
* [cookiecutter-poetry](https://fpgmaas.github.io/cookiecutter-poetry/)


