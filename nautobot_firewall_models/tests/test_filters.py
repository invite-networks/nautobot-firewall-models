"""Unit tests for nautobot_firewall_models."""

# pylint: disable=invalid-name

from nautobot.apps.testing import FilterTestCases
from nautobot.dcim.models import Device
from nautobot.extras.models import DynamicGroup, Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix

from nautobot_firewall_models import filters, models
from nautobot_firewall_models.models import UserObject

from . import fixtures


class AddressObjectTestCase(FilterTestCases.FilterTestCase):
    """Test filtering operations for AddressObject Model."""

    queryset = models.AddressObject.objects.all()
    filterset = filters.AddressObjectFilterSet
    generic_filter_tests = (
        ("address_object_groups", "address_object_groups__id"),
        ("address_object_groups", "address_object_groups__name"),
    )

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        status_active = Status.objects.get(name="Active")
        global_namespace = Namespace.objects.get(name="Global")
        Prefix.objects.create(prefix="0.0.0.0/0", namespace=global_namespace, status=status_active)
        ip_addresses = (
            IPAddress.objects.create(address="10.0.0.1", status=status_active, namespace=global_namespace),
            IPAddress.objects.create(address="10.0.0.2", status=status_active, namespace=global_namespace),
            IPAddress.objects.create(address="10.0.0.3", status=status_active, namespace=global_namespace),
        )
        address_objects = (
            models.AddressObject.objects.create(
                name="test-address-object",
                status=status_active,
                ip_address=ip_addresses[0],
            ),
            models.AddressObject.objects.create(
                name="test-address-object-2",
                status=status_active,
                ip_address=ip_addresses[1],
            ),
            models.AddressObject.objects.create(
                name="test-address-object-3",
                status=status_active,
                ip_address=ip_addresses[2],
            ),
        )
        address_object_groups = (
            models.AddressObjectGroup.objects.create(name="test-address-object-group", status=status_active),
            models.AddressObjectGroup.objects.create(name="test-address-object-group-2", status=status_active),
            models.AddressObjectGroup.objects.create(name="test-address-object-group-3", status=status_active),
        )
        address_object_groups[0].address_objects.set([address_objects[0]])
        address_object_groups[1].address_objects.set([address_objects[1]])
        address_object_groups[2].address_objects.set([address_objects[2]])


class ApplicationObjectTestCase(FilterTestCases.FilterTestCase):
    """Test filtering operations for ApplicationObject Model."""

    queryset = models.ApplicationObject.objects.all()
    filterset = filters.ApplicationObjectFilterSet
    generic_filter_tests = (
        ("application_object_groups", "application_object_groups__id"),
        ("application_object_groups", "application_object_groups__name"),
    )

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        status_active = Status.objects.get(name="Active")
        application_objects = (
            models.ApplicationObject.objects.create(
                name="test-application-object",
                status=status_active,
            ),
            models.ApplicationObject.objects.create(
                name="test-application-object-2",
                status=status_active,
            ),
            models.ApplicationObject.objects.create(
                name="test-application-object-3",
                status=status_active,
            ),
        )
        application_object_groups = (
            models.ApplicationObjectGroup.objects.create(name="test-application-object-group", status=status_active),
            models.ApplicationObjectGroup.objects.create(name="test-application-object-group-2", status=status_active),
            models.ApplicationObjectGroup.objects.create(name="test-application-object-group-3", status=status_active),
        )
        application_object_groups[0].application_objects.set([application_objects[0]])
        application_object_groups[1].application_objects.set([application_objects[1]])
        application_object_groups[2].application_objects.set([application_objects[2]])


class UserObjectTestCase(FilterTestCases.FilterTestCase):
    """Test filtering operations for ApplicationObject Model."""

    queryset = models.UserObject.objects.all()
    filterset = filters.UserObjectFilterSet

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""

        status_active = Status.objects.get(name="Active")
        UserObject.objects.get_or_create(
            username="user1",
            name="Bob",
            status=status_active,
        )
        UserObject.objects.get_or_create(
            username="user2",
            name="Fred",
            status=status_active,
        )
        UserObject.objects.get_or_create(
            username="user3",
            name="Tom",
            status=status_active,
        )

    def test_q_filter_name(self):
        """Test q filter on name field"""
        params = {"q": "Bob"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_q_filter_username(self):
        """Test q filter on username field"""
        params = {"q": "user2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ZoneTestCase(FilterTestCases.FilterTestCase):
    """Test filtering operations for Zone Model."""

    queryset = models.Zone.objects.all()
    filterset = filters.ZoneFilterSet
    generic_filter_tests = (
        ("zone_group", "zone_group__id"),
        ("zone_group", "zone_group__name"),
        ("devices", "devices__id"),
        ("devices", "devices__name"),
    )

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        fixtures.create_zone_group()
        fixtures.bind_zone_devices()
        # A zone in a third group, so each group filter matches a strict subset of zones.
        models.Zone.objects.create(
            name="Guest", status=Status.objects.get(name="Active"), zone_group=fixtures.default_zone_group()
        )


class ZoneGroupTestCase(FilterTestCases.FilterTestCase):
    """Test filtering operations for ZoneGroup Model."""

    queryset = models.ZoneGroup.objects.all()
    filterset = filters.ZoneGroupFilterSet
    generic_filter_tests = (("name",),)

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        fixtures.create_zone_group()


class PolicyBandTestCase(FilterTestCases.FilterTestCase):
    """Test filtering operations for PolicyBand Model."""

    queryset = models.PolicyBand.objects.all()
    filterset = filters.PolicyBandFilterSet
    generic_filter_tests = (("name",), ("index",))

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        fixtures.create_policy_band()


class PolicyRuleTestCase(FilterTestCases.FilterTestCase):
    """Test filtering operations for PolicyRule Model."""

    queryset = models.PolicyRule.objects.all()
    filterset = filters.PolicyRuleFilterSet
    generic_filter_tests = (
        ("band", "band__id"),
        ("band", "band__name"),
    )

    @classmethod
    def setUpTestData(cls):
        """Set up test data."""
        fixtures.assign_policies()
        # A rule in a third band, outside every Policy, so each band filter matches a strict subset of rules.
        models.PolicyRule.objects.create(
            rule_type="panos",
            name="Unassigned",
            action="allow",
            band=models.PolicyBand.objects.get(name="Universal"),
            position="pre",
        )
        for group in DynamicGroup.objects.all():
            group.update_cached_members()
        cls.assigned = models.PolicyRule.objects.exclude(name="Unassigned")

    def test_position(self):
        """Filter rules by position."""
        params = {"position": ["post"]}
        self.assertQuerysetEqual(
            self.filterset(params, self.queryset).qs, self.queryset.filter(position="post"), ordered=False
        )

    def test_device_through_direct_assignment(self):
        """A Device sees the rules of Policies assigned to it directly."""
        params = {"device": ["HOU02-WAN00"]}
        self.assertEqual([rule.name for rule in self.filterset(params, self.queryset).qs], ["Policy Rule 1"])

    def test_device_through_dynamic_group(self):
        """A Device sees the rules of Policies assigned to a Dynamic Group it belongs to, in firewall order."""
        params = {"device": ["DFW02-WAN01"]}
        self.assertEqual(list(self.filterset(params, self.queryset).qs), list(self.assigned))

    def test_device_merges_policies_without_duplicates(self):
        """Rules shared by several Policies on one Device appear once, in band order."""
        device = Device.objects.get(name="DFW02-WAN00")
        rules = list(self.filterset({"device": [device.pk]}, self.queryset).qs)

        self.assertEqual(len(rules), len(set(rules)))
        self.assertEqual(rules, list(self.assigned))
