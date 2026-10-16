"""Load models."""

from .address import (
    FQDN,
    AddressObject,
    AddressObjectGroup,
)
from .appliance import Firewall, FirewallGroup, HAGroup
from .nat_policy import (
    NATPolicy,
    NATPolicyRule,
)
from .security_policy import (
    Policy,
    PolicyBand,
    PolicyRule,
)
from .service import (
    ApplicationObject,
    ApplicationObjectGroup,
    ServiceObject,
    ServiceObjectGroup,
)
from .user import UserObject, UserObjectGroup
from .zone import Zone, ZoneGroup

__all__ = (
    "AddressObject",
    "AddressObjectGroup",
    "ApplicationObject",
    "ApplicationObjectGroup",
    "FQDN",
    "Firewall",
    "FirewallGroup",
    "HAGroup",
    "NATPolicy",
    "NATPolicyRule",
    "Policy",
    "PolicyBand",
    "PolicyRule",
    "ServiceObject",
    "ServiceObjectGroup",
    "UserObject",
    "UserObjectGroup",
    "Zone",
    "ZoneGroup",
)
