# v4.1 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Added Policy Bands. A Policy Band is a section of a firewall policy, such as Global Deny or Medium Trust, and bands set the order rules are deployed in.
- Every Policy Rule now belongs to a band as a Header or Closer rule. Header rules land at the top of the band and Closer rules at the bottom, leaving the space between them for rules created locally on the firewall. See the [upgrade guide](../upgrade.md) before upgrading.
- Policy Rules can be filtered by Device to get one firewall's rules merged across every assigned Policy, in firewall order.

<!-- towncrier release notes start -->

## [v4.1.0 (2026-10-13)](https://github.com/invite-networks/nautobot-firewall-models/releases/tag/v4.1.0)

### Breaking Changes

- Changed Policy Rules to require a Policy Band and a position (header or closer), and to sort by band instead of index alone. The migration stops if any Policy Rules already exist. See the upgrade guide.

### Added

- Added the PolicyBand model under Security > Policy to define the sections of a firewall policy and the order they are evaluated in.
- Added a device filter on Policy Rules that returns one Device's rules merged across every Policy assigned to it directly or through a Dynamic Group, in firewall order.
