"""Models for the Firewall app."""
# pylint: disable=duplicate-code, too-many-lines

from django.core.exceptions import ValidationError
from django.db import models
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models.generics import BaseModel, PrimaryModel
from nautobot.extras.models import StatusField
from nautobot.extras.utils import extras_features

from nautobot_firewall_models import choices
from nautobot_firewall_models.models.address import host_relative_names, render_addresses
from nautobot_firewall_models.models.zone import expand_zones
from nautobot_firewall_models.utils import get_default_status, model_to_json

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
    "webhooks",
)
class PolicyBand(PrimaryModel):
    """
    A PolicyBand is a section of a firewall policy, such as Global Deny or Medium Trust.

    Bands are evaluated in index order. Every PolicyRule belongs to a band, which decides where the rule lands.
    """

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    index = models.PositiveSmallIntegerField(unique=True, help_text="Bands are evaluated from lowest to highest.")
    description = models.CharField(max_length=1024, blank=True)

    class Meta:
        """Meta class."""

        ordering = ["index"]
        verbose_name_plural = "Policy Bands"

    def __str__(self):
        """Stringify instance."""
        return self.name


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    # "graphql" is omitted on purpose: nautobot_firewall_models.graphql.types provides a custom type.
    "relationships",
    "statuses",
    "webhooks",
)
class PolicyRule(PrimaryModel):
    """
    A PolicyRule is a the equivalent of a single in a firewall policy or access list.

    Firewall policies are typically made up of several individual rules. The rule type decides which platform the rule
    is written for and so which fields it may use.
    """

    # Relations only a PAN-OS rule can express; an nftables host firewall has no zones, users or App-ID.
    PANOS_ONLY_RELATIONS = (
        "source_users",
        "source_user_groups",
        "source_zones",
        "source_zone_groups",
        "destination_zones",
        "destination_zone_groups",
        "applications",
        "application_groups",
    )
    # Relations only an nftables rule can express; PAN-OS security rules match on destination service only.
    NFTABLES_ONLY_RELATIONS = (
        "source_services",
        "source_service_groups",
    )
    # Per rule type, the fields it requires and the fields it refuses, each with the error to show.
    TYPE_FIELDS = {
        "panos": (
            {"band": "PAN-OS rules need a Policy Band.", "position": "PAN-OS rules need a position."},
            {"chain": "Only nftables rules have a chain."},
        ),
        "nftables": (
            {"chain": "nftables rules need a chain."},
            {
                "band": "Only PAN-OS rules have a Policy Band.",
                "position": "Only PAN-OS rules have a position.",
                "negate_source": "Only PAN-OS rules can negate an address.",
                "negate_destination": "Only PAN-OS rules can negate an address.",
            },
        ),
    }
    ADDRESS_RELATIONS = (
        "source_addresses",
        "source_address_groups",
        "destination_addresses",
        "destination_address_groups",
    )

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    rule_type = models.CharField(
        choices=choices.RULE_TYPE_CHOICES,
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name="Rule Type",
        help_text="The platform the rule is written for. It cannot be changed once the rule exists.",
    )
    source_users = models.ManyToManyField(
        blank=True, to="nautobot_firewall_models.UserObject", related_name="policy_rules", verbose_name="Source Users"
    )
    source_user_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.UserObjectGroup",
        related_name="policy_rules",
        verbose_name="Source User Groups",
    )
    source_addresses = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.AddressObject",
        related_name="source_policy_rules",
        verbose_name="Source Addresses",
    )
    source_address_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.AddressObjectGroup",
        related_name="source_policy_rules",
        verbose_name="Source Address Groups",
    )
    source_zones = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.Zone",
        related_name="source_policy_rules",
        verbose_name="Source Zones",
    )
    source_zone_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.ZoneGroup",
        related_name="source_policy_rules",
        verbose_name="Source Zone Groups",
    )
    source_services = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.ServiceObject",
        related_name="source_policy_rules",
        verbose_name="Source Services",
    )
    source_service_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.ServiceObjectGroup",
        related_name="source_policy_rules",
        verbose_name="Source Service Groups",
    )
    destination_addresses = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.AddressObject",
        related_name="destination_policy_rules",
        verbose_name="Destination Addresses",
    )
    destination_address_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.AddressObjectGroup",
        related_name="destination_policy_rules",
        verbose_name="Destination Address Groups",
    )
    destination_zones = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.Zone",
        related_name="destination_policy_rules",
        verbose_name="Destination Zones",
    )
    destination_zone_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.ZoneGroup",
        related_name="destination_policy_rules",
        verbose_name="Destination Zone Groups",
    )
    destination_services = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.ServiceObject",
        related_name="destination_policy_rules",
        verbose_name="Destination Services",
    )
    destination_service_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.ServiceObjectGroup",
        related_name="destination_policy_rules",
        verbose_name="Destination Service Groups",
    )
    action = models.CharField(choices=choices.ACTION_CHOICES, max_length=CHARFIELD_MAX_LENGTH)
    log = models.BooleanField(default=False)
    negate_source = models.BooleanField(
        default=False,
        verbose_name="Negate Source",
        help_text="PAN-OS only. Match every source except the addresses set.",
    )
    negate_destination = models.BooleanField(
        default=False,
        verbose_name="Negate Destination",
        help_text="PAN-OS only. Match every destination except the addresses set.",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )
    applications = models.ManyToManyField(
        blank=True, to="nautobot_firewall_models.ApplicationObject", related_name="policy_rules"
    )
    application_groups = models.ManyToManyField(
        blank=True,
        to="nautobot_firewall_models.ApplicationObjectGroup",
        related_name="policy_rules",
        verbose_name="Application Groups",
    )
    request_id = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True, verbose_name="Request ID")
    description = models.CharField(max_length=1024, blank=True)
    band = models.ForeignKey(
        to="nautobot_firewall_models.PolicyBand",
        on_delete=models.PROTECT,
        related_name="policy_rules",
        null=True,
        blank=True,
        help_text="Required on PAN-OS rules.",
    )
    position = models.CharField(
        choices=choices.POSITION_CHOICES,
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        help_text=(
            "PAN-OS only. Pre Rules come before the band's local rules on the firewall and Post Rules after. "
            "Final rules, which deny or drop, are always last in the band."
        ),
    )
    chain = models.CharField(
        choices=choices.CHAIN_CHOICES,
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        help_text="Required on nftables rules.",
    )
    index = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Orders rules within a band and position. Rules may share an index."
    )

    clone_fields = [
        "rule_type",
        "band",
        "position",
        "chain",
        "source_users",
        "source_user_groups",
        "source_addresses",
        "source_address_groups",
        "source_zones",
        "source_zone_groups",
        "source_services",
        "source_service_groups",
        "destination_addresses",
        "destination_address_groups",
        "destination_zones",
        "destination_zone_groups",
        "destination_services",
        "destination_service_groups",
        "action",
        "log",
        "status",
    ]
    natural_key_field_names = ["pk"]

    class Meta:
        """Meta class."""

        # Band, then Pre Rules, Post Rules and Final rules, then chain, then index, then name so rules sharing an
        # index keep a stable order. nftables rules have no band and sort after PAN-OS rules.
        ordering = [
            models.F("band__index").asc(nulls_last=True),
            models.Case(models.When(position="pre", then=0), models.When(position="post", then=1), default=2),
            "chain",
            models.F("index").asc(nulls_last=True),
            "name",
        ]
        verbose_name_plural = "Policy Rules"

    def rule_details(self):
        """Convience method to convert to more consumable dictionary."""
        row = {}
        row["rule"] = self
        row["rule_type"] = self.rule_type
        row["band"] = self.band
        row["position"] = self.position
        row["chain"] = self.chain
        row["source_address_groups"] = self.source_address_groups.all()
        row["source_addresses"] = self.source_addresses.all()
        row["source_users"] = self.source_users.all()
        row["source_user_groupes"] = self.source_user_groups.all()
        row["source_zones"] = self.source_zones.all()
        row["source_zone_groups"] = self.source_zone_groups.all()
        row["source_services"] = self.source_services.all()
        row["source_service_groups"] = self.source_service_groups.all()

        row["destination_address_groups"] = self.destination_address_groups.all()
        row["destination_addresses"] = self.destination_addresses.all()
        row["destination_zones"] = self.destination_zones.all()
        row["destination_zone_groups"] = self.destination_zone_groups.all()
        row["destination_services"] = self.destination_services.all()
        row["destination_service_groups"] = self.destination_service_groups.all()

        row["negate_source"] = self.negate_source
        row["negate_destination"] = self.negate_destination
        row["action"] = self.action
        row["log"] = self.log
        row["status"] = self.status
        row["request_id"] = self.request_id
        return row

    def clean(self):
        """Require the fields the rule type needs and refuse the ones it cannot use."""
        super().clean()
        errors = {}
        required, refused = self.TYPE_FIELDS.get(self.rule_type, ({}, {}))
        # serializable_value() reads a foreign key's id, so checking the band does not load it.
        errors.update({field: msg for field, msg in required.items() if not self.serializable_value(field)})
        errors.update({field: msg for field, msg in refused.items() if self.serializable_value(field)})
        if self.rule_type == "nftables" and self.action == "remark":
            errors["action"] = "nftables rules cannot be remarks."
        if self.position == "final" and self.action not in choices.FINAL_ACTIONS:
            errors["action"] = "A Final rule closes the band, so it must deny or drop."
        if self.present_in_database:
            saved_type = PolicyRule.objects.filter(pk=self.pk).values_list("rule_type", flat=True).first()
            if saved_type and saved_type != self.rule_type:
                errors["rule_type"] = "The rule type cannot be changed once the rule exists."
        if errors:
            raise ValidationError(errors)

    @classmethod
    def validate_relations(cls, rule_type, relations):
        """Refuse related objects that the rule type cannot render.

        `relations` maps a many-to-many field name to the objects being assigned. Forms and the API call this, since
        many-to-many values are not on the instance when `clean()` runs.
        """
        errors = {}
        if rule_type == "nftables":
            for field in cls.PANOS_ONLY_RELATIONS:
                if relations.get(field):
                    errors[field] = "Only PAN-OS rules can use this."
        elif rule_type == "panos":
            for field in cls.NFTABLES_ONLY_RELATIONS:
                if relations.get(field):
                    errors[field] = "Only nftables rules can use this."
            for field in cls.ADDRESS_RELATIONS:
                if names := host_relative_names(relations.get(field)):
                    errors[field] = (
                        f"Device and dynamic Address Objects resolve per host and only work on nftables rules: "
                        f"{', '.join(names)}."
                    )
        if errors:
            raise ValidationError(errors)

    def rendered_source_addresses(self):
        """Return the source Address Objects to render, including the members of every flattened group."""
        return render_addresses(self.source_addresses, self.source_address_groups)[0]

    def rendered_source_address_groups(self):
        """Return the source Address Object Groups to render, leaving out every flattened group."""
        return render_addresses(self.source_addresses, self.source_address_groups)[1]

    def rendered_destination_addresses(self):
        """Return the destination Address Objects to render, including the members of every flattened group."""
        return render_addresses(self.destination_addresses, self.destination_address_groups)[0]

    def rendered_destination_address_groups(self):
        """Return the destination Address Object Groups to render, leaving out every flattened group."""
        return render_addresses(self.destination_addresses, self.destination_address_groups)[1]

    def expanded_source_zones(self):
        """Return the source Zones with every source ZoneGroup expanded into its member Zones."""
        return expand_zones(self.source_zones, self.source_zone_groups)

    def expanded_destination_zones(self):
        """Return the destination Zones with every destination ZoneGroup expanded into its member Zones."""
        return expand_zones(self.destination_zones, self.destination_zone_groups)

    def to_json(self):
        """Convience method to convert to json."""
        return model_to_json(self)

    def __str__(self):
        """Stringify instance."""
        if self.request_id and self.name:
            return f"{self.name} - {self.request_id}"
        if self.name:
            return self.name
        return str(self.id)


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
class Policy(PrimaryModel):
    """
    The overarching model that is the full firewall policy with all underlying rules and child objects.

    Each Policy can be assigned to both devices and to dynamic groups which in turn can assign the policy to a related device.
    """

    description = models.CharField(
        max_length=1024,
        blank=True,
    )
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    rule_type = models.CharField(
        choices=choices.RULE_TYPE_CHOICES,
        max_length=CHARFIELD_MAX_LENGTH,
        verbose_name="Rule Type",
        help_text="Every rule in the Policy must be of this type. It cannot be changed once the Policy exists.",
    )
    policy_rules = models.ManyToManyField(
        to=PolicyRule, blank=True, related_name="policies", verbose_name="Policy Rules"
    )
    assigned_devices = models.ManyToManyField(
        to="dcim.Device",
        through="PolicyDeviceM2M",
        related_name="firewall_policies",
        blank=True,
        verbose_name="Assigned Devices",
    )
    assigned_dynamic_groups = models.ManyToManyField(
        to="extras.DynamicGroup",
        through="PolicyDynamicGroupM2M",
        related_name="firewall_policies",
        blank=True,
        verbose_name="Assigned Dynamic Groups",
    )
    status = StatusField(
        on_delete=models.PROTECT,
        related_name="%(app_label)s_%(class)s_related",  # e.g. dcim_device_related
        default=get_default_status,
    )
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="policies",
        blank=True,
        null=True,
    )

    class Meta:
        """Meta class."""

        ordering = ["name"]
        verbose_name_plural = "Policies"

    def clean(self):
        """Keep the rule type of a saved Policy."""
        super().clean()
        if self.present_in_database:
            saved_type = Policy.objects.filter(pk=self.pk).values_list("rule_type", flat=True).first()
            if saved_type and saved_type != self.rule_type:
                raise ValidationError({"rule_type": "The rule type cannot be changed once the Policy exists."})

    @staticmethod
    def validate_policy_rules(rule_type, policy_rules):
        """Refuse Policy Rules whose type differs from the Policy's."""
        if not rule_type:
            return
        if mismatched := sorted(str(i) for i in policy_rules or [] if i.rule_type != rule_type):
            raise ValidationError(
                {"policy_rules": f"Only {rule_type} rules can be added to this Policy: {', '.join(mismatched)}."}
            )

    @property
    def policy_details(self):
        """Convience method to convert to a Python list of dictionaries."""
        data = []
        for policy_rule in self.policy_rules.all():
            data.append(policy_rule.rule_details())
        return data

    def to_json(self):
        """Convience method to convert to json."""
        return model_to_json(self)

    def __str__(self):
        """Stringify instance."""
        return self.name


###########################
# Through Models
###########################


class PolicyDeviceM2M(BaseModel):
    """Through model to add weight to the the Policy & Device relationship."""

    policy = models.ForeignKey("nautobot_firewall_models.Policy", on_delete=models.CASCADE)
    device = models.ForeignKey("dcim.Device", on_delete=models.PROTECT)
    weight = models.PositiveSmallIntegerField(default=100)

    class Meta:
        """Meta class."""

        ordering = ["weight"]
        unique_together = ["policy", "device"]

    def __str__(self):
        """Stringify instance."""
        return f"{self.policy.name} - {self.device.name} - {self.weight}"


class PolicyDynamicGroupM2M(BaseModel):
    """Through model to add weight to the the Policy & DynamicGroup relationship."""

    policy = models.ForeignKey("nautobot_firewall_models.Policy", on_delete=models.CASCADE)
    dynamic_group = models.ForeignKey("extras.DynamicGroup", on_delete=models.PROTECT, verbose_name="Dynamic Group")
    weight = models.PositiveSmallIntegerField(default=100)

    class Meta:
        """Meta class."""

        ordering = ["weight"]
        unique_together = ["policy", "dynamic_group"]

    def __str__(self):
        """Stringify instance."""
        return f"{self.policy.name} - {self.dynamic_group.name} - {self.weight}"
