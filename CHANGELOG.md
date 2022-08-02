# CHANGELOG

## Release 0.9.9 -- ??
* Name installed package plugins as `plugin_installed_xxx`.
* Replace (most) `print` instances with `logger`.
* Processing installed packages:
  * FreeRADIUS components
  * lightsquid
  * menu
  * pf components
  * service
  * servicewatchdog
  * Squid and SquidGuard components
  * Suricata components
  * vpn\_openvpn\_export
  * zabbixagentlts

* Added Zabbix custom sanitization.
* Added pf custom sanitization.
* Reports
  * Unknown packages.

* Gathered output formats into a module.
* Added text (txt) output format.
* Support blank `vpn_openvpn_export/config` element.

## Release 0.9.8 -- 2022-05-27
* Support per-plugin sanitize method (see haproxy plugin for example).
* Complete first pass of all base XML elements.
* HAProxy.
* Hoist test scripts.


## Release 0.9.7 -- 2022-04-23
* Refactor following "Hypermodern Python" model.
* Use nox for automation.

## Release 0.9.6-a1 -- 2022-03-24

* Refactor original script into modules.
* Convert to plugin architecture.

## Release 0.9.5-a2 -- 2022-03-22

* Unbound sheet.
* Improve access to possibly missing elements.
* Add --sanitized option.
* Delete unsanitized file after it is sanitized.
* Only process sanitized files.

## Release 0.9.3-alpha -- 2022-03-21

* Change default output directory to ./.
* Support multiple input files.
* Add --sanitize option.

## Release 0.9.2-alpha -- 2022-03-20

* Mypy and flakeheaven code cleanups.

## Release 0.9.1-alpha -- 2022-03-19

* Initial alpha release.
