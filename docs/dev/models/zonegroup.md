# ZoneGroup

Groups Zones so a single object can stand in for several of them on a Policy Rule or NAT Policy Rule.

Each Zone belongs to exactly one Zone Group, chosen on the Zone, so a group is created first and Zones are added to it from the Zone form or the Add Zone button on the group's page. A group cannot be deleted while it still has Zones.

## Attributes

* Name (string, unique)
* Description (optional, string)
* Zones (the Zones that belong to the group, set on each Zone)
* Status (FK to Status)
