"""Set of choices to use in firewall models."""

from netutils.protocol_mapper import PROTO_NAME_TO_NUM

IP_PROTOCOL_CHOICES = tuple((i, i) for i in PROTO_NAME_TO_NUM.keys())  # pylint: disable=consider-iterating-dictionary

ACTION_CHOICES = (("allow", "allow"), ("deny", "deny"), ("drop", "drop"), ("remark", "remark"))

POSITION_CHOICES = (("header", "Header"), ("closer", "Closer"))

RULE_TYPE_CHOICES = (("panos", "PAN-OS"), ("nftables", "nftables"))

CHAIN_CHOICES = (("input", "Input"), ("forward", "Forward"), ("output", "Output"))

DYNAMIC_ADDRESS_CHOICES = (("subnet", "Subnet"),)
