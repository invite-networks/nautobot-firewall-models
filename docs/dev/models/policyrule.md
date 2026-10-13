# PolicyRule

Represents a single security rule in a Policy.

It is recommended to use a descriptive name to best identify a PolicyRule, otherwise the string representation of the PolicyRule if the UUID for the instance.

## Attributes

* Name (optional, string)
* Status (FK to Status)
* Tags (M2M to Tag)
* Source User (M2M to UserObject)
* Source User Group (M2M to UserObjectGroup)
* Source Address (M2M to AddressObject)
* Source Address Group (M2M to AddressObjectGroup)
* Source Zone (FK to Zone)
* Destination Address (M2M to AddressObject)
* Destination Address Group (M2M to AddressObjectGroup)
* Source Zone (FK to Zone)
* Service (M2M to ServiceObject)
* Service Group (M2M to ServiceObjectGroup)
* Action (string, choice of deny drop allow)
* Log (boolean)
* Request ID (optional, string)
    * Meant to represent an upstream request (e.g. an service request from an ITSM solution).
* Band (FK to PolicyBand)
    * The section of the policy the rule belongs to.
* Position (string, choice of header closer)
    * Header rules come before the band's locally created rules on the firewall, Closer rules after.
* Index (optional, int)
    * Orders rules within a band and position. Rules may share an index when their order does not matter.
    * Example `20 permit icmp host 1.1.1.1 any` would have an index of `20`.

Rules are ordered by band index, then Header before Closer, then index (rules without one last), then name.

## Examples

Example line in an access list that would translate to a Policy Rule:

```no-highlight
30 deny ip host 44.33.66.36 host 1.1.1.1
```
