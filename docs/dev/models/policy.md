# Policy

A Policy models set of security rules permitting or blocking data packets.

Policy is defined as a collection of Policy Rules. A PAN-OS Policy is assigned to Firewalls, HA Groups and Firewall Groups.

You can think of a policy as roughly corresponding to access lists or policies on security appliances.

## Attributes

* Name (string)
* Rule Type (string, choice of panos nftables)
    * Every Policy Rule in the Policy must be of this type. It cannot be changed once the Policy exists.
* Description (optional, string)
* Policy Rules (M2M to PolicyRule via PolicyRuleM2M)
* Assigned Firewalls (M2M to Firewall)
* Assigned HA Groups (M2M to HAGroup)
* Assigned Firewall Groups (M2M to FirewallGroup)
    * The Firewalls, HA Groups and Firewall Groups the Policy is assigned to, picked in one Assigned To field. A Firewall that is in an HA Group is assigned through its HA Group.
    * Only PAN-OS Policies can be assigned.
* Status (FK to Status)
* Tags (M2M to Tag)

## Examples

Example of access list that could be translated to a Policy

```no-highlight
Extended IP access list Virtual-Access1.1#1
    20 permit icmp host 1.1.1.1 any
    30 deny ip host 44.33.66.36 host 1.1.1.1
    40 permit udp any host 1.1.1.1
```
