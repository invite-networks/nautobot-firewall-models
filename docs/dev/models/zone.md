# Zone

Zones are common on firewalls and are typically seen as representations of area (e.g. DMZ, trust, untrust).

## Attributes

* Name (string)
* Description (optional, string)
* Zone Group (FK to ZoneGroup, required)
    * The one Zone Group the Zone belongs to.
* VRFs (M2M to VRF)
* Devices (M2M to Device)
* Virtual Machines (M2M to VirtualMachine)
    * The Devices and Virtual Machines the Zone is bound to. The form picks both in one searchable field.
* Status (FK to Status)
