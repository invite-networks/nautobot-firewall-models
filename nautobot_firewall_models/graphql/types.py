"""GraphQL types for nautobot_firewall_models.

PolicyRule and NATPolicyRule get custom types so they can expose their zones with every ZoneGroup expanded.
"""

import graphene
from nautobot.apps.graphql import OptimizedNautobotObjectType

from nautobot_firewall_models import filters, models


class ZoneType(OptimizedNautobotObjectType):
    """GraphQL type for Zone."""

    class Meta:
        """Meta attributes."""

        model = models.Zone
        filterset_class = filters.ZoneFilterSet


class ExpandedZonesMixin:
    """Expose a rule's zones after its ZoneGroups are expanded into their member Zones."""

    expanded_source_zones = graphene.List(ZoneType)
    expanded_destination_zones = graphene.List(ZoneType)

    @staticmethod
    def resolve_expanded_source_zones(root, _info):
        """Resolve the expanded source zones."""
        return root.expanded_source_zones()

    @staticmethod
    def resolve_expanded_destination_zones(root, _info):
        """Resolve the expanded destination zones."""
        return root.expanded_destination_zones()


class PolicyRuleType(ExpandedZonesMixin, OptimizedNautobotObjectType):
    """GraphQL type for PolicyRule."""

    class Meta:
        """Meta attributes."""

        model = models.PolicyRule
        filterset_class = filters.PolicyRuleFilterSet


class NATPolicyRuleType(ExpandedZonesMixin, OptimizedNautobotObjectType):
    """GraphQL type for NATPolicyRule."""

    class Meta:
        """Meta attributes."""

        model = models.NATPolicyRule
        filterset_class = filters.NATPolicyRuleFilterSet


graphql_types = [ZoneType, PolicyRuleType, NATPolicyRuleType]
