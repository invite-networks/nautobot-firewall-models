# Upgrading the App

Here you will find any steps necessary to upgrade the App in your Nautobot environment.

## Upgrade Nautobot 1.X to Nautobot 2.X

As part of the upgrade for Nautobot 2.0 it is recommended to perform a stepped upgrade by first upgrading Nautobot the lastest stable release within these constraints `>=1.6.2,<2.0.0`. After performing the initial upgrade of Nautobot you will need to run `nautobot-server populate_platform_network_driver --no-use-napalm-driver-field`. This will populate the `network_driver` attribute on Platform objects from the `slug` field.

## Upgrade 3.X to 4.X

Version 4.0 adds Zone Groups and allows a rule to reference more than one Zone on each side. On Policy Rules and NAT Policy Rules, `source_zone` and `destination_zone` are replaced by the many-to-many fields `source_zones` and `destination_zones`, alongside the new `source_zone_groups` and `destination_zone_groups`.

The database migration copies each rule's existing source and destination Zone into the new fields, so no data is lost. Update any integrations that read or write the old field names:

- REST API: send `"source_zones": ["<zone id>"]` instead of `"source_zone": "<zone id>"`. Many-to-many fields are only returned when `?exclude_m2m=false` is set.
- GraphQL: query `source_zones { name }` instead of `source_zone { name }`.
- Deployment tooling: read `expanded_source_zones` and `expanded_destination_zones`, which already resolve Zone Groups into their member Zones.

Rolling the migration back keeps only the first Zone (by name) on each side of a rule and drops all Zone Group assignments.

## Upgrade Guide

When a new release comes out it may be necessary to run a migration of the database to account for any changes in the data models used by this app. Execute the command `nautobot-server post-upgrade` within the runtime environment of your Nautobot installation after updating the `nautobot-firewall-models` package via `pip`.
