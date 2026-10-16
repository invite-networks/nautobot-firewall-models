# PolicyRule

Represents a single security rule in a Policy.

It is recommended to use a descriptive name to best identify a PolicyRule, otherwise the string representation of the PolicyRule if the UUID for the instance.

## Attributes

* Name (optional, string)
* Rule Type (string, choice of panos nftables)
    * The platform the rule is written for. It decides which of the fields below the rule may use, and cannot be changed once the rule exists.
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
* Negate Source (boolean, PAN-OS only, default false)
    * Matches every source except the addresses set.
* Negate Destination (boolean, PAN-OS only, default false)
    * Matches every destination except the addresses set.
* Action (string, choice of deny drop allow)
* Log at Session Start (boolean, PAN-OS only, default false)
* Log at Session End (boolean, default true)
    * On nftables rules, which have one log, this is the rule's log. Their form starts it unchecked.
* Request ID (optional, string)
    * Meant to represent an upstream request (e.g. an service request from an ITSM solution).
* PAN-OS Rule Type (string, choice of universal intrazone interzone, PAN-OS only, default universal)
    * Universal matches traffic within and between zones. Intrazone matches traffic within the source zones and takes no destination zone or zone group. Interzone matches traffic between different zones.
* Band (FK to PolicyBand, PAN-OS only and required there)
    * The section of the policy the rule belongs to.
* Position (string, choice of pre post final, PAN-OS only and required there)
    * Pre Rules come before the band's locally created rules on the firewall and Post Rules after. Final rules are always last in the band and must deny or drop; a band may have several.
* Chain (string, choice of input forward output, nftables only and required there)
* Index (optional, int)
    * Orders rules within a band and position. Rules may share an index when their order does not matter.
    * Example `20 permit icmp host 1.1.1.1 any` would have an index of `20`.

Rules are ordered by band index (nftables rules have none and sort last), then Pre Rules, Post Rules and Final rules, then chain, then index (rules without one last), then name.

## Rule Types

* PAN-OS rules may use every field except Chain, Source Services and Source Service Groups. An Intrazone PAN-OS rule also takes no destination zone or zone group. PAN-OS security rules match on destination service only.
* nftables rules are host firewall rules. They may not use zones, zone groups, users, user groups, applications, application groups, a band, a position, negation or the remark action.
* Address Objects that reference a Device or the dynamic Subnet only resolve per host, so they may only be used on nftables rules, directly or inside an Address Object Group.
* A Policy holds rules of a single type, set by the Policy's own Rule Type.

## Examples

Example line in an access list that would translate to a Policy Rule:

```no-highlight
30 deny ip host 44.33.66.36 host 1.1.1.1
```
