# Netgate Firewall Converter

## IMPORTANT
This is a first-draft alpha walk through the Netgate XML to get a feel for the type of data to be extracted.

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

Or by using pipx
```
pipx install netgate-xml-to-xlsx
```

Once installed, the `netgate-xml-to-xlsx` command is available on your path.

## Usage

### Help
```
# Display help
netgate-xml-to-xlsx --help
```

### Sanitize Before Use
Netgate configuration files contains sensitive information.
Sanitize the files before processing.
Only sanitized files can be processed.
The original (unsanitized) file is deleted.

```
# Sanitize Netgate configuration file(s) for review.
netgate-xml-to-xlsx --sanitize firewall-config.xml
netgate-xml-to-xlsx --sanitize dir/*
```

The sanitize step alters the XML format and layout as it goes through a binary conversion and back to XML again.

### Convert to Spreadsheet
* By default, output is sent to the `./output` directory.
* Use the `--output-dir` parameter to set a specific output directory.
* The output filename is based on the `hostname` and `domain` elements of the XML `system` element.
* Only sanitized files can generate a spreadsheet output.

```
# Convert a Netgate firewall configuration file.
netgate-xml-to-xlsx firewall-config.xml

# Convert all files in a directory.
netgate-xml-to-xlsx ../source/*-sanitized.xml
```

## Implementation Notes

### Why a plugin architecture?

This is an explicit decision to provide flexibility vs. speed/efficiency.
A standard interface only gets so far and attempting to shoe-horn some of the complex elements into a standardized approach seemed futile.
Some additional advantages are:

* Simplifies testing.
  Plugins parse XML and return a list of rows to be output.
  Plugins do not do their own output.
  This allows tests to provide source XML and check the returned rows.
* There are numerous Netgate plugins which I'll probably never see.
  Now people can add their own plugins, along with tests.
* Allows us to have a configuration file that defines what plugins to run, and the order in which to run them.


## Nosec on lxml imports
The `#nosec` flag is added to the lxml imports as the lxml parsing is not a security concern in this environment.

## Tools
    * nox
    * tbump: setting version number

### Using flakeheaven
The large collection of flakeheaven plugins is a bit overboard while I continue to find the best mixture of plugins that work best for my projects.

### Cookiecutter References
* [cookiecutter-hypermodern-python](https://github.com/cjolowicz/cookiecutter-hypermodern-python)
* [cookiecutter-poetry](https://fpgmaas.github.io/cookiecutter-poetry/)


