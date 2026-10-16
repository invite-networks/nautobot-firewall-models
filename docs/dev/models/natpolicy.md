# NATPolicy

A `NATPolicy` models a set of network address translation (NAT) rules. NAT Policies are assigned to Firewalls, HA Groups and Firewall Groups.

## Attributes

* Name (string)
* Description (optional, string)
* NAT Policy Rules (M2M to NATPolicyRule via NATPolicyRuleM2M)
* Assigned Firewalls (M2M to Firewall)
* Assigned HA Groups (M2M to HAGroup)
* Assigned Firewall Groups (M2M to FirewallGroup)
    * The Firewalls, HA Groups and Firewall Groups the NAT Policy is assigned to, picked in one Assigned To field. A Firewall that is in an HA Group is assigned through its HA Group.
* Status (FK to `Status`)
* Tags (M2M to `Tag`)
