"""Mixins shared by the firewall models."""

from django.core.exceptions import ValidationError

from nautobot_firewall_models.utils import is_managed_locally


class ManagedLocallyGroupMixin:
    """A group that, when Managed Locally, is defined on the firewall, so Nautobot holds its name and no members."""

    # Name of the many-to-many field holding the group's members; set by each group model.
    members_field = None

    @classmethod
    def validate_managed_members(cls, status, members):
        """Refuse members on a Managed Locally group."""
        if is_managed_locally(status) and members:
            raise ValidationError(
                {cls.members_field: "A Managed Locally group is defined on the firewall, so it can not have members."}
            )
