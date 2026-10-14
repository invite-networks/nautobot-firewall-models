"""Mixins shared by the firewall models."""

from django.core.exceptions import ValidationError

from nautobot_firewall_models.utils import is_managed_locally


class ManagedLocallyGroupMixin:
    """A group that, when Managed Locally, is defined on the firewall, so Nautobot holds its name and no members."""

    # Names of the many-to-many fields holding the group's members; set by each group model.
    members_fields = ()

    @classmethod
    def validate_managed_members(cls, status, members):
        """Refuse members on a Managed Locally group. `members` maps each member field to the members being set."""
        if not is_managed_locally(status):
            return
        if errors := {
            field: "A Managed Locally group is defined on the firewall, so it can not have members."
            for field, value in members.items()
            if value
        }:
            raise ValidationError(errors)
