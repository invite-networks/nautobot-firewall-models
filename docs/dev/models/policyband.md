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
* Trust Band (boolean, default false)
    * Marks a band that must end with an explicit deny, such as Low Trust or Medium Trust, unlike bands such as Universal or Managed. A Trust Band without a Final deny or drop rule is reported, not blocked: its page shows a warning, the band list marks its Final Rule as Missing, the REST API returns `missing_final_rule: true`, and `?missing_final_rule=true` lists every such band. Deployment tooling can refuse to push a band that is missing its Final rule.
* Description (optional, string)
* Tags (M2M to Tag)
