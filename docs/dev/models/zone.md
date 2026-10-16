# Zone

Zones are common on firewalls and are typically seen as representations of area (e.g. DMZ, trust, untrust).

## Attributes

* Name (string)
* Description (optional, string)
* Zone Group (FK to ZoneGroup, required)
    * The one Zone Group the Zone belongs to.
* VRFs (M2M to VRF)
* Firewalls (M2M to Firewall)
* HA Groups (M2M to HAGroup)
* Firewall Groups (M2M to FirewallGroup)
    * What the Zone is bound to, picked in one Bound To field. A Firewall that is in an HA Group is bound through its HA Group.
* Status (FK to Status)
