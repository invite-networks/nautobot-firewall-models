"""Configurable signals."""

from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from nautobot.dcim.models import Device, Interface
from nautobot.extras.models import Status
from nautobot.ipam.models import VRF, IPAddress, Prefix

from nautobot_firewall_models import models
from nautobot_firewall_models.constants import PLUGIN_CFG
from nautobot_firewall_models.utils import create_configured_statuses, get_firewall_models_with_status_field

ON_DELETE = {
    IPAddress: ["fqdns", "address_objects"],
    Prefix: ["address_objects"],
    VRF: ["zones"],
    Device: ["zones", "address_objects"],
    Interface: ["zones"],
    models.FQDN: ["address_objects"],
    models.IPRange: ["address_objects"],
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
        "zone_groups",
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
    models.NATPolicyRule: [
        "nat_policies",
    ],
}

if PLUGIN_CFG["protect_on_delete"]:

    @receiver(pre_delete, sender=IPAddress)
    @receiver(pre_delete, sender=Prefix)
    @receiver(pre_delete, sender=VRF)
    @receiver(pre_delete, sender=Device)
    @receiver(pre_delete, sender=Interface)
    @receiver(pre_delete, sender=models.FQDN)
    @receiver(pre_delete, sender=models.IPRange)
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
    def on_delete_handler(instance, **kwargs):
        """Signal handler to enable on_delete=PROTECT."""
        for i in ON_DELETE[instance._meta.model]:
            if hasattr(instance, i) and getattr(instance, i).exists():
                raise ValidationError(f"{instance} is assigned to an {i} & `protect_on_delete` is enabled.")


# Many-to-many assignments that depend on a rule type or on host relative Address Objects. Forms and the REST API run
# the same checks first for friendly errors; this catches every other path, such as bulk edit and scripts.
# Each entry maps a through model to (field name, check), and check(owner, field, objects) raises ValidationError.
M2M_CHECKS = {
    **{
        getattr(models.PolicyRule, field).through: (
            field,
            lambda rule, field, objects: models.PolicyRule.validate_relations(rule.rule_type, {field: objects}),
        )
        for field in (*models.PolicyRule.PANOS_ONLY_RELATIONS, *models.PolicyRule.ADDRESS_RELATIONS)
    },
    **{
        getattr(models.NATPolicyRule, field).through: (
            field,
            lambda rule, field, objects: models.NATPolicyRule.validate_relations({field: objects}),
        )
        for field in models.NATPolicyRule.ADDRESS_RELATIONS
    },
    models.AddressObjectGroup.address_objects.through: (
        "address_objects",
        lambda group, _field, objects: group.validate_address_objects(objects),
    ),
    models.Policy.policy_rules.through: (
        "policy_rules",
        lambda policy, _field, objects: models.Policy.validate_policy_rules(policy.rule_type, objects),
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
    for status in Status.objects.filter(name__in=["Active", "Staged", "Decommissioned"]):
        content_types = get_firewall_models_with_status_field()
        status.content_types.add(*content_types)
