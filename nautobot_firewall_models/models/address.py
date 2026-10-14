"""Models for the Firewall app."""
# pylint: disable=duplicate-code, too-many-lines

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.constraints import UniqueConstraint
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models.generics import PrimaryModel
from nautobot.extras.models import StatusField
from nautobot.extras.utils import extras_features
from nautobot.ipam.fields import VarbinaryIPField
from netaddr import IPAddress, IPNetwork

from nautobot_firewall_models import choices
from nautobot_firewall_models.utils import get_default_status

ADDRESS_TYPES = ["fqdn", "ip_range", "ip_address", "prefix", "device", "dynamic"]

# Reverse relations from an Address Object or Address Object Group to the rules using it. PAN-OS Policy Rules and every
# NAT Policy Rule can not render an address that only resolves per host.
POLICY_RULE_RELATIONS = ("source_policy_rules", "destination_policy_rules")
NAT_POLICY_RULE_RELATIONS = (
    "original_source_nat_policy_rules",
    "translated_source_nat_policy_rules",
    "original_destination_nat_policy_rules",
    "translated_destination_nat_policy_rules",
)


def host_relative_names(objects):
    """Return the names of the host relative Address Objects in `objects`, looking inside any Address Object Groups."""
    names = set()
    for obj in objects or []:
        if isinstance(obj, AddressObjectGroup):
            names.update(str(i) for i in obj.address_objects.all() if i.is_host_relative)
        elif obj.is_host_relative:
            names.add(str(obj))
    return sorted(names)


def rules_refusing_host_relative(obj):
    """Return the names of the rules that use `obj`, an Address Object or Group, and can not take host relative ones."""
    if not obj.present_in_database:
        return []
    rules = set()
    for relation in POLICY_RULE_RELATIONS:
        rules.update(str(i) for i in getattr(obj, relation).filter(rule_type="panos"))
    for relation in NAT_POLICY_RULE_RELATIONS:
        rules.update(str(i) for i in getattr(obj, relation).all())
    return sorted(rules)


###########################
# Core Models
###########################


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class IPRange(PrimaryModel):
    """IPRange model to track ranges of IPs in firewall rules."""

    start_address = VarbinaryIPField(
        null=False,
        db_index=True,
        help_text="Starting IPv4 or IPv6 host address",
    )
    end_address = VarbinaryIPField(
        null=False,
        db_index=True,
        help_text="Ending IPv4 or IPv6 host address",
    )
    vrf = models.ForeignKey(
        to="ipam.VRF", on_delete=models.PROTECT, related_name="ip_ranges", blank=True, null=True, verbose_name="VRF"
    )
    description = models.CharField(
        max_length=1024,
        blank=True,
    )
    size = models.PositiveIntegerField(editable=False)
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["start_address"]
        verbose_name = "IP Range"
        verbose_name_plural = "IP Ranges"
        constraints = [
            UniqueConstraint(fields=["start_address", "end_address", "vrf"], name="unique_with_vrf"),
            UniqueConstraint(fields=["start_address", "end_address"], condition=Q(vrf=None), name="unique_without_vrf"),
        ]

    def __str__(self):
        """Stringify instance."""
        return f"{self.start_address}-{self.end_address}"

    def save(self, *args, **kwargs):
        """Overloads to inject size attr."""
        # Record the range's size (number of IP addresses)
        self.clean()
        self.size = int(IPAddress(self.end_address) - IPAddress(self.start_address)) + 1
        super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """Overloads to validate attr for form verification."""
        if not getattr(self, "start_address") or not getattr(self, "end_address"):
            raise ValidationError("Must have `start_address` and `end_address`.")
        if IPAddress(self.start_address) > IPAddress(self.end_address):
            raise ValidationError("`end_address` must be >= than `start_address`.")

        super().clean(*args, **kwargs)


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class FQDN(PrimaryModel):
    """Models fully qualified domain names, can be used on some firewall in place of a static IP."""

    description = models.CharField(
        max_length=1024,
        blank=True,
    )
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        unique=True,
        help_text="Resolvable fully qualified domain name (e.g. networktocode.com)",
    )
    ip_addresses = models.ManyToManyField(
        to="ipam.IPAddress",
        related_name="fqdns",
        blank=True,
        help_text="IP(s) an FQDN should resolve to.",
        verbose_name="IP Addresses",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name = "FQDN"
        verbose_name_plural = "FQDNs"

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class AddressObject(PrimaryModel):
    """Intermediate model to aggregate underlying address items, to allow for easier management."""

    description = models.CharField(
        max_length=1024,
        blank=True,
    )
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, unique=True, help_text="Name descriptor for an address object type."
    )
    fqdn = models.ForeignKey(
        to="nautobot_firewall_models.FQDN",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="address_objects",
        verbose_name="FQDN",
    )
    ip_range = models.ForeignKey(
        to="nautobot_firewall_models.IPRange",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="address_objects",
        verbose_name="IP Range",
    )
    ip_address = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="address_objects",
        verbose_name="IP Address",
    )
    prefix = models.ForeignKey(
        to="ipam.Prefix", on_delete=models.PROTECT, null=True, blank=True, related_name="address_objects"
    )
    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="address_objects",
        help_text="Resolves to the primary IPs of this Device.",
    )
    dynamic = models.CharField(
        choices=choices.DYNAMIC_ADDRESS_CHOICES,
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        help_text="Resolves when rendered for a host, e.g. Subnet becomes the prefix of the host's primary IP.",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name_plural = "Address Objects"

    def get_address_info(self):
        """Method to Return the actual AddressObject type."""
        for key in ADDRESS_TYPES:
            if getattr(self, key):
                return (key, getattr(self, key))
        return (None, None)

    def __str__(self):
        """Stringify instance."""
        return self.name

    def save(self, *args, **kwargs):
        """Overloads to enforce clear."""
        self.clean()
        super().save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        """Overloads to validate attr for form verification."""
        address_count = sum(1 for i in ADDRESS_TYPES if getattr(self, i, None))
        if address_count != 1:
            raise ValidationError(f"Must specify only one address from type {ADDRESS_TYPES}, {address_count} found.")
        if self.is_host_relative:
            rules = set(rules_refusing_host_relative(self))
            if self.present_in_database:
                for group in self.address_object_groups.all():
                    rules.update(rules_refusing_host_relative(group))
            if rules:
                raise ValidationError(
                    f"Device and dynamic Address Objects only work on nftables rules, and this one is used by: "
                    f"{', '.join(sorted(rules))}."
                )

        super().clean(*args, **kwargs)

    @property
    def address(self):
        """Returns the assigned address object."""
        return self.get_address_info()[1]

    @property
    def is_host_relative(self):
        """Whether this object only has a value once rendered for a specific host, so only host firewalls can use it."""
        return bool(self.dynamic or self.device_id)

    def resolve(self, host):
        """Return the networks this object stands for when rendered for `host`, the Device the rules are applied to.

        Only Device and dynamic objects are resolved here; other objects already hold their value.
        """
        if self.device_id:
            ips = [self.device.primary_ip4, self.device.primary_ip6]
            networks = [IPNetwork(ip.host) for ip in ips if ip]
            if not networks:
                raise ValidationError(f"{self}: Device {self.device} has no primary IP.")
            return networks
        if self.dynamic == "subnet":
            ips = [ip for ip in (host.primary_ip4, host.primary_ip6) if ip]
            if not ips:
                raise ValidationError(f"{self}: Device {host} has no primary IP.")
            if missing := [str(ip) for ip in ips if not ip.parent]:
                raise ValidationError(f"{self}: no Prefix contains {', '.join(missing)} on Device {host}.")
            return [ip.parent.prefix for ip in ips]
        raise ValueError(f"{self} is not a host relative address object.")


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "statuses",
    "webhooks",
)
class AddressObjectGroup(PrimaryModel):
    """Groups together AddressObjects to better mimic grouping sets of address objects that have a some commonality."""

    description = models.CharField(
        max_length=1024,
        blank=True,
    )
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, unique=True, help_text="Name descriptor for a group address objects."
    )
    address_objects = models.ManyToManyField(
        to="nautobot_firewall_models.AddressObject",
        related_name="address_object_groups",
        blank=True,
        verbose_name="Address Objects",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name_plural = "Address Object Groups"

    def __str__(self):
        """Stringify instance."""
        return self.name

    def validate_address_objects(self, address_objects):
        """Refuse host relative Address Objects while a PAN-OS or NAT Policy Rule uses this group."""
        names = host_relative_names(address_objects)
        rules = rules_refusing_host_relative(self) if names else []
        if rules:
            raise ValidationError(
                {
                    "address_objects": f"{', '.join(names)} only work on nftables rules, and this group is used by: "
                    f"{', '.join(rules)}."
                }
            )
