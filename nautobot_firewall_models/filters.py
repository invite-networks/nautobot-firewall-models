"""Filtering for nautobot_firewall_models."""

import django_filters
from django.contrib.contenttypes.fields import GenericRelation
from django.db.models import Q
from nautobot.apps.filters import (
    MultiValueCharFilter,
    NaturalKeyOrPKMultipleChoiceFilter,
    NautobotFilterSet,
    SearchFilter,
    StatusModelFilterSetMixin,
)
from nautobot.dcim.models import Device

from nautobot_firewall_models import models


class BaseFilterSet(StatusModelFilterSetMixin, django_filters.filterset.FilterSet):
    """A base class for adding the search method to models which only expose the `name` and `description` fields."""

    q = SearchFilter(
        filter_predicates={
            "name": "icontains",
            "description": "icontains",
        }
    )


class IPRangeFilterSet(BaseFilterSet, NautobotFilterSet):  # pylint: disable=too-many-ancestors
    """Filter for IPRange."""

    start_address = MultiValueCharFilter(
        label="Address",
    )
    end_address = MultiValueCharFilter(
        label="Address",
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.IPRange

        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


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

    zone_groups = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="zone_groups",
        queryset=models.ZoneGroup.objects.all(),
        label="Zone Groups (name or ID)",
    )
    devices = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="devices",
        queryset=Device.objects.all(),
        label="Devices (name or ID)",
    )

    class Meta:
        """Meta attributes for filter."""

        model = models.Zone
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class ZoneGroupFilterSet(BaseFilterSet, NautobotFilterSet):
    """Filter for ZoneGroup."""

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
    device = NaturalKeyOrPKMultipleChoiceFilter(
        queryset=Device.objects.all(),
        method="filter_device",
        label="Devices (name or ID), through Policies assigned directly or by Dynamic Group",
    )

    def filter_device(self, queryset, name, value):  # pylint: disable=unused-argument
        """Return the rules of every Policy assigned to the Devices, directly or through a Dynamic Group."""
        if not value:
            return queryset
        assigned = Q()
        for device in value:
            assigned |= Q(policies__assigned_devices=device)
            assigned |= Q(policies__assigned_dynamic_groups__in=device.dynamic_groups)
        return queryset.filter(pk__in=models.PolicyRule.objects.filter(assigned).values("pk"))

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


###########################
# Through Models
###########################


class PolicyDeviceM2MFilterSet(NautobotFilterSet):
    """Filter for PolicyDeviceM2M."""

    class Meta:
        """Meta attributes for filter."""

        model = models.PolicyDeviceM2M
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class PolicyDynamicGroupM2MFilterSet(NautobotFilterSet):
    """Filter for PolicyDynamicGroupM2M."""

    class Meta:
        """Meta attributes for filter."""

        model = models.PolicyDynamicGroupM2M
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class NATPolicyDeviceM2MFilterSet(NautobotFilterSet):
    """Filter for NATPolicyDeviceM2M."""

    class Meta:
        """Meta attributes for filter."""

        model = models.NATPolicyDeviceM2M
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]


class NATPolicyDynamicGroupM2MFilterSet(NautobotFilterSet):
    """Filter for NATPolicyDynamicGroupM2M."""

    class Meta:
        """Meta attributes for filter."""

        model = models.NATPolicyDynamicGroupM2M
        fields = [i.name for i in model._meta.get_fields() if not isinstance(i, GenericRelation)]
