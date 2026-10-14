"""API serializers for nautobot_firewall_models."""

from django.core.exceptions import ValidationError as DjangoValidationError
from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin, ValidatedModelSerializer
from rest_framework import serializers

from nautobot_firewall_models import models


class ManagedLocallyGroupSerializerMixin:
    """Refuse members on a group whose status is Managed Locally."""

    def validate(self, attrs):
        """Check the resulting status and members together, using saved values for fields a PATCH leaves out."""
        model = self.Meta.model
        status = attrs.get("status", self.instance.status if self.instance else None)
        members = {}
        for field in model.members_fields:
            if field in attrs:
                members[field] = attrs[field]
            else:
                members[field] = getattr(self.instance, field).all() if self.instance else []
        run_model_check(model.validate_managed_members, status, members)
        return super().validate(attrs)


def run_model_check(check, *args):
    """Run a model validation function and report its errors the way the REST API expects."""
    try:
        check(*args)
    except DjangoValidationError as e:
        raise serializers.ValidationError(e.message_dict) from e


class FQDNSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """FQDN Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.FQDN
        fields = "__all__"


class AddressObjectSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """AddressObject Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.AddressObject
        fields = "__all__"


class AddressObjectGroupSerializer(
    ManagedLocallyGroupSerializerMixin, NautobotModelSerializer, TaggedModelSerializerMixin
):
    """AddressObjectGroup Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.AddressObjectGroup
        fields = "__all__"

    def validate(self, attrs):
        """Refuse nested groups that would loop, and host relative members while a PAN-OS or NAT rule uses the group."""
        if self.instance:
            run_model_check(
                self.instance.validate_members, attrs.get("address_objects"), attrs.get("address_object_groups")
            )
        return super().validate(attrs)


class ApplicationObjectSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """ApplicationObject Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ApplicationObject
        fields = "__all__"


class ApplicationObjectGroupSerializer(
    ManagedLocallyGroupSerializerMixin, NautobotModelSerializer, TaggedModelSerializerMixin
):
    """ApplicationObjectGroup Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ApplicationObjectGroup
        fields = "__all__"


class ServiceObjectSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """ServiceObject Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ServiceObject
        fields = "__all__"


class ServiceObjectGroupSerializer(
    ManagedLocallyGroupSerializerMixin, NautobotModelSerializer, TaggedModelSerializerMixin
):
    """ServiceObjectGroup Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ServiceObjectGroup
        fields = "__all__"


class UserObjectSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """UserObject Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.UserObject
        fields = "__all__"


class UserObjectGroupSerializer(
    ManagedLocallyGroupSerializerMixin, NautobotModelSerializer, TaggedModelSerializerMixin
):
    """UserObjectGroup Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.UserObjectGroup
        fields = "__all__"


class ZoneSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """Zone Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.Zone
        fields = "__all__"


class ZoneGroupSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """ZoneGroup Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ZoneGroup
        fields = "__all__"


class ExpandedZoneSerializer(serializers.ModelSerializer):
    """Read-only Zone representation for a rule's zones after its ZoneGroups are expanded."""

    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:nautobot_firewall_models-api:zone-detail")

    class Meta:
        """Meta attributes."""

        model = models.Zone
        fields = ["id", "url", "name"]


class RenderedAddressObjectSerializer(serializers.ModelSerializer):
    """Read-only Address Object representation for a rule's rendered addresses."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_firewall_models-api:addressobject-detail"
    )

    class Meta:
        """Meta attributes."""

        model = models.AddressObject
        fields = ["id", "url", "name"]


class RenderedAddressObjectGroupSerializer(serializers.ModelSerializer):
    """Read-only Address Object Group representation for a rule's rendered address groups."""

    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:nautobot_firewall_models-api:addressobjectgroup-detail"
    )

    class Meta:
        """Meta attributes."""

        model = models.AddressObjectGroup
        fields = ["id", "url", "name"]


class PolicyBandSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """PolicyBand Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.PolicyBand
        fields = "__all__"


class PolicyRuleSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """PolicyRule Serializer."""

    index = serializers.IntegerField(required=False, default=None)
    expanded_source_zones = ExpandedZoneSerializer(many=True, read_only=True)
    expanded_destination_zones = ExpandedZoneSerializer(many=True, read_only=True)
    rendered_source_addresses = RenderedAddressObjectSerializer(many=True, read_only=True)
    rendered_source_address_groups = RenderedAddressObjectGroupSerializer(many=True, read_only=True)
    rendered_destination_addresses = RenderedAddressObjectSerializer(many=True, read_only=True)
    rendered_destination_address_groups = RenderedAddressObjectGroupSerializer(many=True, read_only=True)

    class Meta:
        """Meta attributes."""

        model = models.PolicyRule
        fields = "__all__"

    def validate(self, attrs):
        """Check the related objects against the rule type, using the saved values for fields a PATCH leaves out."""
        rule_type = self.instance.rule_type if self.instance else attrs.get("rule_type")
        relations = {}
        for field in (
            *models.PolicyRule.PANOS_ONLY_RELATIONS,
            *models.PolicyRule.NFTABLES_ONLY_RELATIONS,
            *models.PolicyRule.ADDRESS_RELATIONS,
        ):
            if field in attrs:
                relations[field] = attrs[field]
            elif self.instance:
                relations[field] = getattr(self.instance, field).all()
        run_model_check(models.PolicyRule.validate_relations, rule_type, relations)
        return super().validate(attrs)


class PolicySerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """Policy Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.Policy
        fields = "__all__"

    def validate(self, attrs):
        """Refuse Policy Rules of another type."""
        rule_type = self.instance.rule_type if self.instance else attrs.get("rule_type")
        run_model_check(models.Policy.validate_policy_rules, rule_type, attrs.get("policy_rules"))
        return super().validate(attrs)


class NATPolicyRuleSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """PolicyRule Serializer."""

    expanded_source_zones = ExpandedZoneSerializer(many=True, read_only=True)
    expanded_destination_zones = ExpandedZoneSerializer(many=True, read_only=True)

    class Meta:
        """Meta attributes."""

        model = models.NATPolicyRule
        fields = "__all__"

    def validate(self, attrs):
        """Refuse host relative Address Objects."""
        run_model_check(models.NATPolicyRule.validate_relations, attrs)
        return super().validate(attrs)


class NATPolicySerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """NATPolicy Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.NATPolicy
        fields = "__all__"


###########################
# Through Models
###########################


class PolicyDeviceM2MSerializer(ValidatedModelSerializer):
    """PolicyDeviceM2M Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.PolicyDeviceM2M
        fields = "__all__"


class PolicyDynamicGroupM2MSerializer(ValidatedModelSerializer):
    """PolicyDynamicGroupM2M Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.PolicyDynamicGroupM2M
        fields = "__all__"


class NATPolicyDeviceM2MSerializer(ValidatedModelSerializer):
    """NATPolicyDeviceM2M Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.NATPolicyDeviceM2M
        fields = "__all__"


class NATPolicyDynamicGroupM2MSerializer(ValidatedModelSerializer):
    """NATPolicyDynamicGroupM2M Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.NATPolicyDynamicGroupM2M
        fields = "__all__"
