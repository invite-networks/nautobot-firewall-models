"""Appliance Viewsets."""

from nautobot.apps.views import NautobotUIViewSet

from nautobot_firewall_models import details, filters, forms, models, tables
from nautobot_firewall_models.api import serializers


class FirewallUIViewSet(NautobotUIViewSet):
    """ViewSet for the Firewall model."""

    bulk_update_form_class = forms.FirewallBulkEditForm
    filterset_class = filters.FirewallFilterSet
    filterset_form_class = forms.FirewallFilterForm
    form_class = forms.FirewallForm
    queryset = models.Firewall.objects.all().select_related("device", "virtual_machine", "ha_group")
    serializer_class = serializers.FirewallSerializer
    table_class = tables.FirewallTable
    object_detail_content = details.firewall

    lookup_field = "pk"


class HAGroupUIViewSet(NautobotUIViewSet):
    """ViewSet for the HAGroup model."""

    bulk_update_form_class = forms.HAGroupBulkEditForm
    filterset_class = filters.HAGroupFilterSet
    filterset_form_class = forms.HAGroupFilterForm
    form_class = forms.HAGroupForm
    queryset = models.HAGroup.objects.all().select_related("management_address")
    serializer_class = serializers.HAGroupSerializer
    table_class = tables.HAGroupTable
    object_detail_content = details.ha_group

    lookup_field = "pk"


class FirewallGroupUIViewSet(NautobotUIViewSet):
    """ViewSet for the FirewallGroup model."""

    bulk_update_form_class = forms.FirewallGroupBulkEditForm
    filterset_class = filters.FirewallGroupFilterSet
    filterset_form_class = forms.FirewallGroupFilterForm
    form_class = forms.FirewallGroupForm
    queryset = models.FirewallGroup.objects.all()
    serializer_class = serializers.FirewallGroupSerializer
    table_class = tables.FirewallGroupTable
    object_detail_content = details.firewall_group

    lookup_field = "pk"
