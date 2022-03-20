# Netgate Firewall Converter

The `netgate-xml-to-xlsx` converts a standard Netgate firewall .xml configuration file to an .xlsx spreadsheet with multiple tabs.

* Supports Python 3.10+.
* This is an alpha version tested on a limited number of firewall files.
* The specific spreadsheet tabs implemented address our (ASI's) immediate firewall review needs.
* Tested only on Netgate firewall version 21.x files.


## Installation
Recommend installing this in a virtual environment.

```
python -m pip install netgate-xml-to-xlsx
```

Once installed, the `netgate-xml-to-xlsx` command is available on your path.

## Usage

* By default, output is sent to the current directory.
* Use the `--output-dir` parameter to set a specific output directory.
* The output filename is based on the `hostname` and `domain` elements of the XML `system` element.

```
# Display help
netgate-xml-to-xlsx --help
```

```
# Convert a Netgate firewall configuration file.
netgate-xml-to-xlsx firewall-config.xml
```

## Notes

### Using flakeheaven
The large collection of flakeheaven plugins is a bit overboard while I continue to find the best mixture of plugins that work best for my projects.
