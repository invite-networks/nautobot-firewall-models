"""GraphQL types for nautobot_firewall_models.

PolicyRule and NATPolicyRule get custom types so they can expose their zones with every ZoneGroup expanded, and
PolicyRule its addresses as rendered, with every flattened Address Object Group replaced by its members.
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


class AddressObjectType(OptimizedNautobotObjectType):
    """GraphQL type for AddressObject."""

    class Meta:
        """Meta attributes."""

        model = models.AddressObject
        filterset_class = filters.AddressObjectFilterSet


class AddressObjectGroupType(OptimizedNautobotObjectType):
    """GraphQL type for AddressObjectGroup."""

    class Meta:
        """Meta attributes."""

        model = models.AddressObjectGroup
        filterset_class = filters.AddressObjectGroupFilterSet


class RenderedAddressesMixin:
    """Expose a rule's addresses as rendered: each flattened Address Object Group replaced by its members."""

    rendered_source_addresses = graphene.List(AddressObjectType)
    rendered_source_address_groups = graphene.List(AddressObjectGroupType)
    rendered_destination_addresses = graphene.List(AddressObjectType)
    rendered_destination_address_groups = graphene.List(AddressObjectGroupType)

    @staticmethod
    def resolve_rendered_source_addresses(root, _info):
        """Resolve the rendered source addresses."""
        return root.rendered_source_addresses()

    @staticmethod
    def resolve_rendered_source_address_groups(root, _info):
        """Resolve the rendered source address groups."""
        return root.rendered_source_address_groups()

    @staticmethod
    def resolve_rendered_destination_addresses(root, _info):
        """Resolve the rendered destination addresses."""
        return root.rendered_destination_addresses()

    @staticmethod
    def resolve_rendered_destination_address_groups(root, _info):
        """Resolve the rendered destination address groups."""
        return root.rendered_destination_address_groups()


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


class PolicyRuleType(ExpandedZonesMixin, RenderedAddressesMixin, OptimizedNautobotObjectType):
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


graphql_types = [ZoneType, AddressObjectType, AddressObjectGroupType, PolicyRuleType, NATPolicyRuleType]
