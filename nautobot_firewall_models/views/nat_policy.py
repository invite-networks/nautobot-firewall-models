"""NAT Rule Object Viewsets."""

from nautobot.apps.views import NautobotUIViewSet

from nautobot_firewall_models import details, filters, forms, models, tables
from nautobot_firewall_models.api import serializers


class NATPolicyRuleUIViewSet(NautobotUIViewSet):
    """ViewSet for the NATPolicyRule model."""

    bulk_update_form_class = forms.NATPolicyRuleBulkEditForm
    filterset_class = filters.NATPolicyRuleFilterSet
    filterset_form_class = forms.NATPolicyRuleFilterForm
    form_class = forms.NATPolicyRuleForm
    queryset = models.NATPolicyRule.objects.all()
    serializer_class = serializers.NATPolicyRuleSerializer
    table_class = tables.NATPolicyRuleTable
    object_detail_content = details.nat_policy_rule

    lookup_field = "pk"


class NATPolicyUIViewSet(NautobotUIViewSet):
    """ViewSet for the NATPolicy model."""

    bulk_update_form_class = forms.NATPolicyBulkEditForm
    filterset_class = filters.NATPolicyFilterSet
    filterset_form_class = forms.NATPolicyFilterForm
    form_class = forms.NATPolicyForm
    queryset = models.NATPolicy.objects.all()
    serializer_class = serializers.NATPolicySerializer
    table_class = tables.NATPolicyTable
    object_detail_content = details.nat_policy
    prefetch_related = [
        "nat_policy_rules__source_users",
        "nat_policy_rules__source_user_groups",
        "nat_policy_rules__source_zones",
        "nat_policy_rules__source_zone_groups",
        "nat_policy_rules__destination_zones",
        "nat_policy_rules__destination_zone_groups",
        "nat_policy_rules__original_source_addresses",
        "nat_policy_rules__original_source_address_groups",
        "nat_policy_rules__original_source_services",
        "nat_policy_rules__original_source_service_groups",
        "nat_policy_rules__translated_source_addresses",
        "nat_policy_rules__translated_source_address_groups",
        "nat_policy_rules__translated_source_services",
        "nat_policy_rules__translated_source_service_groups",
        "nat_policy_rules__original_destination_addresses",
        "nat_policy_rules__original_destination_address_groups",
        "nat_policy_rules__original_destination_services",
        "nat_policy_rules__original_destination_service_groups",
        "nat_policy_rules__translated_destination_addresses",
        "nat_policy_rules__translated_destination_address_groups",
        "nat_policy_rules__translated_destination_services",
        "nat_policy_rules__translated_destination_service_groups",
    ]

    lookup_field = "pk"
