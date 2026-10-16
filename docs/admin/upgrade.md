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

Zones also gain a `devices` field so one Zone can be bound to multiple Devices. The upgrade binds each existing Zone to every Device that owns one of its Interfaces, so no manual step is needed. Set it over REST with `"devices": ["<device id>", ...]`, or filter Zones with `?devices=<device name or id>`. With `protect_on_delete` enabled, a Device can't be deleted while it is bound to a Zone.

Rolling the migrations back keeps only the first Zone (by name) on each side of a rule and drops all Zone Group assignments and Zone to Device bindings.

## Upgrade 4.0 to 4.1

Version 4.1 adds Policy Bands. Every Policy Rule now requires a `band` and a `position` (`header` or `closer`), and rules are ordered by band rather than by index alone.

The migration does not assign bands to existing rules. If any Policy Rules exist, it stops with an error before changing the database. To upgrade with existing rules:

1. Export the Policy Rules (CSV or REST API) and delete them.
2. Upgrade and run `nautobot-server post-upgrade`.
3. Create the Policy Bands under Security > Policy > Policy Bands.
4. Add `band` and `position` to the exported rules and import them again.

Integrations that create Policy Rules must now send `band` and `position`. To get one Device's rules in firewall order, merged across every Policy assigned to it directly or through a Dynamic Group, call `/api/plugins/firewall/policy-rule/?device=<device name or id>`.

## Upgrade 4.1 to 4.2

Version 4.2 adds a required rule type, `panos` or `nftables`, to Policy Rules and Policies. There is no default, and the migration does not assign one, so it expects no Policy Rules or Policies to exist. Export and delete them before upgrading, then import them again with a `rule_type`.

Integrations must now send `rule_type` when creating Policy Rules and Policies. nftables rules take a `chain` instead of `band` and `position`, and a Policy only accepts rules of its own type.

## Upgrade 4.2 to 4.3

Version 4.3 removes IP Ranges. The migration stops if any IP Ranges exist. Change every Address Object that uses one to a Prefix, IP Address or FQDN, delete the IP Ranges, then upgrade. Integrations that call `/api/plugins/firewall/ip-range/` or read `ip_range` on Address Objects must be updated.

Policy Rule positions are renamed: `header` becomes `pre` (Pre Rules) and `closer` becomes `post` (Post Rules). The migration renames existing rules, so update any integration that sends or reads the old values. A new `final` position holds a band's closing deny or drop rules, which always sort last in the band.

The migration also creates the Managed Locally status and adds the negate and flatten fields with defaults of false, so no other step is needed.

## Upgrade Guide

When a new release comes out it may be necessary to run a migration of the database to account for any changes in the data models used by this app. Execute the command `nautobot-server post-upgrade` within the runtime environment of your Nautobot installation after updating the `nautobot-firewall-models` package via `pip`.
