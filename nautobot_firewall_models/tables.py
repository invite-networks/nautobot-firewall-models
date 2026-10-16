"""Table Views for Firewall Models."""

import django_tables2 as tables
from nautobot.apps.tables import BaseTable, ButtonsColumn, ToggleColumn
from nautobot.extras.tables import StatusTableMixin

from nautobot_firewall_models import models


class FQDNTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.FQDN, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.FQDN
        fields = ("pk", "name", "description", "ip_addresses", "status")


class AddressObjectTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    actions = ButtonsColumn(models.AddressObject, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.AddressObject
        fields = (
            "pk",
            "name",
            "description",
            "ip_address",
            "prefix",
            "fqdn",
            "device",
            "dynamic",
            "status",
        )


class AddressObjectGroupTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.AddressObjectGroup, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.AddressObjectGroup
        fields = ("pk", "name", "description", "address_objects", "address_object_groups", "flatten", "status")


class ApplicationObjectTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.ApplicationObject, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.ApplicationObject
        fields = ("pk", "name", "description", "category", "subcategory", "technology", "risk", "default_type")


class ApplicationObjectGroupTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    application_objects = tables.ManyToManyColumn(linkify_item=True)
    actions = ButtonsColumn(models.ApplicationObjectGroup, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.ApplicationObjectGroup
        fields = ("pk", "name", "description", "application_objects")


class ServiceObjectTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.ServiceObject, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.ServiceObject
        fields = ("pk", "name", "port", "ip_protocol", "description", "status")


class ServiceObjectGroupTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.ServiceObjectGroup, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.ServiceObjectGroup
        fields = ("pk", "name", "description", "service_objects", "status")


class UserObjectTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    username = tables.Column(linkify=True)
    actions = ButtonsColumn(models.UserObject, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.UserObject
        fields = ("pk", "username", "name", "status")


class UserObjectGroupTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.UserObjectGroup, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.UserObjectGroup
        fields = ("pk", "name", "description", "user_objects", "status")


class ZoneTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    zone_group = tables.Column(linkify=True)
    actions = ButtonsColumn(models.Zone, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.Zone
        fields = (
            "pk",
            "name",
            "zone_group",
            "vrfs",
            "firewalls",
            "ha_groups",
            "firewall_groups",
            "description",
            "status",
        )


class ZoneGroupTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    zones = tables.ManyToManyColumn(linkify_item=True)
    actions = ButtonsColumn(models.ZoneGroup, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.ZoneGroup
        fields = ("pk", "name", "zones", "description", "status")


class PolicyBandTable(BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    policy_rule_count = tables.Column(verbose_name="Policy Rules")
    final_rule = tables.TemplateColumn(
        template_name="nautobot_firewall_models/inc/policy_band_final_rule_column.html",
        verbose_name="Final Rule",
        orderable=False,
    )
    actions = ButtonsColumn(models.PolicyBand, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.PolicyBand
        fields = ("pk", "index", "name", "trust_band", "final_rule", "description", "policy_rule_count", "actions")


# TODO: refactor
class PolicyRuleTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    band = tables.Column(linkify=True)
    actions = ButtonsColumn(models.PolicyRule, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.PolicyRule
        fields = (
            # pylint: disable=duplicate-code
            "pk",
            "rule_type",
            "panos_rule_type",
            "band",
            "position",
            "chain",
            "index",
            "name",
            "source_users",
            "source_user_groups",
            "source_addresses",
            "source_address_groups",
            "negate_source",
            "source_zones",
            "source_zone_groups",
            "source_services",
            "source_service_groups",
            "destination_addresses",
            "destination_address_groups",
            "negate_destination",
            "destination_zones",
            "destination_zone_groups",
            "destination_services",
            "destination_service_groups",
            "applications",
            "application_groups",
            "action",
            "description",
            "request_id",
            "log_start",
            "log_end",
            "status",
            "actions",
        )
        default_columns = (
            "pk",
            "rule_type",
            "panos_rule_type",
            "band",
            "position",
            "chain",
            "index",
            "name",
            "source_users",
            "source_user_groups",
            "source_addresses",
            "source_address_groups",
            "negate_source",
            "source_zones",
            "source_zone_groups",
            "source_services",
            "source_service_groups",
            "destination_addresses",
            "destination_address_groups",
            "negate_destination",
            "destination_zones",
            "destination_zone_groups",
            "destination_services",
            "destination_service_groups",
            "applications",
            "application_groups",
            "action",
            "log_start",
            "log_end",
            "status",
            "actions",
        )


class PolicyTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    actions = ButtonsColumn(models.Policy, buttons=("edit", "delete"))
    assigned_firewalls = tables.ManyToManyColumn(linkify_item=True, verbose_name="Firewalls")
    assigned_ha_groups = tables.ManyToManyColumn(linkify_item=True, verbose_name="HA Groups")
    assigned_firewall_groups = tables.ManyToManyColumn(linkify_item=True, verbose_name="Firewall Groups")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.Policy
        fields = (
            "pk",
            "name",
            "rule_type",
            "description",
            "policy_rules",
            "assigned_firewalls",
            "assigned_ha_groups",
            "assigned_firewall_groups",
            "status",
        )


# TODO: refactor
class NATPolicyRuleTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.LinkColumn()
    actions = ButtonsColumn(models.NATPolicyRule, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.NATPolicyRule
        fields = (
            # pylint: disable=duplicate-code
            "pk",
            "name",
            "source_zones",
            "source_zone_groups",
            "destination_zones",
            "destination_zone_groups",
            "original_source_addresses",
            "original_source_address_groups",
            "original_source_services",
            "original_source_service_groups",
            "translated_source_addresses",
            "translated_source_address_groups",
            "translated_source_services",
            "translated_source_service_groups",
            "original_destination_addresses",
            "original_destination_address_groups",
            "original_destination_services",
            "original_destination_service_groups",
            "translated_destination_addresses",
            "translated_destination_address_groups",
            "translated_destination_services",
            "translated_destination_service_groups",
            "remark",
            "request_id",
            "description",
            "log",
            "status",
            "actions",
        )
        default_columns = (
            # pylint: disable=duplicate-code
            "pk",
            "name",
            "source_zones",
            "source_zone_groups",
            "destination_zones",
            "destination_zone_groups",
            "original_source_addresses",
            "original_source_address_groups",
            "translated_source_addresses",
            "translated_source_address_groups",
            "original_destination_addresses",
            "original_destination_address_groups",
            "original_destination_services",
            "original_destination_service_groups",
            "translated_destination_addresses",
            "translated_destination_address_groups",
            "translated_destination_services",
            "translated_destination_service_groups",
            "remark",
            "log",
            "status",
            "actions",
        )


class NATPolicyTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    nat_policy_rules = tables.ManyToManyColumn(verbose_name="NAT policy rules", linkify_item=True)
    actions = ButtonsColumn(models.NATPolicy, buttons=("edit", "delete"))
    assigned_firewalls = tables.ManyToManyColumn(linkify_item=True, verbose_name="Firewalls")
    assigned_ha_groups = tables.ManyToManyColumn(linkify_item=True, verbose_name="HA Groups")
    assigned_firewall_groups = tables.ManyToManyColumn(linkify_item=True, verbose_name="Firewall Groups")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.NATPolicy
        fields = (
            "pk",
            "name",
            "description",
            "nat_policy_rules",
            "assigned_firewalls",
            "assigned_ha_groups",
            "assigned_firewall_groups",
            "status",
        )


class FirewallTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    virtual_machine = tables.Column(linkify=True)
    ha_group = tables.Column(linkify=True)
    firewall_groups = tables.ManyToManyColumn(linkify_item=True)
    actions = ButtonsColumn(models.Firewall, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.Firewall
        fields = ("pk", "name", "device", "virtual_machine", "ha_group", "firewall_groups", "description", "status")


class HAGroupTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    management_address = tables.Column(linkify=True)
    firewalls = tables.ManyToManyColumn(linkify_item=True)
    actions = ButtonsColumn(models.HAGroup, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.HAGroup
        fields = ("pk", "name", "management_address", "firewalls", "description", "status")


class FirewallGroupTable(StatusTableMixin, BaseTable):
    """Table for list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    firewalls = tables.ManyToManyColumn(linkify_item=True)
    ha_groups = tables.ManyToManyColumn(linkify_item=True, verbose_name="HA Groups")
    actions = ButtonsColumn(models.FirewallGroup, buttons=("edit", "delete"))

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.FirewallGroup
        fields = ("pk", "name", "firewalls", "ha_groups", "description", "status")
