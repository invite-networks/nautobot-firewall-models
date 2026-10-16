# HAGroup

Two Firewalls running as a high availability pair.

## Attributes

* Name (string, unique)
* Description (optional, string)
* Management Address (FK to IPAddress, required)
    * The management address the pair shares.
* Firewalls
    * The two Firewalls in the pair, picked on the HA Group's form, which requires exactly two. A Firewall can be in only one HA Group. Over the REST API, a Firewall joins an HA Group through its own `ha_group` field, and a full group refuses a third.
* Status (FK to Status)
