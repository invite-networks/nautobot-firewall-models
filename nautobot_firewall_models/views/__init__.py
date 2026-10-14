"""UI Viewsets."""

from nautobot_firewall_models.views.address import (
    AddressObjectGroupUIViewSet,
    AddressObjectUIViewSet,
    FQDNUIViewSet,
)
from nautobot_firewall_models.views.nat_policy import NATPolicyRuleUIViewSet, NATPolicyUIViewSet
from nautobot_firewall_models.views.security_policy import (
    PolicyBandUIViewSet,
    PolicyRuleUIViewSet,
    PolicyUIViewSet,
)
from nautobot_firewall_models.views.service import (
    ApplicationObjectGroupUIViewSet,
    ApplicationObjectUIViewSet,
    ServiceObjectGroupUIViewSet,
    ServiceObjectUIViewSet,
)
from nautobot_firewall_models.views.user import UserObjectGroupUIViewSet, UserObjectUIViewSet
from nautobot_firewall_models.views.zone import ZoneGroupUIViewSet, ZoneUIViewSet

__all__ = (
    "AddressObjectUIViewSet",
    "AddressObjectGroupUIViewSet",
    "ApplicationObjectUIViewSet",
    "ApplicationObjectGroupUIViewSet",
    "FQDNUIViewSet",
    "NATPolicyRuleUIViewSet",
    "NATPolicyUIViewSet",
    "PolicyUIViewSet",
    "PolicyBandUIViewSet",
    "PolicyRuleUIViewSet",
    "ServiceObjectUIViewSet",
    "ServiceObjectGroupUIViewSet",
    "UserObjectUIViewSet",
    "UserObjectGroupUIViewSet",
    "ZoneUIViewSet",
    "ZoneGroupUIViewSet",
)
