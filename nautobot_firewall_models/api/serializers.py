"""API serializers for nautobot_firewall_models."""

from django.core.exceptions import ValidationError as DjangoValidationError
from nautobot.apps.api import NautobotModelSerializer, TaggedModelSerializerMixin, ValidatedModelSerializer
from rest_framework import serializers

from nautobot_firewall_models import models


def run_model_check(check, *args):
    """Run a model validation function and report its errors the way the REST API expects."""
    try:
        check(*args)
    except DjangoValidationError as e:
        raise serializers.ValidationError(e.message_dict) from e


class IPRangeSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):  # pylint: disable=too-many-ancestors
    """IPRange Serializer."""

    start_address = serializers.CharField()
    end_address = serializers.CharField()

    class Meta:
        """Meta attributes."""

        model = models.IPRange
        fields = "__all__"

        # Omit the UniqueTogetherValidators that would be automatically added to validate (start_address, end_address, vrf).
        # This prevents vrf from being interpreted as a required field.
        validators = []

    def validate(self, attrs):
        """Custom validate method to enforce unique constraints on IPRange model."""
        # Validate uniqueness of (start_address, end_address, vrf) since we omitted the automatically-created validator above.
        start_address = attrs.get("start_address")
        end_address = attrs.get("end_address")
        vrf = attrs.get("vrf")
        if not any([start_address is not None, end_address is not None, vrf is not None]):
            return super().validate(attrs)

        # Use existing object's attributes for partial updates
        if self.instance:
            start_address = start_address or self.instance.start_address
            end_address = end_address or self.instance.end_address
            vrf = vrf or self.instance.vrf
            qs = models.IPRange.objects.exclude(pk=self.instance.pk)
        else:
            qs = models.IPRange.objects.all()

        if vrf is not None:
            if qs.filter(start_address=start_address, end_address=end_address, vrf=vrf).exists():
                raise serializers.ValidationError("The fields start_address, end_address, vrf must make a unique set.")
        elif qs.filter(start_address=start_address, end_address=end_address, vrf__isnull=True).exists():
            raise serializers.ValidationError("The fields start_address, end_address must make a unique set.")

        return super().validate(attrs)


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


class AddressObjectGroupSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """AddressObjectGroup Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.AddressObjectGroup
        fields = "__all__"

    def validate(self, attrs):
        """Refuse host relative Address Objects while a PAN-OS or NAT Policy Rule uses the group."""
        if self.instance and "address_objects" in attrs:
            run_model_check(self.instance.validate_address_objects, attrs["address_objects"])
        return super().validate(attrs)


class ApplicationObjectSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
    """ApplicationObject Serializer."""

    class Meta:
        """Meta attributes."""

        model = models.ApplicationObject
        fields = "__all__"


class ApplicationObjectGroupSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
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


class ServiceObjectGroupSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
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


class UserObjectGroupSerializer(NautobotModelSerializer, TaggedModelSerializerMixin):
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
