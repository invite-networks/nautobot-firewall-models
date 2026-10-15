"""Forms for nautobot_firewall_models."""
# pylint: disable=too-many-lines

from django import forms
from nautobot.apps.forms import (
    BulkEditNullBooleanSelect,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
    add_blank_choice,
)
from nautobot.dcim.models import Device
from nautobot.extras.forms import (
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
)
from nautobot.extras.models import DynamicGroup, Tag
from nautobot.ipam.models import VRF, IPAddress, Prefix
from nautobot.tenancy.forms import TenancyFilterForm, TenancyForm
from nautobot.tenancy.models import Tenant
from nautobot.virtualization.models import VirtualMachine

from nautobot_firewall_models import choices, fields, models


class FQDNFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.FQDN
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")


class FQDNForm(NautobotModelForm):
    """FQDN creation/edit form."""

    ip_addresses = DynamicModelMultipleChoiceField(queryset=IPAddress.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = models.FQDN
        fields = ["name", "description", "ip_addresses", "status", "tags"]


class FQDNBulkEditForm(NautobotBulkEditForm):
    """FQDN bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.FQDN.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    ip_addresses = DynamicModelMultipleChoiceField(queryset=IPAddress.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description", "ip_addresses"]


class AddressObjectFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.AddressObject
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    ip_address = DynamicModelChoiceField(queryset=IPAddress.objects.all(), required=False, label="IP Address")
    prefix = DynamicModelChoiceField(queryset=Prefix.objects.all(), required=False, label="Prefix")
    fqdn = DynamicModelChoiceField(queryset=models.FQDN.objects.all(), required=False, label="FQDN")
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
    dynamic = forms.ChoiceField(choices=add_blank_choice(choices.DYNAMIC_ADDRESS_CHOICES), required=False)


class AddressObjectForm(NautobotModelForm):
    """AddressObject creation/edit form."""

    ip_address = DynamicModelChoiceField(queryset=IPAddress.objects.all(), required=False, label="IP Address")
    prefix = DynamicModelChoiceField(queryset=Prefix.objects.all(), required=False, label="Prefix")
    fqdn = DynamicModelChoiceField(queryset=models.FQDN.objects.all(), required=False, label="FQDN")
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = models.AddressObject
        fields = [
            "name",
            "description",
            "fqdn",
            "ip_address",
            "prefix",
            "device",
            "dynamic",
            "status",
            "tags",
        ]


class AddressObjectBulkEditForm(NautobotBulkEditForm):
    """AddressObject bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.AddressObject.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description", "fqdn", "ip_address", "prefix", "device"]


class AddressObjectGroupFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.AddressObjectGroup
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")


class AddressObjectGroupForm(fields.ManagedLocallyGroupFormMixin, fields.ObjectOrGroupFormMixin, NautobotModelForm):  # pylint: disable=too-many-ancestors
    """AddressObjectGroup creation/edit form, with one picker for its Address Objects and nested groups."""

    address_objects = DynamicModelMultipleChoiceField(queryset=models.AddressObject.objects.all(), required=False)
    address_object_groups = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(), required=False
    )

    class Meta:
        """Meta attributes."""

        model = models.AddressObjectGroup
        fields = ["name", "description", "address_objects", "address_object_groups", "flatten", "status", "tags"]

    def __init__(self, *args, **kwargs):
        """Show one picker for Address Objects and nested Address Object Groups."""
        super().__init__(*args, **kwargs)
        self.combine_grouped_fields()

    def clean(self):
        """Refuse nested groups that would loop, and host relative members while a PAN-OS or NAT rule uses the group."""
        super().clean()
        self.instance.validate_members(
            self.cleaned_data.get("address_objects"), self.cleaned_data.get("address_object_groups")
        )
        return self.cleaned_data


class AddressObjectGroupBulkEditForm(NautobotBulkEditForm):
    """AddressObjectGroup bulk edit form."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False)
    flatten = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class ApplicationObjectFilterForm(NautobotFilterForm):  # pylint: disable=too-many-ancestors
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.ApplicationObject
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    category = DynamicModelChoiceField(
        queryset=models.ApplicationObject.objects.all(), required=False, label="Category"
    )


class ApplicationObjectForm(NautobotModelForm):
    """ApplicationObject creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.ApplicationObject
        fields = [
            # pylint: disable=duplicate-code
            "name",
            "description",
            "category",
            "subcategory",
            "technology",
            "risk",
            "default_type",
            "default_ip_protocol",
            "status",
        ]


class ApplicationObjectBulkEditForm(NautobotBulkEditForm):
    """ApplicationObject bulk edit form."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.ApplicationObject.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False)
    risk = forms.IntegerField(required=False)
    technology = forms.CharField(required=False)
    category = forms.CharField(required=False)
    subcategory = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
            "default_ip_protocol",
            "default_type",
            "technology",
            "category",
            "subcategory",
        ]


class ApplicationObjectGroupFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.ApplicationObjectGroup
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")


class ApplicationObjectGroupForm(fields.ManagedLocallyGroupFormMixin, NautobotModelForm):
    """ApplicationObjectGroup creation/edit form."""

    application_objects = DynamicModelMultipleChoiceField(queryset=models.ApplicationObject.objects.all())

    class Meta:
        """Meta attributes."""

        model = models.ApplicationObjectGroup
        fields = ["name", "description", "application_objects", "status", "tags"]


class ApplicationObjectGroupBulkEditForm(NautobotBulkEditForm):
    """ApplicationObjectGroup bulk edit form."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.ApplicationObjectGroup.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class ServiceObjectFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.ServiceObject
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    port = forms.IntegerField(required=False)
    ip_protocol = forms.ChoiceField(choices=add_blank_choice(choices.IP_PROTOCOL_CHOICES), required=False)


class ServiceObjectForm(NautobotModelForm):
    """ServiceObject creation/edit form."""

    port = forms.CharField(
        help_text="Must be a single integer representation of port OR single port range without spaces (e.g. 80 or 8080-8088)",
        required=False,
    )

    class Meta:
        """Meta attributes."""

        model = models.ServiceObject
        fields = ["name", "description", "port", "ip_protocol", "status", "tags"]


class ServiceObjectBulkEditForm(NautobotBulkEditForm):
    """ServiceObject bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.ServiceObject.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    port = forms.CharField(
        help_text="Must be a single integer representation of port OR single port range without spaces (e.g. 80 or 8080-8088)",
        required=False,
    )

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description", "port"]


class ServiceObjectGroupFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.ServiceObjectGroup
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")


class ServiceObjectGroupForm(fields.ManagedLocallyGroupFormMixin, NautobotModelForm):
    """ServiceObjectGroup creation/edit form."""

    service_objects = DynamicModelMultipleChoiceField(queryset=models.ServiceObject.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = models.ServiceObjectGroup
        fields = ["name", "description", "service_objects", "status", "tags"]


class ServiceObjectGroupBulkEditForm(NautobotBulkEditForm):
    """ServiceObjectGroup bulk edit form."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObjectGroup.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class UserObjectFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "username", "name"]

    model = models.UserObject
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    username = forms.CharField(required=False, label="Username")


class UserObjectForm(NautobotModelForm):
    """UserObject creation/edit form."""

    username = forms.CharField(label="Username")
    name = forms.CharField(
        label="Name",
        required=False,
    )

    class Meta:
        """Meta attributes."""

        model = models.UserObject
        fields = ["username", "name", "status", "tags"]


class UserObjectBulkEditForm(NautobotBulkEditForm):
    """UserObject bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.UserObject.objects.all(), widget=forms.MultipleHiddenInput)
    name = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "name",
        ]


class UserObjectGroupFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.UserObjectGroup
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")


class UserObjectGroupForm(fields.ManagedLocallyGroupFormMixin, NautobotModelForm):
    """UserObjectGroup creation/edit form."""

    user_objects = DynamicModelMultipleChoiceField(queryset=models.UserObject.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = models.UserObjectGroup
        fields = ["name", "description", "user_objects", "status", "tags"]


class UserObjectGroupBulkEditForm(NautobotBulkEditForm):
    """UserObjectGroup bulk edit form."""

    pk = DynamicModelMultipleChoiceField(
        queryset=models.UserObjectGroup.objects.all(), widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class ZoneFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.Zone
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    vrfs = DynamicModelChoiceField(queryset=VRF.objects.all(), label="VRF")
    devices = DynamicModelChoiceField(queryset=Device.objects.all(), label="Device")
    virtual_machines = DynamicModelChoiceField(queryset=VirtualMachine.objects.all(), label="Virtual Machine")


class ZoneForm(fields.ObjectOrGroupFormMixin, NautobotModelForm):
    """Zone creation/edit form, with one picker for the Devices and Virtual Machines the Zone is bound to."""

    vrfs = DynamicModelMultipleChoiceField(queryset=VRF.objects.all(), required=False, label="VRF")
    devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Devices")
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label="Virtual Machines"
    )

    class Meta:
        """Meta attributes."""

        model = models.Zone
        fields = ["name", "description", "vrfs", "devices", "virtual_machines", "status", "tags"]

    def __init__(self, *args, **kwargs):
        """Show one picker for Devices and Virtual Machines."""
        super().__init__(*args, **kwargs)
        self.combine_grouped_fields()


class ZoneBulkEditForm(NautobotBulkEditForm):
    """Zone bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.Zone.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    vrfs = DynamicModelMultipleChoiceField(queryset=VRF.objects.all(), required=False, label="VRF")
    devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Devices")
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label="Virtual Machines"
    )

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description", "vrfs", "devices", "virtual_machines"]


class ZoneGroupFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.ZoneGroup
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    zones = DynamicModelChoiceField(queryset=models.Zone.objects.all(), required=False, label="Zone")


class ZoneGroupForm(NautobotModelForm):
    """ZoneGroup creation/edit form."""

    zones = DynamicModelMultipleChoiceField(queryset=models.Zone.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = models.ZoneGroup
        fields = ["name", "description", "zones", "status", "tags"]


class ZoneGroupBulkEditForm(NautobotBulkEditForm):
    """ZoneGroup bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.ZoneGroup.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class PolicyBandFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.PolicyBand
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")


class PolicyBandForm(NautobotModelForm):
    """PolicyBand creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.PolicyBand
        fields = ["name", "index", "description", "tags"]


class PolicyBandBulkEditForm(NautobotBulkEditForm):
    """PolicyBand bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.PolicyBand.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description"]


class PolicyRuleFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name", "rule_type", "band", "position", "chain", "device"]

    model = models.PolicyRule
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    band = DynamicModelMultipleChoiceField(
        queryset=models.PolicyBand.objects.all(), to_field_name="name", required=False, label="Policy Band"
    )
    position = forms.MultipleChoiceField(choices=choices.POSITION_CHOICES, required=False)
    rule_type = forms.MultipleChoiceField(choices=choices.RULE_TYPE_CHOICES, required=False, label="Rule Type")
    chain = forms.MultipleChoiceField(choices=choices.CHAIN_CHOICES, required=False)
    device = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    tag = TagFilterField(models.PolicyRule)


class PolicyRuleForm(fields.ObjectOrGroupFormMixin, NautobotModelForm):
    """PolicyRule creation/edit form.

    The rule type is chosen before the form opens (see PolicyRuleUIViewSet.create) and is fixed afterwards, so the form
    only shows the fields that type can use.
    """

    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    rule_type = forms.ChoiceField(choices=choices.RULE_TYPE_CHOICES, widget=forms.HiddenInput, required=False)
    band = DynamicModelChoiceField(queryset=models.PolicyBand.objects.all(), required=False, label="Policy Band")
    source_users = DynamicModelMultipleChoiceField(
        queryset=models.UserObject.objects.all(), label="Source User Objects", required=False
    )
    source_user_groups = DynamicModelMultipleChoiceField(
        queryset=models.UserObjectGroup.objects.all(), label="Source User Object Groups", required=False
    )
    source_addresses = DynamicModelMultipleChoiceField(
        queryset=models.AddressObject.objects.all(), label="Source Address Objects", required=False
    )
    source_address_groups = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(), label="Source Address Object Groups", required=False
    )
    source_zones = DynamicModelMultipleChoiceField(
        queryset=models.Zone.objects.all(), label="Source Zones", required=False
    )
    source_zone_groups = DynamicModelMultipleChoiceField(
        queryset=models.ZoneGroup.objects.all(), label="Source Zone Groups", required=False
    )
    source_services = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObject.objects.all(), label="Source Service Objects", required=False
    )
    source_service_groups = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObjectGroup.objects.all(), label="Source Service Object Groups", required=False
    )
    destination_addresses = DynamicModelMultipleChoiceField(
        queryset=models.AddressObject.objects.all(), label="Destination Address Objects", required=False
    )
    destination_address_groups = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(), label="Destination Address Object Groups", required=False
    )
    destination_zones = DynamicModelMultipleChoiceField(
        queryset=models.Zone.objects.all(), label="Destination Zones", required=False
    )
    destination_zone_groups = DynamicModelMultipleChoiceField(
        queryset=models.ZoneGroup.objects.all(), label="Destination Zone Groups", required=False
    )
    destination_services = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObject.objects.all(), label="Destination Service Objects", required=False
    )
    destination_service_groups = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObjectGroup.objects.all(), label="Destination Service Object Groups", required=False
    )
    applications = DynamicModelMultipleChoiceField(
        queryset=models.ApplicationObject.objects.all(), label="Destination Application Objects", required=False
    )
    application_groups = DynamicModelMultipleChoiceField(
        queryset=models.ApplicationObjectGroup.objects.all(),
        label="Destination Application Object Groups",
        required=False,
    )
    request_id = forms.CharField(required=False, label="Optional field for request ticket identifier.")

    class Meta:
        """Meta attributes."""

        model = models.PolicyRule
        fields = (
            # pylint: disable=duplicate-code
            "name",
            "rule_type",
            "band",
            "position",
            "chain",
            "index",
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
            "log",
            "status",
            "tags",
            "request_id",
            "description",
        )

    def __init__(self, *args, **kwargs):
        """Drop the fields the rule type cannot use."""
        super().__init__(*args, **kwargs)
        if self.instance.present_in_database:
            rule_type = self.instance.rule_type
        else:
            rule_type = self.data.get("rule_type") or self.initial.get("rule_type") or self.instance.rule_type
        self.rule_type = rule_type
        self.initial["rule_type"] = rule_type
        if rule_type == "nftables":
            for field in (
                "band",
                "position",
                "negate_source",
                "negate_destination",
                *models.PolicyRule.PANOS_ONLY_RELATIONS,
            ):
                del self.fields[field]
            self.fields["chain"].required = True
            self.fields["action"].choices = [i for i in self.fields["action"].choices if i[0] != "remark"]
        else:
            for field in ("chain", *models.PolicyRule.NFTABLES_ONLY_RELATIONS):
                del self.fields[field]
            self.fields["band"].required = True
            self.fields["position"].required = True
        self.combine_grouped_fields()

    def clean(self):
        """Use the rule type the form was built for and check the related objects against it."""
        super().clean()
        self.cleaned_data["rule_type"] = self.rule_type
        models.PolicyRule.validate_relations(self.cleaned_data.get("rule_type"), self.cleaned_data)
        return self.cleaned_data


# TODO: Refactor
class PolicyRuleBulkEditForm(NautobotBulkEditForm):
    """PolicyRule bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.PolicyRule.objects.all(), widget=forms.MultipleHiddenInput)
    band = DynamicModelChoiceField(queryset=models.PolicyBand.objects.all(), required=False, label="Policy Band")
    position = forms.ChoiceField(choices=add_blank_choice(choices.POSITION_CHOICES), required=False)
    chain = forms.ChoiceField(choices=add_blank_choice(choices.CHAIN_CHOICES), required=False)
    index = forms.IntegerField(required=False, min_value=0)
    action = forms.ChoiceField(choices=add_blank_choice(choices.ACTION_CHOICES), required=False)
    log = forms.BooleanField(required=False)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description", "tags", "index"]


class PolicyFilterForm(NautobotFilterForm, TenancyFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name", "rule_type", "assigned_devices", "assigned_dynamic_groups"]

    model = models.Policy
    rule_type = forms.MultipleChoiceField(choices=choices.RULE_TYPE_CHOICES, required=False, label="Rule Type")
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    assigned_devices = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
    assigned_dynamic_groups = DynamicModelChoiceField(queryset=DynamicGroup.objects.all(), required=False)


class PolicyForm(NautobotModelForm, TenancyForm):
    """Policy creation/edit form."""

    assigned_devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    assigned_dynamic_groups = DynamicModelMultipleChoiceField(queryset=DynamicGroup.objects.all(), required=False)
    policy_rules = DynamicModelMultipleChoiceField(
        queryset=models.PolicyRule.objects.all(), required=False, query_params={"rule_type": "$rule_type"}
    )

    class Meta:
        """Meta attributes."""

        model = models.Policy
        fields = [
            "name",
            "rule_type",
            "description",
            "policy_rules",
            "status",
            "assigned_devices",
            "assigned_dynamic_groups",
            "tenant_group",
            "tenant",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        """Lock the rule type once the Policy exists."""
        super().__init__(*args, **kwargs)
        if self.instance.present_in_database:
            self.fields["rule_type"].disabled = True

    def clean(self):
        """Refuse Policy Rules of another type."""
        super().clean()
        models.Policy.validate_policy_rules(self.cleaned_data.get("rule_type"), self.cleaned_data.get("policy_rules"))
        return self.cleaned_data


class PolicyBulkEditForm(NautobotBulkEditForm):
    """Policy bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.Policy.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    assigned_devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    assigned_dynamic_groups = DynamicModelMultipleChoiceField(queryset=DynamicGroup.objects.all(), required=False)
    policy_rules = DynamicModelMultipleChoiceField(queryset=models.PolicyRule.objects.all(), required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


# NATPolicy


class NATPolicyRuleFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name"]

    model = models.NATPolicyRule
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    tag = TagFilterField(models.NATPolicyRule)


class NATPolicyRuleForm(fields.ObjectOrGroupFormMixin, NautobotModelForm):
    """NATPolicyRule creation/edit form."""

    # Metadata
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)
    request_id = forms.CharField(required=False, label="Optional field for request ticket identifier.")

    # Data that can not undergo a translation
    source_zones = DynamicModelMultipleChoiceField(
        queryset=models.Zone.objects.all(), label="Source Zones", required=False
    )
    source_zone_groups = DynamicModelMultipleChoiceField(
        queryset=models.ZoneGroup.objects.all(), label="Source Zone Groups", required=False
    )
    destination_zones = DynamicModelMultipleChoiceField(
        queryset=models.Zone.objects.all(), label="Destination Zones", required=False
    )
    destination_zone_groups = DynamicModelMultipleChoiceField(
        queryset=models.ZoneGroup.objects.all(), label="Destination Zone Groups", required=False
    )

    # Original source data
    original_source_addresses = DynamicModelMultipleChoiceField(
        queryset=models.AddressObject.objects.all(), label="Original Source Address Objects", required=False
    )
    original_source_address_groups = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(), label="Original Source Address Object Groups", required=False
    )

    # Translated source data
    translated_source_addresses = DynamicModelMultipleChoiceField(
        queryset=models.AddressObject.objects.all(), label="Translated Source Address Objects", required=False
    )
    translated_source_address_groups = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(),
        label="Translated Source Address Object Groups",
        required=False,
    )

    # Original destination data
    original_destination_addresses = DynamicModelMultipleChoiceField(
        queryset=models.AddressObject.objects.all(), label="Original Destination Address Objects", required=False
    )
    original_destination_address_groups = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(),
        label="Original Destination Address Object Groups",
        required=False,
    )
    original_destination_services = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObject.objects.all(), label="Original Destination Service Objects", required=False
    )
    original_destination_service_groups = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObjectGroup.objects.all(),
        label="Original Destination Service Object Groups",
        required=False,
    )

    # Translated destination data
    translated_destination_addresses = DynamicModelMultipleChoiceField(
        queryset=models.AddressObject.objects.all(), label="Translated Destination Address Objects", required=False
    )
    translated_destination_address_groups = DynamicModelMultipleChoiceField(
        queryset=models.AddressObjectGroup.objects.all(),
        label="Translated Destination Address Object Groups",
        required=False,
    )
    translated_destination_services = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObject.objects.all(), label="Translated Destination Service Objects", required=False
    )
    translated_destination_service_groups = DynamicModelMultipleChoiceField(
        queryset=models.ServiceObjectGroup.objects.all(),
        label="Translated Destination Service Object Groups",
        required=False,
    )

    class Meta:
        """Meta attributes."""

        model = models.NATPolicyRule
        fields = (
            # pylint: disable=duplicate-code
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
            "tags",
            "request_id",
            "description",
        )

    def __init__(self, *args, **kwargs):
        """Show one picker for each object and group field pair."""
        super().__init__(*args, **kwargs)
        self.combine_grouped_fields()

    def clean(self):
        """Refuse host relative Address Objects."""
        super().clean()
        models.NATPolicyRule.validate_relations(self.cleaned_data)
        return self.cleaned_data


# TODO: Refactor
class NATPolicyRuleBulkEditForm(PolicyRuleBulkEditForm):
    """NATPolicyRule bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.NATPolicyRule.objects.all(), widget=forms.MultipleHiddenInput)
    # NAT rules have no band, position or chain, so drop the ones inherited from PolicyRuleBulkEditForm.
    band = None
    position = None
    chain = None
    log = forms.BooleanField(required=False)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description", "tags"]


class NATPolicyFilterForm(NautobotFilterForm, TenancyFilterForm):
    """Filter form to filter searches."""

    field_order = ["q", "name", "assigned_devices", "assigned_dynamic_groups"]

    model = models.NATPolicy
    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Description.",
    )
    name = forms.CharField(required=False, label="Name")
    assigned_devices = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
    assigned_dynamic_groups = DynamicModelChoiceField(queryset=DynamicGroup.objects.all(), required=False)


class NATPolicyForm(NautobotModelForm, TenancyForm):
    """NATPolicy creation/edit form."""

    assigned_devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    assigned_dynamic_groups = DynamicModelMultipleChoiceField(queryset=DynamicGroup.objects.all(), required=False)
    nat_policy_rules = DynamicModelMultipleChoiceField(queryset=models.NATPolicyRule.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        model = models.NATPolicy
        fields = [
            "name",
            "description",
            "nat_policy_rules",
            "status",
            "assigned_devices",
            "assigned_dynamic_groups",
            "tenant_group",
            "tenant",
            "tags",
        ]


class NATPolicyBulkEditForm(NautobotBulkEditForm):
    """NATPolicy bulk edit form."""

    pk = DynamicModelMultipleChoiceField(queryset=models.NATPolicy.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)
    assigned_devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    assigned_dynamic_groups = DynamicModelMultipleChoiceField(queryset=DynamicGroup.objects.all(), required=False)
    policy_rules = DynamicModelMultipleChoiceField(queryset=models.NATPolicyRule.objects.all(), required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]
