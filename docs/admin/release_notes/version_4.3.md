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

- Removed the IP Range model, its UI, its REST API endpoint `/api/plugins/firewall/ip-range/` and the `ip_range` field on Address Objects. The migration stops if any IP Ranges exist.

### Added

- Added the Managed Locally status to Address, Service, Application and User Objects and their groups. A Managed Locally Address Object holds only a name, and a Managed Locally group cannot have members, since the firewall defines and maintains them.
- Added `negate_source` and `negate_destination` to Policy Rules. They are PAN-OS only, and the expanded rule view marks a negated side with NOT.
- Added `flatten` to Address Object Groups, off by default. Policy Rules expose `rendered_source_addresses`, `rendered_source_address_groups`, `rendered_destination_addresses` and `rendered_destination_address_groups` over REST and GraphQL, with each flattened group replaced by its Address Objects. A flattened group that renders as nothing stays a group so a rule never widens to any address, and a Managed Locally group cannot be flattened.
- Added `address_object_groups` to Address Object Groups for nested groups, to any depth. A group cannot contain itself, directly or through another group. Flattening opens nested groups that are also flattened and keeps the others as groups, and the host relative and Managed Locally checks look through every level. The group form picks Address Objects and nested groups in one searchable field.

### Fixed

- Showed validation errors for the hidden object and group fields behind the combined pickers on the picker itself. A refused save previously re-rendered the form with no message.

### Changed

- Split the rule type checks on Policy Rules into a per type table of required and refused fields, and the grouped objects API paging into its own method. Behavior is unchanged.
