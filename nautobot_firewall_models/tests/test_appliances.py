"""Tests for Firewalls, HA Groups and Firewall Groups, and what is assigned to them."""

# pylint: disable=invalid-name, duplicate-code
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from nautobot.apps.testing import APITestCase, APIViewTestCases, TestCase, ViewTestCases, post_data
from nautobot.extras.models import Status
from nautobot.ipam.models import IPAddress, Namespace, Prefix
from rest_framework import status as drf_status

from nautobot_firewall_models import models

from . import fixtures
from .test_api import IncludeM2MAPITestCaseMixin


def management_address(address):
    """Return an IP Address in 10.0.0.0/24 to use as an HA Group's management address."""
    status = Status.objects.get(name="Active")
    namespace, _ = Namespace.objects.get_or_create(name="global")
    Prefix.objects.get_or_create(network="10.0.0.0", prefix_length=24, namespace=namespace, status=status)
    return IPAddress.objects.get_or_create(address=f"{address}/24", namespace=namespace, status=status)[0]


def firewall(name):
    """Return a new Firewall bound to a new Virtual Machine."""
    return models.Firewall.objects.create(name=name, virtual_machine=fixtures.create_virtual_machine(f"{name}-vm"))


class TestFirewallModels(DjangoTestCase):
    """Test the rules for binding Firewalls and grouping them."""

    def setUp(self) -> None:
        """Create an HA Group of two Firewalls, a standalone Firewall and a Firewall Group."""
        self.ha = fixtures.create_ha_group()
        self.peer_a, self.peer_b = self.ha.firewalls.all()
        self.solo = firewall("solo")
        self.group = models.FirewallGroup.objects.create(name="edge")

    def test_firewall_binds_exactly_one_device_or_virtual_machine(self):
        """A Firewall needs one Device or one Virtual Machine, never neither or both."""
        host = fixtures.create_linux_host("fw-host", "10.0.0.60")
        with self.assertRaises(ValidationError):
            models.Firewall(name="nothing").full_clean()
        with self.assertRaises(ValidationError):
            models.Firewall(name="both", device=host, virtual_machine=self.solo.virtual_machine).full_clean()
        models.Firewall(name="device", device=host).full_clean()

    def test_device_is_only_one_firewall(self):
        """A Device or Virtual Machine can be only one Firewall."""
        with self.assertRaises(IntegrityError), transaction.atomic():
            models.Firewall.objects.create(name="again", virtual_machine=self.solo.virtual_machine)

    def test_ha_group_holds_two_firewalls(self):
        """A third Firewall can not join a full HA Group."""
        self.solo.ha_group = self.ha
        with self.assertRaises(ValidationError) as ctx:
            self.solo.full_clean()
        self.assertIn("ha_group", ctx.exception.message_dict)

    def test_firewall_used_directly_can_not_join_an_ha_group(self):
        """A Firewall in a Firewall Group, Policy or Zone directly is refused an HA Group, naming where it is used."""
        spare = models.HAGroup.objects.create(name="spare", management_address=management_address("10.0.0.61"))
        self.group.firewalls.add(self.solo)
        self.solo.ha_group = spare
        with self.assertRaises(ValidationError) as ctx:
            self.solo.full_clean()
        self.assertIn("Firewall Groups: edge", str(ctx.exception))

    def test_firewall_group_takes_ha_groups_not_their_members(self):
        """A Firewall Group holds HA Groups and standalone Firewalls; an HA member is refused, from either side."""
        self.group.ha_groups.add(self.ha)
        self.group.firewalls.add(self.solo)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.group.firewalls.add(self.peer_a)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.peer_b.firewall_groups.add(self.group)

    def test_policy_assignments(self):
        """Only PAN-OS Policies are assigned, and an HA member is assigned through its HA Group."""
        policy = models.Policy.objects.create(name="edge", rule_type="panos")
        policy.assigned_firewalls.add(self.solo)
        policy.assigned_ha_groups.add(self.ha)
        policy.assigned_firewall_groups.add(self.group)
        with self.assertRaises(ValidationError), transaction.atomic():
            policy.assigned_firewalls.add(self.peer_a)
        host_policy = models.Policy.objects.create(name="hosts", rule_type="nftables")
        with self.assertRaises(ValidationError), transaction.atomic():
            host_policy.assigned_firewalls.add(self.solo)

    def test_nat_policies_and_zones_refuse_ha_members(self):
        """NAT Policies and Zones also take an HA Group rather than its members."""
        nat_policy = models.NATPolicy.objects.create(name="nat")
        zone = models.Zone.objects.create(name="trust", zone_group=fixtures.default_zone_group())
        nat_policy.assigned_ha_groups.add(self.ha)
        zone.ha_groups.add(self.ha)
        with self.assertRaises(ValidationError), transaction.atomic():
            nat_policy.assigned_firewalls.add(self.peer_a)
        with self.assertRaises(ValidationError), transaction.atomic():
            zone.firewalls.add(self.peer_b)

    def test_assigned_policies_reach_firewalls_through_groups(self):
        """A Firewall sees Policies assigned to it, its HA Group, or a Firewall Group holding either."""
        direct = models.Policy.objects.create(name="direct", rule_type="panos")
        direct.assigned_firewalls.add(self.solo)
        by_ha = models.Policy.objects.create(name="by ha", rule_type="panos")
        by_ha.assigned_ha_groups.add(self.ha)
        by_group = models.Policy.objects.create(name="by group", rule_type="panos")
        by_group.assigned_firewall_groups.add(self.group)
        self.group.ha_groups.add(self.ha)

        self.assertEqual(set(self.peer_a.assigned_policies()), {by_ha, by_group})
        self.assertEqual(set(self.solo.assigned_policies()), {direct})
        self.assertEqual(set(self.ha.assigned_policies()), {by_ha, by_group})
        self.assertEqual(set(self.group.assigned_policies()), {by_group})


class FirewallUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Firewall views."""

    model = models.Firewall
    bulk_edit_data = {"description": "bulk description"}

    @classmethod
    def setUpTestData(cls):
        """Create Firewalls and a free Virtual Machine to bind."""
        for name in ("fw1", "fw2", "fw3"):
            firewall(name)
        status = Status.objects.get(name="Active").pk
        cls.form_data = {
            "name": "new",
            "virtual_machine": fixtures.create_virtual_machine("new-vm").pk,
            "status": status,
        }
        csv_vms = [fixtures.create_virtual_machine(f"csv{i}-vm") for i in range(3)]
        cls.csv_data = ("name,virtual_machine,status", *(f"csv{i},{vm.pk},Active" for i, vm in enumerate(csv_vms)))


class HAGroupUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the HA Group views."""

    model = models.HAGroup
    bulk_edit_data = {"description": "bulk description"}

    @classmethod
    def setUpTestData(cls):
        """Create HA Groups and two free Firewalls for the form."""
        for i in range(3):
            models.HAGroup.objects.create(name=f"ha{i}", management_address=management_address(f"10.0.0.{70 + i}"))
        status = Status.objects.get(name="Active").pk
        cls.free = [firewall("free-a"), firewall("free-b")]
        cls.form_data = {
            "name": "new",
            "management_address": management_address("10.0.0.80").pk,
            "firewalls": [i.pk for i in cls.free],
            "status": status,
        }
        addresses = [management_address(f"10.0.0.{90 + i}") for i in range(3)]
        cls.csv_data = (
            "name,management_address,status",
            *(f"csv{i},{address.pk},Active" for i, address in enumerate(addresses)),
        )

    def test_form_requires_two_free_firewalls(self):
        """The form needs exactly two Firewalls, none already in another HA Group or used directly."""
        self.add_permissions("nautobot_firewall_models.add_hagroup", "nautobot_firewall_models.view_firewall")
        self.add_permissions("ipam.view_ipaddress", "extras.view_status")
        url = reverse("plugins:nautobot_firewall_models:hagroup_add")
        data = {**self.form_data, "firewalls": [self.free[0].pk]}
        self.assertContains(self.client.post(url, post_data(data)), "An HA Group holds exactly 2 Firewalls.")

        models.FirewallGroup.objects.create(name="edge").firewalls.add(self.free[0])
        response = self.client.post(url, post_data(self.form_data))
        self.assertContains(response, "is used directly, so replace it with this HA Group first")

    def test_form_sets_and_releases_members(self):
        """Saving sets each chosen Firewall's HA Group and releases the ones no longer chosen."""
        self.add_permissions("nautobot_firewall_models.add_hagroup", "nautobot_firewall_models.change_hagroup")
        self.add_permissions("nautobot_firewall_models.view_hagroup", "nautobot_firewall_models.view_firewall")
        self.add_permissions("ipam.view_ipaddress", "extras.view_status")
        response = self.client.post(reverse("plugins:nautobot_firewall_models:hagroup_add"), post_data(self.form_data))
        self.assertHttpStatus(response, 302)
        group = models.HAGroup.objects.get(name="new")
        self.assertEqual(set(group.firewalls.all()), set(self.free))

        replacement = firewall("replacement")
        data = {**self.form_data, "firewalls": [self.free[0].pk, replacement.pk]}
        url = reverse("plugins:nautobot_firewall_models:hagroup_edit", kwargs={"pk": group.pk})
        self.assertHttpStatus(self.client.post(url, post_data(data)), 302)
        self.assertEqual(set(group.firewalls.all()), {self.free[0], replacement})
        self.free[1].refresh_from_db()
        self.assertIsNone(self.free[1].ha_group)


class FirewallGroupUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Firewall Group views."""

    model = models.FirewallGroup
    bulk_edit_data = {"description": "bulk description"}

    @classmethod
    def setUpTestData(cls):
        """Create Firewall Groups, a standalone Firewall and an HA Group."""
        for name in ("fg1", "fg2", "fg3"):
            models.FirewallGroup.objects.create(name=name)
        cls.solo = firewall("solo")
        cls.ha = fixtures.create_ha_group()
        status = Status.objects.get(name="Active").pk
        # The form picks Firewalls and HA Groups in one field.
        cls.form_data = {
            "name": "new",
            "firewalls_and_groups": [f"object:{cls.solo.pk}", f"group:{cls.ha.pk}"],
            "status": status,
        }
        cls.csv_data = ("name,status", "csv1,Active", "csv2,Active", "csv3,Active")

    def test_picker_saves_firewalls_and_ha_groups_and_refuses_ha_members(self):
        """The picker saves Firewalls and HA Groups, and refuses a Firewall that is in an HA Group."""
        self.add_permissions("nautobot_firewall_models.add_firewallgroup", "nautobot_firewall_models.view_firewall")
        self.add_permissions("nautobot_firewall_models.view_hagroup", "extras.view_status")
        url = reverse("plugins:nautobot_firewall_models:firewallgroup_add")
        self.assertHttpStatus(self.client.post(url, post_data(self.form_data)), 302)
        group = models.FirewallGroup.objects.get(name="new")
        self.assertEqual((list(group.firewalls.all()), list(group.ha_groups.all())), ([self.solo], [self.ha]))

        member = self.ha.firewalls.first()
        data = {**self.form_data, "name": "bad", "firewalls_and_groups": [f"object:{member.pk}"]}
        self.assertContains(self.client.post(url, post_data(data)), "select the HA Group instead")


class AssignmentPickerUIViewTest(TestCase):
    """Test the single picker that assigns Policies and binds Zones to Firewalls, HA Groups and Firewall Groups."""

    def setUp(self):
        """Grant access and create one of each appliance."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_policy",
            "nautobot_firewall_models.view_policy",
            "nautobot_firewall_models.add_zone",
            "nautobot_firewall_models.view_zone",
            "nautobot_firewall_models.view_zonegroup",
            "nautobot_firewall_models.view_firewall",
            "nautobot_firewall_models.view_hagroup",
            "nautobot_firewall_models.view_firewallgroup",
            "extras.view_status",
        )
        self.solo = firewall("solo")
        self.ha = fixtures.create_ha_group()
        self.group = models.FirewallGroup.objects.create(name="edge")
        self.status = Status.objects.get(name="Active").pk
        self.values = [f"firewall:{self.solo.pk}", f"hagroup:{self.ha.pk}", f"firewallgroup:{self.group.pk}"]

    def test_policy_form_assigns_all_three(self):
        """The Policy form has one Assigned To picker that saves Firewalls, HA Groups and Firewall Groups."""
        url = reverse("plugins:nautobot_firewall_models:policy_add")
        response = self.client.get(url)
        self.assertContains(response, 'name="assigned_to"')
        self.assertContains(response, 'data-url="/api/plugins/firewall/grouped-objects/appliances/"')

        data = {"name": "edge", "rule_type": "panos", "status": self.status, "assigned_to": self.values}
        self.assertHttpStatus(self.client.post(url, post_data(data)), 302)
        policy = models.Policy.objects.get(name="edge")
        self.assertEqual(
            (list(policy.assigned_firewalls.all()), list(policy.assigned_ha_groups.all())), ([self.solo], [self.ha])
        )
        self.assertEqual(list(policy.assigned_firewall_groups.all()), [self.group])

    def test_zone_form_binds_all_three(self):
        """The Zone form has one Bound To picker that saves Firewalls, HA Groups and Firewall Groups."""
        data = {
            "name": "dmz",
            "zone_group": fixtures.default_zone_group().pk,
            "status": self.status,
            "bound_to": self.values,
        }
        response = self.client.post(reverse("plugins:nautobot_firewall_models:zone_add"), post_data(data))

        self.assertHttpStatus(response, 302)
        zone = models.Zone.objects.get(name="dmz")
        self.assertEqual(
            (list(zone.firewalls.all()), list(zone.ha_groups.all()), list(zone.firewall_groups.all())),
            ([self.solo], [self.ha], [self.group]),
        )

    def test_firewall_page_lists_assigned_policies(self):
        """A Firewall's page lists the Policies that reach it and links to its rules."""
        self.add_permissions("nautobot_firewall_models.view_firewall")
        policy = models.Policy.objects.create(name="by ha", rule_type="panos")
        policy.assigned_ha_groups.add(self.ha)
        member = self.ha.firewalls.first()

        response = self.client.get(member.get_absolute_url())
        self.assertContains(response, "by ha")
        self.assertContains(response, member.policy_rules_url)


class FirewallAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the Firewall API."""

    model = models.Firewall
    bulk_update_data = {"description": "bulk description"}

    @classmethod
    def setUpTestData(cls):
        """Create Firewalls and free Virtual Machines to bind."""
        for name in ("fw1", "fw2", "fw3"):
            firewall(name)
        cls.create_data = [
            {"name": f"new{i}", "virtual_machine": fixtures.create_virtual_machine(f"new{i}-vm").pk} for i in range(3)
        ]


class HAGroupAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the HA Group API."""

    model = models.HAGroup
    bulk_update_data = {"description": "bulk description"}

    @classmethod
    def setUpTestData(cls):
        """Create HA Groups and management addresses."""
        for i in range(3):
            models.HAGroup.objects.create(name=f"ha{i}", management_address=management_address(f"10.0.0.{70 + i}"))
        cls.create_data = [
            {"name": f"new{i}", "management_address": management_address(f"10.0.0.{80 + i}").pk} for i in range(3)
        ]


class FirewallGroupAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the Firewall Group API."""

    model = models.FirewallGroup
    bulk_update_data = {"description": "bulk description"}

    @classmethod
    def setUpTestData(cls):
        """Create Firewall Groups and a Firewall to add."""
        for name in ("fg1", "fg2", "fg3"):
            models.FirewallGroup.objects.create(name=name)
        solo = firewall("solo")
        cls.create_data = [{"name": f"new{i}", "firewalls": [solo.pk]} for i in range(3)]


class ApplianceAPITest(APITestCase):
    """Test the appliance rules over the REST API."""

    def setUp(self):
        """Grant access and create an HA Group and a standalone Firewall."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_firewall",
            "nautobot_firewall_models.change_firewall",
            "nautobot_firewall_models.view_firewall",
            "nautobot_firewall_models.view_hagroup",
            "nautobot_firewall_models.view_firewallgroup",
            "nautobot_firewall_models.add_policy",
            "virtualization.view_virtualmachine",
        )
        self.ha = fixtures.create_ha_group()
        self.solo = firewall("solo")

    def _url(self, route, pk=None):
        if pk:
            return reverse(f"plugins-api:nautobot_firewall_models-api:{route}-detail", kwargs={"pk": pk})
        return reverse(f"plugins-api:nautobot_firewall_models-api:{route}-list")

    def test_firewall_needs_a_host(self):
        """Creating a Firewall without a Device or Virtual Machine is refused."""
        response = self.client.post(self._url("firewall"), {"name": "nothing"}, format="json", **self.header)
        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)

    def test_full_ha_group_is_refused(self):
        """Joining a full HA Group through the API is refused."""
        response = self.client.patch(
            self._url("firewall", self.solo.pk), {"ha_group": str(self.ha.pk)}, format="json", **self.header
        )
        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("ha_group", response.data)

    def test_policy_assignment_rules(self):
        """The API refuses HA members and non PAN-OS Policies on assignment."""
        member = self.ha.firewalls.first()
        response = self.client.post(
            self._url("policy"),
            {"name": "edge", "rule_type": "panos", "assigned_firewalls": [str(member.pk)]},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("select the HA Group instead", str(response.data["assigned_firewalls"]))

        response = self.client.post(
            self._url("policy"),
            {"name": "hosts", "rule_type": "nftables", "assigned_ha_groups": [str(self.ha.pk)]},
            format="json",
            **self.header,
        )
        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("Only PAN-OS Policies", str(response.data["assigned_ha_groups"]))

    def test_appliance_search_leaves_out_ha_members(self):
        """The assignment picker lists standalone Firewalls, HA Groups and Firewall Groups, not HA members."""
        group = models.FirewallGroup.objects.create(name="edge")
        url = reverse("plugins-api:nautobot_firewall_models-api:grouped-objects", kwargs={"kind": "appliances"})
        response = self.client.get(url, {"limit": 100}, **self.header)

        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        self.assertEqual(
            {i["id"] for i in response.data["results"]},
            {f"firewall:{self.solo.pk}", f"hagroup:{self.ha.pk}", f"firewallgroup:{group.pk}"},
        )
