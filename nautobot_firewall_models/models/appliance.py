"""Models for the firewall appliances that Policies, NAT Policies and Zones are assigned to."""

from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models.generics import PrimaryModel
from nautobot.extras.models import StatusField
from nautobot.extras.utils import extras_features

from nautobot_firewall_models.utils import get_default_status

HA_GROUP_SIZE = 2


def refuse_ha_members(field, firewalls):
    """Return an error for `field` naming the Firewalls in `firewalls` that belong to an HA Group, if any.

    A Firewall in an HA Group shares its configuration with its peer, so it is selected through the HA Group.
    """
    if names := sorted(str(i) for i in firewalls or [] if i.ha_group_id):
        return {field: f"These Firewalls are in an HA Group, so select the HA Group instead: {', '.join(names)}."}
    return {}


class AssignedPoliciesMixin:
    """List the Policies and NAT Policies that reach a Firewall, HA Group or Firewall Group.

    Each model defines `assignment_filter(prefix)`, a Q matching policies assigned to it in any way.
    """

    def assigned_policies(self):
        """Return the Policies that reach this object."""
        policy = apps.get_model("nautobot_firewall_models", "Policy")
        return policy.objects.filter(self.assignment_filter()).distinct()

    def assigned_nat_policies(self):
        """Return the NAT Policies that reach this object."""
        nat_policy = apps.get_model("nautobot_firewall_models", "NATPolicy")
        return nat_policy.objects.filter(self.assignment_filter()).distinct()


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
class HAGroup(AssignedPoliciesMixin, PrimaryModel):
    """Two Firewalls running as a high availability pair, sharing one management address."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=1024, blank=True)
    management_address = models.ForeignKey(
        to="ipam.IPAddress",
        on_delete=models.PROTECT,
        related_name="ha_groups",
        verbose_name="Management Address",
        help_text="The management address the pair shares.",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name = "HA Group"
        verbose_name_plural = "HA Groups"

    def __str__(self):
        """Stringify instance."""
        return self.name

    def assignment_filter(self, prefix=""):
        """Return a Q matching objects assigned to this HA Group directly or through a Firewall Group."""
        return models.Q(**{f"{prefix}assigned_ha_groups": self}) | models.Q(
            **{f"{prefix}assigned_firewall_groups__in": self.firewall_groups.all()}
        )


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
class Firewall(AssignedPoliciesMixin, PrimaryModel):
    """A PAN-OS firewall, bound to the Device or Virtual Machine it runs on."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=1024, blank=True)
    device = models.OneToOneField(
        to="dcim.Device", on_delete=models.PROTECT, null=True, blank=True, related_name="firewall"
    )
    virtual_machine = models.OneToOneField(
        to="virtualization.VirtualMachine",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="firewall",
        verbose_name="Virtual Machine",
    )
    ha_group = models.ForeignKey(
        to=HAGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="firewalls",
        verbose_name="HA Group",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]

    def __str__(self):
        """Stringify instance."""
        return self.name

    def clean(self):
        """Bind exactly one Device or Virtual Machine, and join an HA Group only where the Firewall is not used directly."""
        super().clean()
        if bool(self.device_id) == bool(self.virtual_machine_id):
            raise ValidationError("A Firewall is bound to exactly one Device or one Virtual Machine.")
        if self.ha_group_id:
            self._validate_ha_group()

    def _validate_ha_group(self):
        peers = Firewall.objects.filter(ha_group_id=self.ha_group_id).exclude(pk=self.pk)
        if peers.count() >= HA_GROUP_SIZE:
            raise ValidationError({"ha_group": f"An HA Group holds {HA_GROUP_SIZE} Firewalls and this one is full."})
        if uses := self.direct_uses():
            raise ValidationError(
                {
                    "ha_group": "A Firewall in an HA Group is used through the HA Group. Replace this Firewall with "
                    f"its HA Group in these first. {uses}."
                }
            )

    def direct_uses(self):
        """Describe where this Firewall is used directly, which it can not be once it is in an HA Group."""
        if not self.present_in_database:
            return ""
        uses = []
        for label, relation in (
            ("Firewall Groups", "firewall_groups"),
            ("Policies", "policies"),
            ("NAT Policies", "nat_policies"),
            ("Zones", "zones"),
        ):
            if names := sorted(str(i) for i in getattr(self, relation).all()):
                uses.append(f"{label}: {', '.join(names)}")
        return "; ".join(uses)

    @property
    def policy_rules_url(self):
        """Return the link to this Firewall's Policy Rules in firewall order."""
        return f"{reverse('plugins:nautobot_firewall_models:policyrule_list')}?firewall={self.pk}"

    def firewall_group_memberships(self):
        """Return the Firewall Groups holding this Firewall directly or through its HA Group."""
        held = models.Q(firewalls=self)
        if self.ha_group_id:
            held |= models.Q(ha_groups=self.ha_group_id)
        return FirewallGroup.objects.filter(held).distinct()

    def assignment_filter(self, prefix=""):
        """Return a Q matching objects assigned to this Firewall directly, through its HA Group or a Firewall Group.

        `prefix` is the path from the queried model to the object with the assignments, e.g. "policies__".
        """
        assigned = models.Q(**{f"{prefix}assigned_firewalls": self})
        if self.ha_group_id:
            assigned |= models.Q(**{f"{prefix}assigned_ha_groups": self.ha_group_id})
        assigned |= models.Q(**{f"{prefix}assigned_firewall_groups__in": self.firewall_group_memberships()})
        return assigned


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
class FirewallGroup(AssignedPoliciesMixin, PrimaryModel):
    """A set of Firewalls and HA Groups, so Policies and Zones can be assigned to all of them at once."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    description = models.CharField(max_length=1024, blank=True)
    firewalls = models.ManyToManyField(to=Firewall, blank=True, related_name="firewall_groups")
    ha_groups = models.ManyToManyField(to=HAGroup, blank=True, related_name="firewall_groups", verbose_name="HA Groups")
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]

    def __str__(self):
        """Stringify instance."""
        return self.name

    def assignment_filter(self, prefix=""):
        """Return a Q matching objects assigned to this Firewall Group."""
        return models.Q(**{f"{prefix}assigned_firewall_groups": self})

    @staticmethod
    def validate_members(firewalls):
        """Refuse Firewalls that are in an HA Group; the HA Group is the member instead."""
        if errors := refuse_ha_members("firewalls", firewalls):
            raise ValidationError(errors)
