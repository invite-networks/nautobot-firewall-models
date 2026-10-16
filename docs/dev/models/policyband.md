# PolicyBand

A section of a firewall policy, such as Global Deny, Universal, or Medium Trust. Bands set the order rules are deployed in: every Policy Rule belongs to one band, and bands are evaluated from the lowest index to the highest.

Within a band, each rule is a Pre Rule, a Post Rule or the Final rule, deployed in this order:

1. Pre Rules, at the top of the band.
2. Rules created directly on the firewall, outside Nautobot.
3. Post Rules.
4. Final rules, the band's closing deny or drop rules. They are always last in the band, whatever their index, ordered among themselves by index and then name.

## Attributes

* Name (string, unique)
    * Also used as the band's trust-state tag by deployment tooling.
* Index (int, unique)
    * Bands are evaluated from lowest to highest.
* Description (optional, string)
* Tags (M2M to Tag)
