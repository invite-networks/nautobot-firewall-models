# v4.0 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

This major release is the first INVITE Networks release of the app. Highlights:

- Added Zone Groups. A Zone Group bundles one or more Zones and can be used anywhere a Zone can be used on Policy Rules and NAT Policy Rules.
- Policy Rules and NAT Policy Rules can now reference multiple source and destination Zones. The single `source_zone` and `destination_zone` fields are replaced by `source_zones` and `destination_zones`, and existing assignments are migrated automatically. See the [upgrade guide](../upgrade.md) before upgrading.
- Rules expose `expanded_source_zones` and `expanded_destination_zones` in the REST API and GraphQL so deployment tooling receives Zone Groups already resolved into Zones.
- Removed the Capirca integration.

<!-- towncrier release notes start -->

## [v4.0.0 (2026-10-09)](https://github.com/invite-networks/nautobot-firewall-models/releases/tag/v4.0.0)

### Breaking Changes

- Changed `source_zone` and `destination_zone` on Policy Rules and NAT Policy Rules from a single Zone to many Zones, renamed to `source_zones` and `destination_zones`. Existing assignments are migrated automatically. REST API, GraphQL, filter, and CSV consumers must switch to the new field names and send a list of Zones.

### Added

- Added the ZoneGroup model to group one or more Zones. Zone Groups can be used anywhere a Zone can be used on Policy Rules and NAT Policy Rules, and appear under the Zone menu.
- Added read-only `expanded_source_zones` and `expanded_destination_zones` to the Policy Rule and NAT Policy Rule REST API and GraphQL types, returning each rule's Zones with every Zone Group expanded into its member Zones.

### Removed

- Removed the Capirca integration, including the CapircaPolicy model, its API endpoint, UI views, the "Generate FW Config via Capirca" job, and the `capirca_remark_pass`, `capirca_os_map`, and `custom_capirca` settings.
