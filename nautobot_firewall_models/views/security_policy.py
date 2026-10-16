"""Rule Object Viewsets."""

from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from nautobot.apps.views import NautobotUIViewSet

from nautobot_firewall_models import choices, details, filters, forms, models, tables
from nautobot_firewall_models.api import serializers


class PolicyBandUIViewSet(NautobotUIViewSet):
    """ViewSet for the PolicyBand model."""

    bulk_update_form_class = forms.PolicyBandBulkEditForm
    filterset_class = filters.PolicyBandFilterSet
    filterset_form_class = forms.PolicyBandFilterForm
    form_class = forms.PolicyBandForm
    queryset = models.PolicyBand.objects.annotate(policy_rule_count=Count("policy_rules"))
    serializer_class = serializers.PolicyBandSerializer
    table_class = tables.PolicyBandTable
    object_detail_content = details.policy_band

    lookup_field = "pk"


class PolicyRuleUIViewSet(NautobotUIViewSet):
    """ViewSet for the PolicyRule model."""

    bulk_update_form_class = forms.PolicyRuleBulkEditForm
    filterset_class = filters.PolicyRuleFilterSet
    filterset_form_class = forms.PolicyRuleFilterForm
    form_class = forms.PolicyRuleForm
    queryset = models.PolicyRule.objects.all().select_related("band")
    serializer_class = serializers.PolicyRuleSerializer
    table_class = tables.PolicyRuleTable
    object_detail_content = details.policy_rule

    lookup_field = "pk"

    def create(self, request, *args, **kwargs):
        """Ask for the rule type first, since it decides which fields the form shows."""
        rule_types = dict(choices.RULE_TYPE_CHOICES)
        if request.method == "GET" and request.GET.get("rule_type") not in rule_types:
            options = []
            for value, label in choices.RULE_TYPE_CHOICES:
                query = request.GET.copy()
                query["rule_type"] = value
                options.append({"label": label, "url": f"{request.path}?{query.urlencode()}"})
            return render(
                request,
                "nautobot_firewall_models/policyrule_choose_type.html",
                {"options": options, "return_url": self._safe_return_url(request)},
            )
        return super().create(request, *args, **kwargs)

    @staticmethod
    def _safe_return_url(request):
        """Return the requested return_url when it points at this site, otherwise the rule list."""
        return_url = request.GET.get("return_url")
        if return_url and url_has_allowed_host_and_scheme(return_url, allowed_hosts={request.get_host()}):
            return return_url
        return reverse("plugins:nautobot_firewall_models:policyrule_list")


class PolicyUIViewSet(NautobotUIViewSet):
    """ViewSet for the Policy model."""

    bulk_update_form_class = forms.PolicyBulkEditForm
    filterset_class = filters.PolicyFilterSet
    filterset_form_class = forms.PolicyFilterForm
    form_class = forms.PolicyForm
    queryset = models.Policy.objects.all()
    serializer_class = serializers.PolicySerializer
    table_class = tables.PolicyTable
    object_detail_content = details.policy
    prefetch_related = [
        "policy_rules__source_users",
        "policy_rules__source_user_groups",
        "policy_rules__source_zones",
        "policy_rules__source_zone_groups",
        "policy_rules__destination_zones",
        "policy_rules__destination_zone_groups",
        "policy_rules__original_source_addresses",
        "policy_rules__original_source_address_groups",
        "policy_rules__original_source_services",
        "policy_rules__original_source_service_groups",
        "policy_rules__translated_source_addresses",
        "policy_rules__translated_source_address_groups",
        "policy_rules__translated_source_services",
        "policy_rules__translated_source_service_groups",
        "policy_rules__original_destination_addresses",
        "policy_rules__original_destination_address_groups",
        "policy_rules__original_destination_services",
        "policy_rules__original_destination_service_groups",
        "policy_rules__translated_destination_addresses",
        "policy_rules__translated_destination_address_groups",
        "policy_rules__translated_destination_services",
        "policy_rules__translated_destination_service_groups",
    ]

    lookup_field = "pk"
