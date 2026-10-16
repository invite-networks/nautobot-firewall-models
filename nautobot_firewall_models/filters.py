"""Filtering for nautobot_firewall_models."""

import django_filters
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q
from nautobot.apps.filters import (
    NaturalKeyOrPKMultipleChoiceFilter,
    NautobotFilterSet,
    SearchFilter,
    StatusModelFilterSetMixin,
)
from nautobot.dcim.models import Device
from nautobot.virtualization.models import VirtualMachine

from nautobot_firewall_models import models


def filter_by_firewall(queryset, firewalls, prefix):
    """Return the objects in `queryset` assigned to any of `firewalls`, directly, by HA Group or by Firewall Group.

    `prefix` is the path from the queryset's model to the policy holding the assignments, e.g. "policies__".
    """
    if not firewalls:
        return queryset
    assigned = Q()
    for firewall in firewalls:
        assigned |= firewall.assignment_filter(prefix)
    return queryset.filter(pk__in=queryset.model.objects.filter(assigned).values("pk"))


class BaseFilterSet(StatusModelFilterSetMixin, django_filters.filterset.FilterSet):
    """A base class for adding the search method to models which only expose the `name` and `description` fields."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
        }
    )


class FQDNFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for FQDN."""

    class Meta:
        """Meta attributes for filter."""

        model = models.FQDN
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class AddressObjectFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for AddressObject."""

    address_object_groups = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="address_object_groups",
        queryset=models.AddressObjectGroup.objects.all(),
        label="Address Object Groups (name or ID)",
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.AddressObject
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class AddressObjectGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for AddressObjectGroup."""

    class Meta:
        """Meta attributes for filter."""

        model = models.AddressObjectGroup
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class ApplicationObjectFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for ApplicationObject."""

    application_object_groups = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="application_object_groups",
        queryset=models.ApplicationObjectGroup.objects.all(),
        label="Application Object Groups (name or ID)",
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.ApplicationObject
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class ApplicationObjectGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for ApplicationObjectGroup."""

    class Meta:
        """Meta attributes for filter."""

        model = models.ApplicationObjectGroup
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class ServiceObjectFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for ServiceObject."""

    class Meta:
        """Meta attributes for filter."""

        model = models.ServiceObject
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class ServiceObjectGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for ServiceObjectGroup."""

    class Meta:
        """Meta attributes for filter."""

        model = models.ServiceObjectGroup
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class UserObjectFilterSet(NautobotFilterSet):
    """Filter for UserObject."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "username": "icontains",
        }
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.UserObject
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class UserObjectGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for UserObjectGroup."""

    class Meta:
        """Meta attributes for filter."""

        model = models.UserObjectGroup
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class ZoneFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for Zone."""

    zone_group = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="zone_group",
        queryset=models.ZoneGroup.objects.all(),
        label="Zone Group (name or ID)",
    )
    firewalls = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="firewalls", queryset=models.Firewall.objects.all(), label="Firewalls (name or ID)"
    )
    ha_groups = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="ha_groups", queryset=models.HAGroup.objects.all(), label="HA Groups (name or ID)"
    )
    firewall_groups = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="firewall_groups", queryset=models.FirewallGroup.objects.all(), label="Firewall Groups (name or ID)"
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.Zone
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class ZoneGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for ZoneGroup."""

    zones = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="zones",
        queryset=models.Zone.objects.all(),
        label="Zones (name or ID)",
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.ZoneGroup
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class PolicyBandFilterSet(NautobotFilterSet):
    """Filter for PolicyBand."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
        }
    )
    missing_final_rule = django_filters.BooleanFilter(
        method="filter_missing_final_rule", label="Trust Bands without a Final rule"
    )

    def filter_missing_final_rule(self, queryset, name, value):  # pylint: disable=unused-argument
        """Return the Trust Bands without a Final rule, or every other band when value is false."""
        bands_with_final = models.PolicyRule.objects.filter(position="final").values("band")
        missing = Q(trust_band=True) & ~Q(pk__in=bands_with_final)
        return queryset.filter(missing) if value else queryset.exclude(missing)

    class Meta:
        """Meta attributes for filter."""

        model = models.PolicyBand
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class PolicyRuleFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for PolicyRule."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
            "request_id": "icontains",
        }
    )
    band = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="band",
        queryset=models.PolicyBand.objects.all(),
        label="Policy Bands (name or ID)",
    )
    firewall = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.Firewall.objects.all(),
        method="filter_firewall",
        label="Firewalls (name or ID), through Policies assigned to them, their HA Group or a Firewall Group",
    )

    def filter_firewall(self, queryset, name, value):  # pylint: disable=unused-argument
        """Return the rules of every Policy assigned to the Firewalls, their HA Group or a Firewall Group."""
        return filter_by_firewall(queryset, value, "policies__")

    class Meta:
        """Meta attributes for filter."""

        model = models.PolicyRule
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class NATPolicyRuleFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for NATPolicyRule."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
            "request_id": "icontains",
        }
    )
    firewall = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.Firewall.objects.all(),
        method="filter_firewall",
        label="Firewalls (name or ID), through NAT Policies assigned to them, their HA Group or a Firewall Group",
    )

    def filter_firewall(self, queryset, name, value):  # pylint: disable=unused-argument
        """Return the rules of every NAT Policy assigned to the Firewalls, their HA Group or a Firewall Group."""
        return filter_by_firewall(queryset, value, "nat_policies__")

    class Meta:
        """Meta attributes for filter."""

        model = models.NATPolicyRule
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class PolicyFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for Policy."""

    class Meta:
        """Meta attributes for filter."""

        model = models.Policy
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class NATPolicyFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for NATPolicy."""

    class Meta:
        """Meta attributes for filter."""

        model = models.NATPolicy
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class FirewallFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for Firewall."""

    device = NaturalKeyOrPKMultipleChoiceFilter(queryset=Device.objects.all(), label="Device (name or ID)")
    virtual_machine = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=VirtualMachine.objects.all(), label="Virtual Machine (name or ID)"
    )
    ha_group = NaturalKeyOrPKMultipleChoiceFilter(queryset=models.HAGroup.objects.all(), label="HA Group (name or ID)")
    firewall_groups = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.FirewallGroup.objects.all(), label="Firewall Groups (name or ID)"
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.Firewall
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class HAGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for HAGroup."""

    firewalls = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.Firewall.objects.all(), label="Firewalls (name or ID)"
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.HAGroup
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class FirewallGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for FirewallGroup."""

    firewalls = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.Firewall.objects.all(), label="Firewalls (name or ID)"
    )
    ha_groups = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=models.HAGroup.objects.all(), label="HA Groups (name or ID)"
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.FirewallGroup
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]
