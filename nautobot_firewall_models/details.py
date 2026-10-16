"""Object Detail components for golden config."""

from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from nautobot.apps import ui
from nautobot.core.templatetags import helpers

from nautobot_firewall_models import tables


class BaseFieldsPanelMixin:
    """Mixin to render a <ul> HTML list of a given url with hyperlinks, or a placeholder if none exist based on the key `key_and_reverse_url_string`."""

    def render_value(self, key, value, instance):
        """Renders a <ul> HTML list of a given url with hyperlinks, or a placeholder if none exist."""

        def _is_empty_field(val):
            if val is None:
                return True
            if isinstance(val, str) and val.strip() == "":
                return True
            try:
                if hasattr(val, "exists") and callable(val.exists):
                    return not val.exists()
            except (ObjectDoesNotExist, FieldError, TypeError, AttributeError):
                return False
            if hasattr(val, "__len__") and len(val) == 0:
                return True
            return False

        if self.key_and_reverse_url_string.get(key):
            # Defer callable check until after empty check (to catch empty ManyRelatedManager before .value())
            if _is_empty_field(value):
                return helpers.placeholder(None)

            # Now it's safe to call, and intended for dynamic/resolved values
            if callable(value) and not isinstance(value, models.Manager):
                value = value()
            full_listing_link = reverse(self.key_and_reverse_url_string[key])

            return helpers.render_m2m(
                value.all(),
                full_listing_link=full_listing_link,
                verbose_name_plural=key,
            )
        return super().render_value(key, value, instance)


class AddressObjectGroupFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for AddressObjectGroup."""

    key_and_reverse_url_string = {
        "address_object_groups": "plugins:nautobot_firewall_models:addressobjectgroup_list",
        "parent_groups": "plugins:nautobot_firewall_models:addressobjectgroup_list",
    }


class MissingFinalRulePanel(ui.Panel):
    """Warn on a Trust Band's page when the band has no Final rule. The check is reported, never enforced."""

    def should_render(self, context):
        """Only render for a Trust Band that is missing its Final rule."""
        return super().should_render(context) and context["object"].missing_final_rule


class ServiceObjectGroupFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for ServiceObjectGroup."""

    key_and_reverse_url_string = {"service_objects": "plugins:nautobot_firewall_models:serviceobject_list"}


class FQDNFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for FQDN."""

    key_and_reverse_url_string = {"ip_addresses": "ipam:ipaddress_list"}


ASSIGNED_TO_LABELS = {
    "assigned_firewalls__all": "Firewalls",
    "assigned_ha_groups__all": "HA Groups",
    "assigned_firewall_groups__all": "Firewall Groups",
}


class FirewallFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for Firewall."""

    key_and_reverse_url_string = {"firewall_groups": "plugins:nautobot_firewall_models:firewallgroup_list"}


class HAGroupFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for HAGroup."""

    key_and_reverse_url_string = {
        "firewalls": "plugins:nautobot_firewall_models:firewall_list",
        "firewall_groups": "plugins:nautobot_firewall_models:firewallgroup_list",
    }


class FirewallGroupFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for FirewallGroup."""

    key_and_reverse_url_string = {
        "firewalls": "plugins:nautobot_firewall_models:firewall_list",
        "ha_groups": "plugins:nautobot_firewall_models:hagroup_list",
    }


class NATPolicyFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for NATPolicy."""

    key_and_reverse_url_string = {
        "assigned_firewalls__all": "plugins:nautobot_firewall_models:firewall_list",
        "assigned_ha_groups__all": "plugins:nautobot_firewall_models:hagroup_list",
        "assigned_firewall_groups__all": "plugins:nautobot_firewall_models:firewallgroup_list",
    }


class NATPolicyRuleFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for NATPolicyRule."""

    key_and_reverse_url_string = {"nat_policies__all": "plugins:nautobot_firewall_models:natpolicyrule_list"}


class PolicyFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for Policy."""

    key_and_reverse_url_string = {
        "assigned_firewalls__all": "plugins:nautobot_firewall_models:firewall_list",
        "assigned_ha_groups__all": "plugins:nautobot_firewall_models:hagroup_list",
        "assigned_firewall_groups__all": "plugins:nautobot_firewall_models:firewallgroup_list",
    }


class PolicyRuleFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for PolicyRule."""

    key_and_reverse_url_string = {"policies__all": "plugins:nautobot_firewall_models:policyrule_list"}


class UserObjectGroupFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for UserObjectGroup."""

    key_and_reverse_url_string = {"user_objects": "plugins:nautobot_firewall_models:userobject_list"}


class ZoneFieldsPanel(BaseFieldsPanelMixin, ui.ObjectFieldsPanel):
    """Set `key_and_reverse_url_string` for Zone."""

    key_and_reverse_url_string = {
        "vrfs": "ipam:vrf_list",
        "firewalls": "plugins:nautobot_firewall_models:firewall_list",
        "ha_groups": "plugins:nautobot_firewall_models:hagroup_list",
        "firewall_groups": "plugins:nautobot_firewall_models:firewallgroup_list",
    }


address_object = ui.ObjectDetailContent(
    panels=(
        ui.ObjectFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields="__all__",
        ),
    ),
)

address_object_group = ui.ObjectDetailContent(
    panels=(
        AddressObjectGroupFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            # Replace with `__all__` once order is fixed
            fields=["name", "description", "address_object_groups", "parent_groups", "flatten", "status"],
            key_transforms={"address_object_groups": "Nested Groups", "parent_groups": "Member Of"},
        ),
        ui.ObjectsTablePanel(
            weight=100,
            section=ui.SectionChoices.FULL_WIDTH,
            table_class=tables.AddressObjectTable,
            table_filter="address_object_groups",
            related_field_name="address_object_groups",
            add_button_route=None,
        ),
    ),
)

application_object = ui.ObjectDetailContent(
    panels=(
        ui.ObjectFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            # Replace with `__all__` once order is fixed
            fields=[
                "name",
                "description",
                "category",
                "subcategory",
                "technology",
                "risk",
                "default_ip_protocol",
                "default_type",
            ],
        ),
    ),
)


application_object_group = ui.ObjectDetailContent(
    panels=(
        ui.ObjectFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            # Replace with `__all__` once order is fixed
            fields=["name", "description", "status"],
        ),
        ui.ObjectsTablePanel(
            weight=100,
            section=ui.SectionChoices.FULL_WIDTH,
            table_class=tables.ApplicationObjectTable,
            table_filter="application_object_groups",
            related_field_name="application_object_groups",
            add_button_route=None,
        ),
    ),
)

fqdn = ui.ObjectDetailContent(
    panels=(
        FQDNFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            # Replace with `__all__` once order is fixed, needs additional_fields=["ip_addresses"]
            fields=["name", "description", "ip_addresses", "status"],
        ),
    ),
)


nat_policy = ui.ObjectDetailContent(
    panels=(
        NATPolicyFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=[
                "name",
                "description",
                "assigned_firewalls__all",
                "assigned_ha_groups__all",
                "assigned_firewall_groups__all",
                "tenant",
                "status",
            ],
            key_transforms=ASSIGNED_TO_LABELS,
        ),
    ),
    extra_tabs=(
        ui.Tab(
            weight=ui.Tab.WEIGHT_CHANGELOG_TAB + 200,
            tab_id="nat-policy-rules",
            label="NAT Policy Rules",
            panels=(
                ui.Panel(
                    section=ui.SectionChoices.FULL_WIDTH,
                    weight=100,
                    template_path="nautobot_firewall_models/inc/nat_policy_expanded_rules.html",
                ),
            ),
        ),
    ),
)

nat_policy_rule = ui.ObjectDetailContent(
    panels=(
        NATPolicyRuleFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            # Replace with `__all__` once order is fixed, needs additional_fields=["ip_addresses"]
            fields=["description", "nat_policies__all", "status"],
            key_transforms={"nat_policies__all": "Assigned Policies"},
        ),
        ui.Panel(
            section=ui.SectionChoices.FULL_WIDTH,
            weight=100,
            template_path="nautobot_firewall_models/inc/nat_policy_expanded_rules.html",
        ),
    ),
)

policy = ui.ObjectDetailContent(
    panels=(
        PolicyFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=[
                "name",
                "rule_type",
                "description",
                "assigned_firewalls__all",
                "assigned_ha_groups__all",
                "assigned_firewall_groups__all",
                "tenant",
                "status",
            ],
            key_transforms=ASSIGNED_TO_LABELS,
        ),
    ),
    extra_tabs=(
        ui.Tab(
            weight=ui.Tab.WEIGHT_CHANGELOG_TAB + 200,
            tab_id="policy-rules",
            label="Policy Rules",
            panels=(
                ui.Panel(
                    section=ui.SectionChoices.FULL_WIDTH,
                    weight=100,
                    template_path="nautobot_firewall_models/inc/policy_expanded_rules.html",
                ),
            ),
        ),
    ),
)

policy_band = ui.ObjectDetailContent(
    panels=(
        MissingFinalRulePanel(
            section=ui.SectionChoices.FULL_WIDTH,
            weight=50,
            label="Trust Band check",
            template_path="nautobot_firewall_models/inc/policy_band_missing_final_rule.html",
        ),
        ui.ObjectFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=["name", "index", "trust_band", "description"],
        ),
        ui.ObjectsTablePanel(
            weight=100,
            section=ui.SectionChoices.FULL_WIDTH,
            table_class=tables.PolicyRuleTable,
            table_filter="band",
            related_field_name="band",
            exclude_columns=["band"],
        ),
    ),
)

policy_rule = ui.ObjectDetailContent(
    panels=(
        PolicyRuleFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            # Replace with `__all__` once order is fixed, needs additional_fields=["ip_addresses"]
            fields=[
                "rule_type",
                "panos_rule_type",
                "band",
                "position",
                "chain",
                "index",
                "negate_source",
                "negate_destination",
                "description",
                "policies__all",
                "status",
            ],
            key_transforms={"policies__all": "Assigned Policies"},
        ),
        ui.Panel(
            section=ui.SectionChoices.FULL_WIDTH,
            weight=100,
            template_path="nautobot_firewall_models/inc/policy_expanded_rules.html",
        ),
    ),
)

service_object = ui.ObjectDetailContent(
    panels=(
        ui.ObjectFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields="__all__",
        ),
    ),
)


service_object_group = ui.ObjectDetailContent(
    panels=(
        ServiceObjectGroupFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            # Replace with `__all__` once order is fixed
            fields=["name", "description", "service_objects", "status"],
        ),
    ),
)

user_object = ui.ObjectDetailContent(
    panels=(
        ui.ObjectFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields="__all__",
        ),
    ),
)

user_object_group = ui.ObjectDetailContent(
    panels=(
        UserObjectGroupFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=["name", "description", "user_objects", "status"],
        ),
    ),
)

zone = ui.ObjectDetailContent(
    panels=(
        ZoneFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=["name", "zone_group", "description", "vrfs", "firewalls", "ha_groups", "firewall_groups", "status"],
        ),
    ),
)

zone_group = ui.ObjectDetailContent(
    panels=(
        ui.ObjectFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=["name", "description", "status"],
        ),
        ui.ObjectsTablePanel(
            weight=100,
            section=ui.SectionChoices.FULL_WIDTH,
            table_class=tables.ZoneTable,
            table_filter="zone_group",
            related_field_name="zone_group",
            exclude_columns=["zone_group"],
        ),
    ),
)

# Shown on a Firewall, HA Group or Firewall Group: the Policies and NAT Policies that reach it.
assigned_policies_panel = ui.Panel(
    section=ui.SectionChoices.RIGHT_HALF,
    weight=100,
    label="Assigned Policies",
    template_path="nautobot_firewall_models/inc/appliance_policies.html",
)

firewall = ui.ObjectDetailContent(
    panels=(
        FirewallFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=["name", "description", "device", "virtual_machine", "ha_group", "firewall_groups", "status"],
        ),
        assigned_policies_panel,
    ),
)

ha_group = ui.ObjectDetailContent(
    panels=(
        HAGroupFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=["name", "description", "management_address", "firewalls", "firewall_groups", "status"],
        ),
        assigned_policies_panel,
    ),
)

firewall_group = ui.ObjectDetailContent(
    panels=(
        FirewallGroupFieldsPanel(
            section=ui.SectionChoices.LEFT_HALF,
            weight=100,
            fields=["name", "description", "firewalls", "ha_groups", "status"],
            key_transforms={"ha_groups": "HA Groups"},
        ),
        assigned_policies_panel,
    ),
)
