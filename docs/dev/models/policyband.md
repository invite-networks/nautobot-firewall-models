# PolicyBand

A section of a firewall policy, such as Global Deny, Universal, or Medium Trust. Bands set the order rules are deployed in: every Policy Rule belongs to one band, and bands are evaluated from the lowest index to the highest.

Within a band, each rule is either a Header rule or a Closer rule. Header rules are deployed at the top of the band and Closer rules at the bottom, such as a terminal deny. Rules created directly on the firewall, outside Nautobot, are expected to sit between a band's Header and Closer rules.

## Attributes

* Name (string, unique)
    * Also used as the band's trust-state tag by deployment tooling.
* Index (int, unique)
    * Bands are evaluated from lowest to highest.
* Description (optional, string)
* Tags (M2M to Tag)
