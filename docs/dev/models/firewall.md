# Firewall

A PAN-OS firewall, bound to the Device or Virtual Machine it runs on. Policies, NAT Policies and Zones are assigned to Firewalls, either directly or through an HA Group or Firewall Group.

## Attributes

* Name (string, unique)
* Description (optional, string)
* Device (one to one with Device) or Virtual Machine (one to one with VirtualMachine)
    * Exactly one is set, and a Device or Virtual Machine can be only one Firewall.
* HA Group (FK to HAGroup, optional)
    * Set from the HA Group's form. A Firewall in an HA Group is used only through the HA Group: it cannot be added to a Firewall Group, Policy, NAT Policy or Zone directly, and it cannot join an HA Group while it is used in one of those directly.
* Status (FK to Status)

A Firewall's page lists the Policies and NAT Policies that reach it, and links to its Policy Rules in firewall order. The Device or Virtual Machine page shows its Firewall.
