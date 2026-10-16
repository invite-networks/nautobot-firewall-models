# v4.3 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Removed IP Ranges. See the [upgrade guide](../upgrade.md) before upgrading.
- Added the Managed Locally status for objects the firewall defines itself, such as the PAN-OS predefined External Dynamic List "Palo Alto Networks - High risk IP addresses". Rules reference them by name.
- Added Negate Source and Negate Destination to PAN-OS Policy Rules.
- Added Flatten to Address Object Groups, so a group such as a list of countries renders as its individual entries.
- Address Object Groups can hold other Address Object Groups, picked in the same field as their Address Objects.

<!-- towncrier release notes start -->

## [v4.3.0 (2026-10-14)](https://github.com/invite-networks/nautobot-firewall-models/releases/tag/v4.3.0)

### Breaking Changes

- Added `panos_rule_type` to PAN-OS Policy Rules: Universal by default, or Intrazone or Interzone. An Intrazone rule takes no destination zone or zone group, matching PAN-OS. The migration sets existing PAN-OS rules to Universal.
- Bound each Zone to exactly one Zone Group with the required `zone_group` field on the Zone, replacing the Zone Group's `zones` list. A group is created first and Zones join it from the Zone form, its page lists its Zones, and it cannot be deleted while it has any. The migration moves each Zone's one group across and stops if a Zone has none or several. The Zone filter `zone_groups` is now `zone_group`.
- Replaced `log` on Policy Rules with `log_start` (Log at Session Start, PAN-OS only, off by default) and `log_end` (Log at Session End, on by default). The migration copies each rule's `log` into `log_end`. On nftables rules `log_end` is the rule's one log, shown as Log and unchecked on a new rule. NAT Policy Rules keep `log`.
- Renamed the Policy Rule positions `header` and `closer` to `pre` (Pre Rules) and `post` (Post Rules). The migration renames existing rules.
- Removed Interfaces from Zones: the `interfaces` field, its form picker and its column. A Zone is bound to Devices and Virtual Machines instead.
- Removed the IP Range model, its UI, its REST API endpoint `/api/plugins/firewall/ip-range/` and the `ip_range` field on Address Objects. The migration stops if any IP Ranges exist.

### Added

- Added the Managed Locally status to Address, Service, Application and User Objects and their groups. A Managed Locally Address Object holds only a name, and a Managed Locally group cannot have members, since the firewall defines and maintains them.
- Added `negate_source` and `negate_destination` to Policy Rules. They are PAN-OS only, and the expanded rule view marks a negated side with NOT.
- Added `flatten` to Address Object Groups, off by default. Policy Rules expose `rendered_source_addresses`, `rendered_source_address_groups`, `rendered_destination_addresses` and `rendered_destination_address_groups` over REST and GraphQL, with each flattened group replaced by its Address Objects. A flattened group that renders as nothing stays a group so a rule never widens to any address, and a Managed Locally group cannot be flattened.
- Added `address_object_groups` to Address Object Groups for nested groups, to any depth. A group cannot contain itself, directly or through another group. Flattening opens nested groups that are also flattened and keeps the others as groups, and the host relative and Managed Locally checks look through every level. The group form picks Address Objects and nested groups in one searchable field.

- Added `virtual_machines` to Zones, so a Zone can be bound to Virtual Machines as well as Devices. The Zone form picks both in one searchable field, Zones can be filtered by Virtual Machine, and with `protect_on_delete` enabled a Virtual Machine cannot be deleted while it is bound to a Zone.

- Added the Final position for a band's closing rules. Final rules sort after every Pre and Post rule in the band whatever their index, ordered among themselves by index and then name, and must deny or drop.

### Fixed

- Allowed an Application Object Group to be saved without Application Objects, which a Managed Locally group needs. The other group forms already allowed it.
- Made the IP protocol optional on Managed Locally Service Objects, so a built in service such as `service-https` needs only a name. Other Service Objects still require it.
- Showed validation errors for the hidden object and group fields behind the combined pickers on the picker itself. A refused save previously re-rendered the form with no message.

### Changed

- Split the rule type checks on Policy Rules into a per type table of required and refused fields, and the grouped objects API paging into its own method. Behavior is unchanged.
