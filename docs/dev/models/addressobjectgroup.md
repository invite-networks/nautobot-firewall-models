# AddressObjectGroup

Represents a group of Address Objects.

## Attributes

* Name (string)
* Description (optional, string)
* Address Objects (M2M to AddressObject)
* Address Object Groups (M2M to AddressObjectGroup)
    * Groups nested in this group, to any depth. A group cannot contain itself, directly or through another group. The form picks Address Objects and nested groups in one field.
* Flatten (boolean, default false)
    * When a rule is rendered, the group is replaced by its members: its Address Objects, plus its nested groups. A nested group that is also flattened is opened in turn, and one that is not stays a group. Use it to keep, for example, a group of country region codes in Nautobot while the firewall receives the individual countries. A flattened group that renders as nothing is kept as a group so a rule never widens to any address, and a Managed Locally group cannot be flattened.
* Status (FK to Status)

A group whose status is Managed Locally is defined on the firewall, so Nautobot holds only its name and the group cannot have members. Service, application and user object groups follow the same rule.

Checks that look inside a group, such as refusing Device and dynamic Address Objects under PAN-OS and NAT rules, look through nested groups at every level.
