"""Configurable signals."""

from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from nautobot.dcim.models import Device
from nautobot.extras.models import Status
from nautobot.ipam.models import VRF, IPAddress, Prefix

from nautobot_firewall_models import models
from nautobot_firewall_models.constants import PLUGIN_CFG
from nautobot_firewall_models.utils import (
    create_configured_statuses,
    create_managed_locally_status,
    get_firewall_models_with_status_field,
)

ON_DELETE = {
    IPAddress: ["fqdns", "address_objects"],
    Prefix: ["address_objects"],
    VRF: ["zones"],
    Device: ["address_objects"],
    models.FQDN: ["address_objects"],
    models.AddressObject: [
        "address_object_groups",
        "source_policy_rules",
        "destination_policy_rules",
        "original_source_nat_policy_rules",
        "translated_source_nat_policy_rules",
        "original_destination_nat_policy_rules",
        "translated_destination_nat_policy_rules",
    ],
    models.AddressObjectGroup: [
        "parent_groups",
        "source_policy_rules",
        "destination_policy_rules",
        "original_source_nat_policy_rules",
        "translated_source_nat_policy_rules",
        "original_destination_nat_policy_rules",
        "translated_destination_nat_policy_rules",
    ],
    models.ServiceObject: [
        "service_object_groups",
        "source_policy_rules",
        "destination_policy_rules",
        "original_source_nat_policy_rules",
        "translated_source_nat_policy_rules",
        "original_destination_nat_policy_rules",
        "translated_destination_nat_policy_rules",
    ],
    models.ServiceObjectGroup: [
        "source_policy_rules",
        "destination_policy_rules",
        "original_source_nat_policy_rules",
        "translated_source_nat_policy_rules",
        "original_destination_nat_policy_rules",
        "translated_destination_nat_policy_rules",
    ],
    models.ApplicationObject: [
        "application_object_groups",
        "destination_policy_rules",
    ],
    models.ApplicationObjectGroup: [
        "destination_policy_rules",
    ],
    models.UserObject: [
        "user_object_groups",
        "policy_rules",
    ],
    models.UserObjectGroup: [
        "policy_rules",
    ],
    models.Zone: [
        "source_policy_rules",
        "destination_policy_rules",
        "source_nat_policy_rules",
        "destination_nat_policy_rules",
    ],
    models.ZoneGroup: [
        "source_policy_rules",
        "destination_policy_rules",
        "source_nat_policy_rules",
        "destination_nat_policy_rules",
    ],
    models.PolicyRule: [
        "policies",
    ],
    models.Firewall: ["firewall_groups", "policies", "nat_policies", "zones"],
    models.HAGroup: ["firewalls", "firewall_groups", "policies", "nat_policies", "zones"],
    models.FirewallGroup: ["policies", "nat_policies", "zones"],
    models.NATPolicyRule: [
        "nat_policies",
    ],
}

if PLUGIN_CFG["protect_on_delete"]:

    @receiver(pre_delete, sender=IPAddress)
    @receiver(pre_delete, sender=Prefix)
    @receiver(pre_delete, sender=VRF)
    @receiver(pre_delete, sender=Device)
    @receiver(pre_delete, sender=models.FQDN)
    @receiver(pre_delete, sender=models.AddressObject)
    @receiver(pre_delete, sender=models.AddressObjectGroup)
    @receiver(pre_delete, sender=models.ServiceObject)
    @receiver(pre_delete, sender=models.ServiceObjectGroup)
    @receiver(pre_delete, sender=models.ApplicationObject)
    @receiver(pre_delete, sender=models.ApplicationObjectGroup)
    @receiver(pre_delete, sender=models.UserObject)
    @receiver(pre_delete, sender=models.UserObjectGroup)
    @receiver(pre_delete, sender=models.Zone)
    @receiver(pre_delete, sender=models.ZoneGroup)
    @receiver(pre_delete, sender=models.PolicyRule)
    @receiver(pre_delete, sender=models.NATPolicyRule)
    @receiver(pre_delete, sender=models.Firewall)
    @receiver(pre_delete, sender=models.HAGroup)
    @receiver(pre_delete, sender=models.FirewallGroup)
    def on_delete_handler(instance, **kwargs):
        """Signal handler to enable on_delete=PROTECT."""
        for i in ON_DELETE[instance._meta.model]:
            if hasattr(instance, i) and getattr(instance, i).exists():
                raise ValidationError(f"{instance} is assigned to an {i} & `protect_on_delete` is enabled.")


def check_group_members(group, field, objects):
    """Refuse members on a Managed Locally group, and for Address Object Groups, loops and host relative members."""
    group.validate_managed_members(group.status, {field: objects})
    if isinstance(group, models.AddressObjectGroup):
        group.validate_members(**{field: objects})


# Many-to-many assignments that depend on a rule type, host relative Address Objects, Managed Locally groups or HA
# Groups. Forms and the REST API run
# the same checks first for friendly errors; this catches every other path, such as bulk edit and scripts.
# Each entry maps a through model to (field name, check), and check(owner, field, objects) raises ValidationError.
M2M_CHECKS = {
    **{
        getattr(models.PolicyRule, field).through: (
            field,
            lambda rule, field, objects: models.PolicyRule.validate_relations(
                rule.rule_type, {field: objects}, rule.panos_rule_type
            ),
        )
        for field in (
            *models.PolicyRule.PANOS_ONLY_RELATIONS,
            *models.PolicyRule.NFTABLES_ONLY_RELATIONS,
            *models.PolicyRule.ADDRESS_RELATIONS,
        )
    },
    **{
        getattr(models.NATPolicyRule, field).through: (
            field,
            lambda rule, field, objects: models.NATPolicyRule.validate_relations({field: objects}),
        )
        for field in (*models.NATPolicyRule.UNSUPPORTED_RELATIONS, *models.NATPolicyRule.ADDRESS_RELATIONS)
    },
    **{
        getattr(group, field).through: (field, check_group_members)
        for group in (
            models.AddressObjectGroup,
            models.ServiceObjectGroup,
            models.ApplicationObjectGroup,
            models.UserObjectGroup,
        )
        for field in group.members_fields
    },
    models.Policy.policy_rules.through: (
        "policy_rules",
        lambda policy, _field, objects: models.Policy.validate_policy_rules(policy.rule_type, objects),
    ),
    # Assignments to Firewalls, HA Groups and Firewall Groups. A Firewall in an HA Group is only used through it.
    **{
        getattr(models.Policy, field).through: (
            field,
            lambda policy, field, objects: models.Policy.validate_assignments(policy.rule_type, {field: objects}),
        )
        for field in ("assigned_firewalls", "assigned_ha_groups", "assigned_firewall_groups")
    },
    models.NATPolicy.assigned_firewalls.through: (
        "assigned_firewalls",
        lambda policy, field, objects: models.NATPolicy.validate_assignments({field: objects}),
    ),
    models.Zone.firewalls.through: ("firewalls", lambda zone, _field, objects: models.Zone.validate_bindings(objects)),
    models.FirewallGroup.firewalls.through: (
        "firewalls",
        lambda group, _field, objects: models.FirewallGroup.validate_members(objects),
    ),
}


def m2m_check_handler(sender, instance, action, **kwargs):
    """Run the M2M_CHECKS entry for objects about to be added, from either side of the relation."""
    if action != "pre_add" or not kwargs["pk_set"]:
        return
    field, check = M2M_CHECKS[sender]
    added = list(kwargs["model"].objects.filter(pk__in=kwargs["pk_set"]))
    if kwargs["reverse"]:
        for owner in added:
            check(owner, field, [instance])
    else:
        check(instance, field, added)


for through in M2M_CHECKS:
    m2m_changed.connect(m2m_check_handler, sender=through, dispatch_uid=f"firewall_m2m_check_{through._meta.label}")


def create_configured_statuses_signal(sender, **kwargs):  # pylint: disable=unused-argument
    """Signal handler to create default_status and allowed_status configured in the app config."""
    create_configured_statuses()


def associate_statuses_signal(sender, **kwargs):  # pylint: disable=unused-argument
    """Signal handler to associate some common statuses with the firewall model content types."""
    create_managed_locally_status()
    for status in Status.objects.filter(name__in=["Active", "Staged", "Decommissioned"]):
        content_types = get_firewall_models_with_status_field()
        status.content_types.add(*content_types)
