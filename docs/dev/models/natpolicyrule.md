# NATPolicyRule

Represents a single network address translation rule in a NATPolicy.

It is recommended to use a descriptive name to best identify a NATPolicyRule, otherwise the string representation of the NATPolicyRule will be the UUID.

## Attributes

### Meta information

* Name (optional, string)
* Status (FK to Status)
* Tags (M2M to Tag)
* Source Zone (FK to Zone)
* Source Zone (FK to Zone)
* Request ID (optional, string)
    * Meant to represent an upstream request (e.g. an service request from an ITSM solution).
* Index (optional, int)
    * Orders the rule in the NAT Policy. Rules without an index come after every indexed rule, and rules sharing an index, or without one, are ordered by name.
* Log (boolean)

### Before translation

* Original Source Address (M2M to AddressObject)
* Original Source Address Group (M2M to AddressObjectGroup)
* Original Destination Address (M2M to AddressObject)
* Original Destination Address Group (M2M to AddressObjectGroup)
* Original Destination Service (M2M to ServiceObject)
* Original Destination Service Group (M2M to ServiceObjectGroup)

NAT rules have no source service. PAN-OS NAT matches on the original destination service and translates the destination port only, so Original and Translated Source Services exist in the data model but are refused.

### After translation

* Translated Source Address (M2M to AddressObject)
* Translated Source Address Group (M2M to AddressObjectGroup)
* Translated Destination Address (M2M to AddressObject)
* Translated Destination Address Group (M2M to AddressObjectGroup)
* Translated Destination Service (M2M to ServiceObject)
* Translated Destination Service Group (M2M to ServiceObjectGroup)
