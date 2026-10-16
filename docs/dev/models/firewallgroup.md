# FirewallGroup

A set of Firewalls and HA Groups, so Policies, NAT Policies and Zones can be assigned to all of them at once. It plays the role of a Panorama Device Group.

## Attributes

* Name (string, unique)
* Description (optional, string)
* Firewalls (M2M to Firewall)
* HA Groups (M2M to HAGroup)
    * Picked in one field. A Firewall that is in an HA Group is added through its HA Group. Firewall Groups do not nest, and a Firewall or HA Group can be in several.
* Status (FK to Status)
