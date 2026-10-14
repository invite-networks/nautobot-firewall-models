# v4.2 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Policy Rules and Policies now have a required rule type, PAN-OS or nftables. Adding a rule asks for the type first, and the form only shows the fields that type can use. A Policy only holds rules of its own type.
- nftables rules are host firewall rules. They use a chain (input, forward or output) in place of a Policy Band and position, and cannot use zones, users or applications.
- Address Objects can reference a Device, which resolves to that Device's primary IPs, or the dynamic value Subnet, which resolves to the Prefix of the primary IP of whichever host the rules are rendered for. Both work only on nftables rules, and are refused on PAN-OS and NAT rules by every path, including Address Object Groups.

<!-- towncrier release notes start -->

## [v4.2.1 (2026-10-14)](https://github.com/invite-networks/nautobot-firewall-models/releases/tag/v4.2.1)

### Changed

- Refused Source Services and Source Service Groups on PAN-OS Policy Rules, which match on destination service only. nftables rules still accept them, and the PAN-OS form no longer shows the picker.
- Refused Original and Translated Source Services and their groups on NAT Policy Rules, and removed them from the NAT rule form and the expanded rule table. PAN-OS NAT matches on the original destination service and translates the destination port only.

### Fixed

- Ordered NAT Policy Rules with no index after indexed rules, and by name when rules share an index or have none, matching Policy Rules. NAT rules without an index previously came back in no defined order.

## [v4.2.0 (2026-10-14)](https://github.com/invite-networks/nautobot-firewall-models/releases/tag/v4.2.0)

### Breaking Changes

- Added a required `rule_type` to Policy Rules and Policies with no default. The migration expects no Policy Rules or Policies to exist. See the upgrade guide.

### Added

- Added a rule type to Policy Rules. PAN-OS rules still require a Policy Band and position.
- Added a rule type to Policies. A Policy only accepts Policy Rules of its type, and its rule picker only lists them.
- Added nftables Policy Rules with a required chain. Band, position, zones, users, applications and remarks are refused on them.
- Added a type chooser to the Add Policy Rule page, and a rule type and chain filter on Policy Rules.
- Added Device and dynamic Subnet options to Address Objects, with `AddressObject.resolve(host)` to turn them into networks for a given host. They are refused on PAN-OS Policy Rules and NAT Policy Rules, including through Address Object Groups and by changing an Address Object those rules already use.
- Added `/api/plugins/firewall/grouped-objects/<kind>/`, which searches objects and their groups together for the combined pickers. `kind` is `zones`, `addresses`, `services`, `users` or `applications`.

### Fixed

- Removed the Policy Band, position and chain fields that the NAT Policy Rule bulk edit form inherited from the Policy Rule form.

### Changed

- Replaced the separate object and group pickers for zones, addresses, services, users and applications on the Policy Rule and NAT Policy Rule forms with one picker per field that searches both as you type, e.g. Source Zones finds Zones and Zone Groups. The REST API and data model keep the separate fields, such as `source_zones` and `source_zone_groups`.
- Made `band` and `position` optional on Policy Rules at the database level. They are still required on PAN-OS rules.
