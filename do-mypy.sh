#!/usr/bin/env bash
echo "add --strict"
mypy --warn-return-any --disallow-untyped-defs --ignore-missing-imports -p netgate_xml_to_xlsx
