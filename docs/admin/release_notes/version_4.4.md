# v4.4 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Added Appliances under the Security menu: Firewalls, HA Groups and Firewall Groups, for PAN-OS.
- Policies, NAT Policies and Zones are now assigned to Firewalls, HA Groups and Firewall Groups instead of Devices, Dynamic Groups and Virtual Machines. See the [upgrade guide](../upgrade.md) before upgrading.

<!-- towncrier release notes start -->

## [v4.4.0 (2026-10-16)](https://github.com/invite-networks/nautobot-firewall-models/releases/tag/v4.4.0)

### Breaking Changes

- Removed Device and Dynamic Group assignment from Policies and NAT Policies, with their weights, the Edit Device Weight and Edit Dynamic Group Weight tabs, and the `policy-device-association`, `policy-dynamic-group-association`, `nat-policy-device-association` and `nat-policy-dynamic-group-association` REST API endpoints.
- Removed Devices and Virtual Machines from Zones.
- Replaced the Policy Rule `device` filter with `firewall`.
- The migration stops, listing each one, while any Policy, NAT Policy or Zone is still assigned to a Device, Dynamic Group or Virtual Machine.

### Added

- Added Firewalls, each bound to exactly one Device or Virtual Machine. A Firewall's page lists the Policies and NAT Policies that reach it and links to its Policy Rules in firewall order, and the Device or Virtual Machine page shows its Firewall.
- Added HA Groups: two Firewalls and the management address they share. The form picks exactly two Firewalls, and a Firewall can be in only one HA Group.
- Added Firewall Groups of Firewalls and HA Groups, picked in one field. They do not nest, and a Firewall or HA Group can be in several.
- Policies and NAT Policies are assigned, and Zones bound, to Firewalls, HA Groups and Firewall Groups in one searchable Assigned To or Bound To field. Only PAN-OS Policies can be assigned.
- A Firewall in an HA Group is used only through its HA Group: Firewall Groups, Policies, NAT Policies and Zones refuse it directly, and it cannot join an HA Group while it is used directly.
- Added Trust Band to Policy Bands, for bands that must end with an explicit deny. A Trust Band without a Final rule is reported on its page, in the band list and as `missing_final_rule` in the REST API, with a `missing_final_rule` filter; saving is never blocked.
- Added a `firewall` filter on Policy Rules and NAT Policy Rules that returns a Firewall's rules across Policies assigned to it, its HA Group or a Firewall Group holding either.

### Changed

- The combined pickers can now search more than two kinds of object in one field.
