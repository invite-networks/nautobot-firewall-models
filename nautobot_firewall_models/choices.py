"""Set of choices to use in firewall models."""

from netutils.protocol_mapper import PROTO_NAME_TO_NUM

IP_PROTOCOL_CHOICES = tuple((i, i) for i in PROTO_NAME_TO_NUM.keys())  # pylint: disable=consider-iterating-dictionary

ACTION_CHOICES = (("allow", "allow"), ("deny", "deny"), ("drop", "drop"), ("remark", "remark"))

POSITION_CHOICES = (("pre", "Pre Rules"), ("post", "Post Rules"), ("final", "Final"))

# Actions a Final rule may take: it is the band's closing deny.
FINAL_ACTIONS = ("deny", "drop")

RULE_TYPE_CHOICES = (("panos", "PAN-OS"), ("nftables", "nftables"))

CHAIN_CHOICES = (("input", "Input"), ("forward", "Forward"), ("output", "Output"))

DYNAMIC_ADDRESS_CHOICES = (("subnet", "Subnet"),)
