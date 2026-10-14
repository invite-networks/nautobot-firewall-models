# AddressObjectGroup

Represents a group of Address Objects.

## Attributes

* Name (string)
* Description (optional, string)
* Address Objects (M2M to AddressObject)
* Flatten (boolean, default false)
    * When a rule is rendered, the group is replaced by its Address Objects. Use it to keep, for example, a group of country region codes in Nautobot while the firewall receives the individual countries. An empty flattened group is kept as a group so a rule never widens to any address, and a Managed Locally group cannot be flattened.
* Status (FK to Status)

A group whose status is Managed Locally is defined on the firewall, so Nautobot holds only its name and the group cannot have members. Service, application and user object groups follow the same rule.
