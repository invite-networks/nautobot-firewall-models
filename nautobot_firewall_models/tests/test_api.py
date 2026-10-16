"""Unit tests for nautobot_firewall_models."""

# pylint: disable=invalid-name, duplicate-code, too-many-lines
from unittest import mock

from django.urls import reverse
from nautobot.apps.testing import APITestCase, APIViewTestCases
from nautobot.dcim.models import Device, DeviceType, Location, Platform
from nautobot.extras.models import Role, Status
from nautobot.ipam.models import Prefix
from nautobot.users.models import ObjectPermission
from rest_framework import status as drf_status

from nautobot_firewall_models import models

from . import fixtures


class IncludeM2MAPITestCaseMixin:
    """Mixin to enable m2m fields in the test_bulk_create_objects test.

    The REST API no longer returns m2m fields by default in Nautobot v3.0.0+.
    This mixin restores the m2m field so that the test_bulk_create_objects test
    can find them.
    """

    def _patched_get_list_url(self):
        return super()._get_list_url() + "?exclude_m2m=false"

    def test_bulk_create_objects(self):
        with mock.patch.object(self, "_get_list_url", self._patched_get_list_url):
            return super().test_bulk_create_objects()


class FQDNAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the Protocol viewsets."""

    model = models.FQDN
    brief_fields = ["display", "id", "name", "url"]
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        cls.create_data = [
            {"name": "test.local"},
            {"name": "sub.test.local"},
        ]
        fixtures.create_fqdn()


class ApplicationObjectAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the ApplicationObject viewsets."""

    model = models.ApplicationObject
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_app_obj()
        models.ApplicationObject.objects.create(name="deleteableobj1")
        models.ApplicationObject.objects.create(name="deleteableobj2")
        models.ApplicationObject.objects.create(name="deleteableobj3")
        cls.create_data = [
            {"name": "obj2", "risk": 1},
            {"name": "obj1", "risk": 1},
        ]


class ApplicationObjectGroupAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the ApplicationObjectGroup viewsets."""

    model = models.ApplicationObjectGroup
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_app_group()
        app_obj = models.ApplicationObject.objects.first()
        models.ApplicationObjectGroup.objects.create(name="deleteableobj1")
        models.ApplicationObjectGroup.objects.create(name="deleteableobj2")
        models.ApplicationObjectGroup.objects.create(name="deleteableobj3")

        cls.create_data = [
            {"name": "test1", "application_objects": [app_obj.id]},
            {"name": "test2", "application_objects": [app_obj.id]},
        ]


class AddressObjectAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the AddressObject viewsets."""

    model = models.AddressObject
    bulk_update_data = {"description": "test update description"}
    choices_fields = ["dynamic"]

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_addr_obj()
        fqdn = models.FQDN.objects.first()
        prefix = Prefix.objects.first()
        models.AddressObject.objects.create(name="deleteableobj1", prefix=prefix)
        models.AddressObject.objects.create(name="deleteableobj2", prefix=prefix)
        models.AddressObject.objects.create(name="deleteableobj3", prefix=prefix)

        cls.create_data = [
            {"name": "obj2", "prefix": prefix.id},
            {"name": "obj1", "fqdn": fqdn.id},
        ]


class AddressObjectGroupAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the AddressObjectGroup viewsets."""

    model = models.AddressObjectGroup
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_addr_group()
        addr_obj = models.AddressObject.objects.first()
        models.AddressObjectGroup.objects.create(name="deleteableobj1")
        models.AddressObjectGroup.objects.create(name="deleteableobj2")
        models.AddressObjectGroup.objects.create(name="deleteableobj3")

        cls.create_data = [
            {"name": "test1", "address_objects": [addr_obj.id]},
            {"name": "test2", "address_objects": [addr_obj.id]},
        ]


class ServiceObjectAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the ServiceObject viewsets."""

    model = models.ServiceObject
    bulk_update_data = {"description": "test update description"}
    choices_fields = ["ip_protocol"]

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        models.ServiceObject.objects.create(name="deleteableobj1", ip_protocol="TCP")
        models.ServiceObject.objects.create(name="deleteableobj2", ip_protocol="TCP")
        models.ServiceObject.objects.create(name="deleteableobj3", ip_protocol="TCP")

        cls.create_data = [
            {"name": "HTTP", "port": "8088", "ip_protocol": "TCP"},
            {"name": "HTTP", "port": "8080-8088", "ip_protocol": "TCP"},
        ]
        fixtures.create_svc_obj()


class ServiceGroupAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the ServiceGroup viewsets."""

    model = models.ServiceObjectGroup
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_svc_group()
        svc_obj = models.ServiceObject.objects.first()
        models.ServiceObjectGroup.objects.create(name="deleteableobj1")
        models.ServiceObjectGroup.objects.create(name="deleteableobj2")
        models.ServiceObjectGroup.objects.create(name="deleteableobj3")

        cls.create_data = [
            {"name": "test1", "service_objects": [svc_obj.id]},
            {"name": "test2", "service_objects": [svc_obj.id]},
        ]


class UserObjectAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the User viewsets."""

    model = models.UserObject
    bulk_update_data = {"name": "User Name 123"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        cls.create_data = [
            {"username": "test1", "name": "Foo"},
            {"username": "test2", "name": "Bar"},
        ]
        models.UserObject.objects.create(username="deleteableobj1", name="deleteableobj1")
        models.UserObject.objects.create(username="deleteableobj2", name="deleteableobj2")
        models.UserObject.objects.create(username="deleteableobj3", name="deleteableobj3")
        fixtures.create_user_obj()


class UserObjectGroupAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the UserGroup viewsets."""

    model = models.UserObjectGroup
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_user_group()
        user = models.UserObject.objects.first()
        models.UserObjectGroup.objects.create(name="deleteableobj1")
        models.UserObjectGroup.objects.create(name="deleteableobj2")
        models.UserObjectGroup.objects.create(name="deleteableobj3")

        cls.create_data = [
            {"name": "test1", "user_objects": [user.id]},
            {"name": "test2", "user_objects": [user.id]},
        ]


class ZoneAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the Zone viewsets."""

    model = models.Zone
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        cls.create_data = [
            {"name": "trust"},
            {"name": "untrust"},
        ]
        models.Zone.objects.create(name="deleteableobj1")
        models.Zone.objects.create(name="deleteableobj2")
        models.Zone.objects.create(name="deleteableobj3")
        fixtures.create_zone()


class ZoneGroupAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the ZoneGroup viewsets."""

    model = models.ZoneGroup
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_zone_group()
        zone = models.Zone.objects.first()
        models.ZoneGroup.objects.create(name="deleteableobj1")
        models.ZoneGroup.objects.create(name="deleteableobj2")
        models.ZoneGroup.objects.create(name="deleteableobj3")

        cls.create_data = [
            {"name": "test1", "zones": [zone.id]},
            {"name": "test2", "zones": [zone.id]},
        ]


class PolicyBandAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the PolicyBand viewsets."""

    model = models.PolicyBand
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_policy_band()
        models.PolicyBand.objects.create(name="deleteableobj1", index=101)
        models.PolicyBand.objects.create(name="deleteableobj2", index=102)
        models.PolicyBand.objects.create(name="deleteableobj3", index=103)
        cls.create_data = [
            {"name": "No Trust", "index": 15},
            {"name": "High Security", "index": 25, "description": "Sensitive systems"},
        ]


class PolicyRuleAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the PolicyRule viewsets."""

    model = models.PolicyRule
    bulk_update_data = {"log": False}
    choices_fields = ["action", "position", "rule_type", "chain"]

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_policy_rule()
        band = models.PolicyBand.objects.first()
        src_usr = models.UserObject.objects.first()
        src_addr = models.AddressObject.objects.first()
        dest_addr = models.AddressObject.objects.last()
        svc = models.ServiceObject.objects.first()
        models.PolicyRule.objects.create(
            rule_type="panos", band=band, position="pre", name="deleteableobj1", action="deny", index=1
        )
        models.PolicyRule.objects.create(
            rule_type="panos", band=band, position="pre", name="deleteableobj2", action="deny", index=1
        )
        models.PolicyRule.objects.create(
            rule_type="panos", band=band, position="pre", name="deleteableobj3", action="deny", index=1
        )
        cls.create_data = [
            {
                # pylint: disable=R0801
                "source_users": [src_usr.id],
                "source_addresses": [src_addr.id],
                "destination_addresses": [dest_addr.id],
                "action": "deny",
                "log": True,
                "destination_services": [svc.id],
                "name": "test rule 1",
                "rule_type": "panos",
                "band": band.id,
                "position": "pre",
            },
            {
                "source_users": [src_usr.id],
                "source_addresses": [src_addr.id],
                "destination_addresses": [dest_addr.id],
                "action": "deny",
                "log": False,
                "destination_services": [svc.id],
                "name": "test rule 2",
                "rule_type": "panos",
                "band": band.id,
                "position": "post",
            },
        ]


class PolicyAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the Policy viewsets."""

    model = models.Policy
    bulk_update_data = {"description": "test update description"}
    choices_fields = ["rule_type"]

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_policy()
        pol_rule = models.PolicyRule.objects.first()
        models.Policy.objects.create(rule_type="panos", name="deleteableobj1")
        models.Policy.objects.create(rule_type="panos", name="deleteableobj2")
        models.Policy.objects.create(rule_type="panos", name="deleteableobj3")

        cls.create_data = [
            {"name": "test 1", "rule_type": "panos", "policy_rules": [pol_rule.id]},
            {"name": "test 2", "rule_type": "panos", "policy_rules": [pol_rule.id], "description": "Test desc"},
        ]


class NATPolicyRuleAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the PolicyRule viewsets."""

    model = models.NATPolicyRule
    bulk_update_data = {"log": False}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_natpolicy_rule()
        src_addr = models.AddressObject.objects.first()
        dest_addr = models.AddressObject.objects.last()
        svc = models.ServiceObject.objects.first()
        models.NATPolicyRule.objects.create(name="deleteableobj1")
        models.NATPolicyRule.objects.create(name="deleteableobj2")
        models.NATPolicyRule.objects.create(name="deleteableobj3")
        cls.create_data = [
            {
                "original_source_addresses": [src_addr.id],
                "original_destination_addresses": [dest_addr.id],
                "translated_destination_addresses": [src_addr.id],
                "log": True,
                "original_destination_services": [svc.id],
                "name": "test rule",
            },
            {
                "original_source_addresses": [src_addr.id],
                "original_destination_addresses": [dest_addr.id],
                "translated_destination_addresses": [src_addr.id],
                "log": False,
                "original_destination_services": [svc.id],
                "name": "test rule",
            },
        ]


class NATPolicyAPIViewTest(IncludeM2MAPITestCaseMixin, APIViewTestCases.APIViewTestCase):
    """Test the Policy viewsets."""

    model = models.NATPolicy
    bulk_update_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_natpolicy()
        nat_pol_rule = models.NATPolicyRule.objects.first()
        models.NATPolicy.objects.create(name="deleteableobj1")
        models.NATPolicy.objects.create(name="deleteableobj2")
        models.NATPolicy.objects.create(name="deleteableobj3")

        cls.create_data = [
            {"name": "test 1", "nat_policy_rules": [nat_pol_rule.id]},
            {"name": "test 2", "nat_policy_rules": [nat_pol_rule.id], "description": "Test desc"},
        ]


###########################
# Through Models
###########################
class PolicyDeviceM2MAPIViewTest(APIViewTestCases.APIViewTestCase):
    """Test the PolicyDeviceM2M viewsets."""

    model = models.PolicyDeviceM2M
    bulk_update_data = {"weight": 1000}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.assign_policies()
        policy = models.Policy.objects.first()
        location = Location.objects.get(name="DFW02")
        dev_role = Role.objects.get(name="WAN")
        status = Status.objects.get(name="Active")
        platform = Platform.objects.get(name="Juniper")
        dev_type = DeviceType.objects.get(model="SRX300")
        dev1 = Device.objects.create(
            name="TEST-DEV-01",
            role=dev_role,
            device_type=dev_type,
            location=location,
            status=status,
            platform=platform,
        )
        dev2 = Device.objects.create(
            name="TEST-DEV-02",
            role=dev_role,
            device_type=dev_type,
            location=location,
            status=status,
            platform=platform,
        )

        cls.create_data = [
            {"device": dev1.id, "policy": policy.id, "weight": 100},
            {"device": dev2.id, "policy": policy.id, "weight": 200},
        ]


class ExpandedZonesAPITest(APITestCase):
    """Test that rules expose their zone groups expanded into zones over REST and GraphQL."""

    @classmethod
    def setUpTestData(cls):
        """Create a rule of each type with a zone and zone groups on both sides."""
        outside, inside, _ = fixtures.create_zone_group()
        wan = models.Zone.objects.get(name="WAN")
        band, _, _ = fixtures.create_policy_band()
        cls.policy_rule = models.PolicyRule.objects.create(
            rule_type="panos", name="expanded", action="allow", band=band, position="pre"
        )
        cls.policy_rule.source_zones.set([wan])
        cls.policy_rule.source_zone_groups.set([outside])
        cls.policy_rule.destination_zone_groups.set([inside])
        cls.nat_rule = models.NATPolicyRule.objects.create(name="expanded nat")
        cls.nat_rule.source_zone_groups.set([inside])
        cls.nat_rule.destination_zones.set([wan])

    def setUp(self):
        """Grant view access to the rules and zones."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.view_policyrule",
            "nautobot_firewall_models.view_natpolicyrule",
            "nautobot_firewall_models.view_zone",
            "nautobot_firewall_models.view_zonegroup",
        )

    def _get_names(self, route, obj, field):
        url = reverse(f"plugins-api:nautobot_firewall_models-api:{route}-detail", kwargs={"pk": obj.pk})
        response = self.client.get(f"{url}?exclude_m2m=false", **self.header)
        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        return [zone["name"] for zone in response.data[field]]

    def test_policy_rule_rest_expanded_zones(self):
        """The PolicyRule API returns the zones with zone groups expanded and duplicates removed."""
        self.assertEqual(self._get_names("policyrule", self.policy_rule, "expanded_source_zones"), ["WAN"])
        self.assertEqual(self._get_names("policyrule", self.policy_rule, "expanded_destination_zones"), ["DMZ", "LAN"])

    def test_nat_policy_rule_rest_expanded_zones(self):
        """The NATPolicyRule API returns the zones with zone groups expanded."""
        self.assertEqual(self._get_names("natpolicyrule", self.nat_rule, "expanded_source_zones"), ["DMZ", "LAN"])
        self.assertEqual(self._get_names("natpolicyrule", self.nat_rule, "expanded_destination_zones"), ["WAN"])

    def test_expanded_zones_are_read_only(self):
        """The expanded fields are ignored on write, so zones can only be changed through the real fields."""
        url = reverse("plugins-api:nautobot_firewall_models-api:policyrule-detail", kwargs={"pk": self.policy_rule.pk})
        self.add_permissions("nautobot_firewall_models.change_policyrule")
        lan = models.Zone.objects.get(name="LAN")
        response = self.client.patch(url, {"expanded_source_zones": [str(lan.pk)]}, format="json", **self.header)
        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        self.assertEqual(list(self.policy_rule.expanded_source_zones().values_list("name", flat=True)), ["WAN"])

    def test_graphql_expanded_zones(self):
        """GraphQL exposes the expanded zones on both rule types."""
        query = """
        query {
          policy_rules(name: "expanded") {
            source_zone_groups { name }
            expanded_source_zones { name }
            expanded_destination_zones { name }
          }
          nat_policy_rules(name: "expanded nat") {
            expanded_source_zones { name }
            expanded_destination_zones { name }
          }
        }
        """
        response = self.client.post(reverse("graphql-api"), {"query": query}, format="json", **self.header)
        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        self.assertNotIn("errors", response.data)
        rule = response.data["data"]["policy_rules"][0]
        self.assertEqual(rule["source_zone_groups"], [{"name": "outside"}])
        self.assertEqual(rule["expanded_source_zones"], [{"name": "WAN"}])
        self.assertEqual(rule["expanded_destination_zones"], [{"name": "DMZ"}, {"name": "LAN"}])
        nat_rule = response.data["data"]["nat_policy_rules"][0]
        self.assertEqual(nat_rule["expanded_source_zones"], [{"name": "DMZ"}, {"name": "LAN"}])
        self.assertEqual(nat_rule["expanded_destination_zones"], [{"name": "WAN"}])


class ZoneDevicesAPITest(APITestCase):
    """Test that a Zone can be bound to several Devices over REST and read back over GraphQL."""

    @classmethod
    def setUpTestData(cls):
        """Create firewalls to bind zones to."""
        fixtures.assign_policies()
        cls.devices = list(Device.objects.filter(name__in=["DFW02-WAN00", "HOU02-WAN00"]))

    def setUp(self):
        """Grant access to zones and devices."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_zone",
            "nautobot_firewall_models.view_zone",
            "dcim.view_device",
            "extras.view_status",
        )

    def test_create_zone_with_multiple_devices(self):
        """POSTing a Zone with two devices binds both, and the detail view returns them."""
        url = reverse("plugins-api:nautobot_firewall_models-api:zone-list")
        data = {
            "name": "shared",
            "status": Status.objects.get(name="Active").pk,
            "devices": [str(dev.pk) for dev in self.devices],
        }
        response = self.client.post(url, data, format="json", **self.header)
        self.assertHttpStatus(response, drf_status.HTTP_201_CREATED)
        zone = models.Zone.objects.get(name="shared")
        self.assertEqual(set(zone.devices.all()), set(self.devices))

        detail = reverse("plugins-api:nautobot_firewall_models-api:zone-detail", kwargs={"pk": zone.pk})
        response = self.client.get(f"{detail}?exclude_m2m=false", **self.header)
        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        self.assertEqual({dev["id"] for dev in response.data["devices"]}, {dev.pk for dev in self.devices})

    def test_graphql_zone_devices(self):
        """GraphQL lists each Zone's devices."""
        zone = models.Zone.objects.create(name="shared", status=Status.objects.get(name="Active"))
        zone.devices.set(self.devices)
        query = 'query { zones(name: "shared") { devices { name } } }'
        response = self.client.post(reverse("graphql-api"), {"query": query}, format="json", **self.header)
        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        self.assertNotIn("errors", response.data)
        names = sorted(dev["name"] for dev in response.data["data"]["zones"][0]["devices"])
        self.assertEqual(names, ["DFW02-WAN00", "HOU02-WAN00"])


class RuleTypeAPITest(APITestCase):
    """Test that the PolicyRule API applies the rule type checks."""

    @classmethod
    def setUpTestData(cls):
        """Create a band, a zone, a dynamic Address Object and a group that holds it."""
        cls.band, _, _ = fixtures.create_policy_band()
        cls.zone = models.Zone.objects.create(name="trust")
        cls.subnet = models.AddressObject.objects.create(name="host subnet", dynamic="subnet")
        cls.url = reverse("plugins-api:nautobot_firewall_models-api:policyrule-list")

    def setUp(self):
        """Grant access to Policy Rules."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_policyrule",
            "nautobot_firewall_models.change_policyrule",
            "nautobot_firewall_models.view_policyrule",
            "nautobot_firewall_models.view_addressobject",
            "nautobot_firewall_models.view_zone",
            "nautobot_firewall_models.view_policyband",
        )

    def _post(self, **data):
        return self.client.post(self.url, {"name": "rule", "action": "allow", **data}, format="json", **self.header)

    def test_create_nftables_rule_with_dynamic_address(self):
        """An nftables rule is created with a chain and a dynamic Address Object."""
        response = self._post(rule_type="nftables", chain="input", source_addresses=[str(self.subnet.pk)])

        self.assertHttpStatus(response, drf_status.HTTP_201_CREATED)
        self.assertEqual(response.data["rule_type"], "nftables")

    def test_nftables_rule_with_zone_is_refused(self):
        """Zones are refused on nftables rules."""
        response = self._post(rule_type="nftables", chain="input", source_zones=[str(self.zone.pk)])

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("source_zones", response.data)

    def test_panos_rule_with_dynamic_address_is_refused(self):
        """Host relative addresses are refused on PAN-OS rules."""
        response = self._post(
            rule_type="panos", band=str(self.band.pk), position="pre", destination_addresses=[str(self.subnet.pk)]
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("destination_addresses", response.data)

    def test_panos_rule_with_source_service_is_refused(self):
        """Source services are refused on PAN-OS rules."""
        service = models.ServiceObject.objects.create(name="ephemeral", port="1024-65535", ip_protocol="TCP")
        self.add_permissions("nautobot_firewall_models.view_serviceobject")
        response = self._post(
            rule_type="panos", band=str(self.band.pk), position="pre", source_services=[str(service.pk)]
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("source_services", response.data)

    def test_patch_keeps_saved_relations_in_the_check(self):
        """A PATCH that leaves zones out still sees the saved rule type."""
        rule = models.PolicyRule.objects.create(name="ssh", action="allow", rule_type="nftables", chain="input")
        url = reverse("plugins-api:nautobot_firewall_models-api:policyrule-detail", kwargs={"pk": rule.pk})

        response = self.client.patch(url, {"source_zones": [str(self.zone.pk)]}, format="json", **self.header)

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)

    def test_rule_type_can_not_change(self):
        """The rule type of a saved rule can not be changed."""
        rule = models.PolicyRule.objects.create(name="ssh", action="allow", rule_type="nftables", chain="input")
        url = reverse("plugins-api:nautobot_firewall_models-api:policyrule-detail", kwargs={"pk": rule.pk})

        response = self.client.patch(
            url,
            {"rule_type": "panos", "chain": "", "band": str(self.band.pk), "position": "pre"},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)


class HostRelativeAndPolicyTypeAPITest(APITestCase):
    """Test the REST API errors for host relative Address Objects and Policy rule types."""

    @classmethod
    def setUpTestData(cls):
        """Create a PAN-OS rule using a group, an nftables rule and a dynamic Address Object."""
        band, _, _ = fixtures.create_policy_band()
        cls.panos_rule = models.PolicyRule.objects.create(
            name="pan", action="allow", rule_type="panos", band=band, position="pre"
        )
        cls.nft_rule = models.PolicyRule.objects.create(name="nft", action="allow", rule_type="nftables", chain="input")
        cls.group = models.AddressObjectGroup.objects.create(name="panos group")
        cls.panos_rule.source_address_groups.add(cls.group)
        cls.subnet = models.AddressObject.objects.create(name="host subnet", dynamic="subnet")

    def setUp(self):
        """Grant access to Policies, NAT Policy Rules and Address Object Groups."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_policy",
            "nautobot_firewall_models.add_natpolicyrule",
            "nautobot_firewall_models.change_addressobjectgroup",
            "nautobot_firewall_models.view_addressobjectgroup",
            "nautobot_firewall_models.view_addressobject",
            "nautobot_firewall_models.view_policyrule",
        )

    def _url(self, route, pk=None):
        if pk:
            return reverse(f"plugins-api:nautobot_firewall_models-api:{route}-detail", kwargs={"pk": pk})
        return reverse(f"plugins-api:nautobot_firewall_models-api:{route}-list")

    def test_policy_refuses_rules_of_another_type(self):
        """Creating a PAN-OS Policy with an nftables rule is refused."""
        response = self.client.post(
            self._url("policy"),
            {"name": "mixed", "rule_type": "panos", "policy_rules": [str(self.nft_rule.pk)]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("policy_rules", response.data)

    def test_policy_requires_a_rule_type(self):
        """There is no default rule type on a Policy."""
        response = self.client.post(self._url("policy"), {"name": "untyped"}, format="json", **self.header)

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("rule_type", response.data)

    def test_nat_rule_refuses_host_relative_address(self):
        """Creating a NAT rule with a dynamic Address Object is refused."""
        response = self.client.post(
            self._url("natpolicyrule"),
            {"name": "nat", "original_source_addresses": [str(self.subnet.pk)]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("original_source_addresses", response.data)

    def test_nat_rule_refuses_source_service(self):
        """Creating a NAT rule with an original source service is refused."""
        service = models.ServiceObject.objects.create(name="ephemeral", port="1024-65535", ip_protocol="TCP")
        self.add_permissions("nautobot_firewall_models.view_serviceobject")
        response = self.client.post(
            self._url("natpolicyrule"),
            {"name": "nat", "original_source_services": [str(service.pk)]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("original_source_services", response.data)

    def test_group_used_by_panos_rule_refuses_host_relative_address(self):
        """Adding a dynamic Address Object to a group a PAN-OS rule uses is refused."""
        response = self.client.patch(
            self._url("addressobjectgroup", self.group.pk),
            {"address_objects": [str(self.subnet.pk)]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_objects", response.data)


class GroupedObjectsAPITest(APITestCase):
    """Test the API the combined pickers search: groups and objects together, limited to what the user may view."""

    @classmethod
    def setUpTestData(cls):
        """Create two Zone Groups and three Zones."""
        cls.groups = [models.ZoneGroup.objects.create(name=name) for name in ("inside", "outside")]
        cls.zones = [models.Zone.objects.create(name=name) for name in ("dmz", "trust", "untrust")]

    def setUp(self):
        """Grant view access to Zones and Zone Groups."""
        super().setUp()
        self.add_permissions("nautobot_firewall_models.view_zone", "nautobot_firewall_models.view_zonegroup")

    def _get(self, kind="zones", **params):
        url = reverse("plugins-api:nautobot_firewall_models-api:grouped-objects", kwargs={"kind": kind})
        return self.client.get(url, params, **self.header)

    def test_groups_come_before_objects_under_headings(self):
        """Groups are listed first, then objects, each under its own heading."""
        response = self._get()

        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 5)
        self.assertEqual(
            [(i["id"], i["group"]["name"]) for i in response.data["results"]],
            [(f"group:{i.pk}", "Zone Groups") for i in self.groups] + [(f"object:{i.pk}", "Zones") for i in self.zones],
        )

    def test_search(self):
        """The q parameter searches groups and objects."""
        response = self._get(q="out")

        self.assertEqual([i["name"] for i in response.data["results"]], ["outside"])

    def test_pages_across_groups_and_objects(self):
        """Paging treats the groups and objects as one list."""
        first = self._get(limit=3)
        second = self._get(limit=3, offset=3)

        self.assertEqual([i["name"] for i in first.data["results"]], ["inside", "outside", "dmz"])
        self.assertIsNotNone(first.data["next"])
        self.assertEqual([i["name"] for i in second.data["results"]], ["trust", "untrust"])
        self.assertIsNone(second.data["next"])

    def test_only_returns_what_the_user_may_view(self):
        """Without permission to view Zone Groups, only Zones are returned."""
        ObjectPermission.objects.filter(object_types__model="zonegroup").delete()

        response = self._get()

        self.assertEqual({i["group"]["name"] for i in response.data["results"]}, {"Zones"})

    def test_unknown_kind(self):
        """An unknown kind is not found."""
        self.assertHttpStatus(self._get(kind="nope"), drf_status.HTTP_404_NOT_FOUND)

    def test_every_kind_responds(self):
        """Every picker kind has a working search."""
        for kind in ("zones", "addresses", "services", "users", "applications"):
            self.assertHttpStatus(self._get(kind=kind), drf_status.HTTP_200_OK)


class ManagedLocallyAPITest(APITestCase):
    """Test the REST API errors for Managed Locally groups."""

    @classmethod
    def setUpTestData(cls):
        """Create a group with a member and a Managed Locally status."""
        cls.managed = Status.objects.get(name="Managed Locally")
        cls.member = models.ServiceObject.objects.create(name="HTTPS", port="443", ip_protocol="TCP")
        cls.group = models.ServiceObjectGroup.objects.create(name="web")
        cls.group.service_objects.add(cls.member)

    def setUp(self):
        """Grant access to Service Object Groups."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_serviceobjectgroup",
            "nautobot_firewall_models.change_serviceobjectgroup",
            "nautobot_firewall_models.view_serviceobjectgroup",
            "nautobot_firewall_models.view_serviceobject",
            "extras.view_status",
        )

    def _url(self, pk=None):
        if pk:
            return reverse("plugins-api:nautobot_firewall_models-api:serviceobjectgroup-detail", kwargs={"pk": pk})
        return reverse("plugins-api:nautobot_firewall_models-api:serviceobjectgroup-list")

    def test_create_managed_locally_group_with_members_is_refused(self):
        """A new Managed Locally group with members is refused."""
        response = self.client.post(
            self._url(),
            {"name": "local", "status": str(self.managed.pk), "service_objects": [str(self.member.pk)]},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("service_objects", response.data)

    def test_marking_a_group_with_members_managed_locally_is_refused(self):
        """Changing a group that still has members to Managed Locally is refused."""
        response = self.client.patch(
            self._url(self.group.pk), {"status": str(self.managed.pk)}, format="json", **self.header
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)

    def test_marking_an_emptied_group_managed_locally(self):
        """Clearing the members and marking the group Managed Locally in one request works."""
        response = self.client.patch(
            self._url(self.group.pk),
            {"status": str(self.managed.pk), "service_objects": []},
            format="json",
            **self.header,
        )

        self.assertHttpStatus(response, drf_status.HTTP_200_OK)


class RenderedAddressesAPITest(APITestCase):
    """Test that rules expose their rendered addresses over REST and GraphQL."""

    @classmethod
    def setUpTestData(cls):
        """Create a rule whose source uses a flattened group of two countries."""
        managed = Status.objects.get(name="Managed Locally")
        countries = models.AddressObjectGroup.objects.create(name="High Risk Countries", flatten=True)
        countries.address_objects.set(
            [models.AddressObject.objects.create(name=name, status=managed) for name in ("CN", "RU")]
        )
        band, _, _ = fixtures.create_policy_band()
        cls.rule = models.PolicyRule.objects.create(
            name="block countries", action="deny", rule_type="panos", band=band, position="pre"
        )
        cls.rule.source_address_groups.set([countries])

    def setUp(self):
        """Grant view access to rules and addresses."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.view_policyrule",
            "nautobot_firewall_models.view_addressobject",
            "nautobot_firewall_models.view_addressobjectgroup",
        )

    def test_rest_rendered_addresses(self):
        """The REST API lists the flattened group's members and leaves the group out."""
        url = reverse("plugins-api:nautobot_firewall_models-api:policyrule-detail", kwargs={"pk": self.rule.pk})
        response = self.client.get(f"{url}?exclude_m2m=false", **self.header)

        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        self.assertEqual([i["name"] for i in response.data["rendered_source_addresses"]], ["CN", "RU"])
        self.assertEqual(response.data["rendered_source_address_groups"], [])

    def test_graphql_rendered_addresses(self):
        """GraphQL exposes the same rendered addresses."""
        query = (
            '{ policy_rules(name: "block countries") '
            "{ rendered_source_addresses { name } rendered_source_address_groups { name } } }"
        )
        response = self.client.post(reverse("graphql-api"), {"query": query}, format="json", **self.header)

        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        rule = response.data["data"]["policy_rules"][0]
        self.assertEqual([i["name"] for i in rule["rendered_source_addresses"]], ["CN", "RU"])
        self.assertEqual(rule["rendered_source_address_groups"], [])


class NestedAddressGroupAPITest(APITestCase):
    """Test nested Address Object Groups over the REST API."""

    def setUp(self):
        """Grant access to Address Object Groups."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_addressobjectgroup",
            "nautobot_firewall_models.change_addressobjectgroup",
            "nautobot_firewall_models.view_addressobjectgroup",
        )
        self.parent = models.AddressObjectGroup.objects.create(name="parent")
        self.child = models.AddressObjectGroup.objects.create(name="child")

    def _url(self, pk=None):
        if pk:
            return reverse("plugins-api:nautobot_firewall_models-api:addressobjectgroup-detail", kwargs={"pk": pk})
        return reverse("plugins-api:nautobot_firewall_models-api:addressobjectgroup-list")

    def test_create_group_with_nested_group(self):
        """A group can be created holding another group."""
        response = self.client.post(
            self._url(), {"name": "new", "address_object_groups": [str(self.child.pk)]}, format="json", **self.header
        )

        self.assertHttpStatus(response, drf_status.HTTP_201_CREATED)
        self.assertEqual(
            list(models.AddressObjectGroup.objects.get(name="new").address_object_groups.all()), [self.child]
        )

    def test_loop_is_refused(self):
        """Nesting a group inside one of its own nested groups is refused."""
        self.parent.address_object_groups.add(self.child)
        response = self.client.patch(
            self._url(self.child.pk), {"address_object_groups": [str(self.parent.pk)]}, format="json", **self.header
        )

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("address_object_groups", response.data)


class ZoneVirtualMachineAPITest(APITestCase):
    """Test binding Zones to Virtual Machines over the REST API and the picker search."""

    def setUp(self):
        """Grant access to Zones, Devices and Virtual Machines."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_zone",
            "nautobot_firewall_models.view_zone",
            "dcim.view_device",
            "virtualization.view_virtualmachine",
        )
        self.vm = fixtures.create_virtual_machine()

    def test_create_zone_with_virtual_machine(self):
        """A Zone can be created bound to a Virtual Machine, and filtered by it."""
        url = reverse("plugins-api:nautobot_firewall_models-api:zone-list")
        response = self.client.post(
            url, {"name": "vm zone", "virtual_machines": [str(self.vm.pk)]}, format="json", **self.header
        )

        self.assertHttpStatus(response, drf_status.HTTP_201_CREATED)
        response = self.client.get(f"{url}?virtual_machines={self.vm.name}", **self.header)
        self.assertEqual([i["name"] for i in response.data["results"]], ["vm zone"])

    def test_picker_search_lists_devices_then_virtual_machines(self):
        """The devices search lists Devices, then Virtual Machines, under their own headings."""
        fixtures.create_sample_env()
        url = reverse("plugins-api:nautobot_firewall_models-api:grouped-objects", kwargs={"kind": "devices"})
        response = self.client.get(url, {"limit": 1000}, **self.header)

        self.assertHttpStatus(response, drf_status.HTTP_200_OK)
        headings = [i["group"]["name"] for i in response.data["results"]]
        self.assertEqual(headings[-1], "Virtual Machines")
        self.assertEqual(set(headings), {"Devices", "Virtual Machines"})
        self.assertIn(
            {"id": f"group:{self.vm.pk}", "name": "vm01", "display": "vm01", "group": {"name": "Virtual Machines"}},
            response.data["results"],
        )


class FinalPositionAPITest(APITestCase):
    """Test the Final position over the REST API."""

    def setUp(self):
        """Grant access to Policy Rules and bands."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_policyrule",
            "nautobot_firewall_models.view_policyrule",
            "nautobot_firewall_models.view_policyband",
        )
        self.band, _, _ = fixtures.create_policy_band()
        self.url = reverse("plugins-api:nautobot_firewall_models-api:policyrule-list")

    def _post(self, **data):
        body = {"rule_type": "panos", "band": str(self.band.pk), "position": "final", "action": "deny", **data}
        return self.client.post(self.url, body, format="json", **self.header)

    def test_band_can_have_several_final_rules(self):
        """The API accepts more than one Final rule in a band."""
        self.assertHttpStatus(self._post(name="final"), drf_status.HTTP_201_CREATED)
        self.assertHttpStatus(self._post(name="second", action="drop"), drf_status.HTTP_201_CREATED)

    def test_final_rule_that_allows_is_refused(self):
        """The API refuses a Final rule that allows."""
        response = self._post(name="final", action="allow")

        self.assertHttpStatus(response, drf_status.HTTP_400_BAD_REQUEST)
        self.assertIn("action", response.data)
