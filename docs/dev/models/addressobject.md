# AddressObject

Defines an object representation of some form of an IP object for cleaner nesting and modeling. Each Address Object can have only ONE IP object type associated to it. The Address property will return the IP object related to the Address Object (e.g. if FQDN is set, `instance.address` would return the FQDN object).

## Attributes

* Name (string)
* Description (optional, string)
* FQDN (FK to FQDN)
* IP Address (FK to IPAddress)
* Prefix (FK to Prefix)
* Device (FK to Device)
    * Resolves to the Device's primary IPv4 and IPv6 addresses.
* Dynamic (string, choice of subnet)
    * Subnet resolves to the Prefix that contains the primary IP of the host the rules are rendered for.
* Status (FK to Status)
* Address (property that returns the assigned object)

Device and dynamic Address Objects only have a value for a specific host, so they can only be used on nftables Policy Rules. They are refused on PAN-OS Policy Rules and NAT Policy Rules, directly or through an Address Object Group, and an Address Object those rules already use cannot be changed into one. Call `resolve(host)` with the Device the rules are applied to for a list of networks. It raises a validation error when the host or referenced Device has no primary IP, or no Prefix contains it.

## Managed Locally

Set the status to Managed Locally for an object the firewall defines and maintains itself, such as the predefined PAN-OS External Dynamic List "Palo Alto Networks - High risk IP addresses". The object then holds only its name, so rules can reference it, and must not have an FQDN, IP Address, Prefix, Device or dynamic value. Deployment tooling references it by name and never pushes it.
