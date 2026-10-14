"""Test Firewall models."""

# ruff: noqa: F403, F405
# pylint: disable=invalid-name
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import ProtectedError
from django.test import TestCase
from nautobot.dcim.models import Device
from nautobot.extras.models import Status
from nautobot.ipam.models import VRF

from nautobot_firewall_models.models import *  # pylint: disable=unused-wildcard-import, wildcard-import

from . import fixtures


class TestModels(TestCase):
    """Test models."""

    def setUp(self) -> None:
        """Setup test data."""
        self.vrf = VRF.objects.create(name="Development")

    def test_create_iprange_only_required(self):
        """Create IPRange with only required fields, and validate null description and __str__."""
        iprange = IPRange.objects.create(start_address="10.0.0.1", end_address="10.0.0.5")

        self.assertEqual(iprange.start_address, "10.0.0.1")
        self.assertEqual(iprange.end_address, "10.0.0.5")
        self.assertEqual(iprange.description, "")
        self.assertEqual(str(iprange), "10.0.0.1-10.0.0.5")
        self.assertEqual(iprange.vrf, None)
        self.assertEqual(iprange.size, 5)

    def test_create_iprange_all_fields_success(self):
        """Create IPRange with all fields."""
        iprange = IPRange.objects.create(
            start_address="10.0.0.1", end_address="10.0.0.5", description="Development", vrf=self.vrf
        )

        self.assertEqual(iprange.start_address, "10.0.0.1")
        self.assertEqual(iprange.end_address, "10.0.0.5")
        self.assertEqual(iprange.description, "Development")
        self.assertEqual(str(iprange), "10.0.0.1-10.0.0.5")
        self.assertEqual(iprange.vrf, self.vrf)
        self.assertEqual(iprange.size, 5)

    def test_iprange_missing_required_attr(self):
        """Test missing start_address."""
        with self.assertRaises(ValidationError):
            IPRange.objects.create(end_address="10.0.0.5", description="Development", vrf=self.vrf)

    def test_iprange_invalid_range(self):
        """Test missing start_address."""
        with self.assertRaises(ValidationError):
            IPRange.objects.create(
                start_address="10.0.0.15", end_address="10.0.0.5", description="Development", vrf=self.vrf
            )

    def test_create_zone_only_required(self):
        """Create Zone with only required fields, and validate null description and __str__."""
        zone = Zone.objects.create(name="trust")

        self.assertEqual(zone.description, "")
        self.assertEqual(zone.name, "trust")
        self.assertEqual(zone.interfaces.count(), 0)
        self.assertEqual(zone.vrfs.count(), 0)

    def test_create_zone_vrf_description_fields_success(self):
        """Create Zone with vrf & description fields."""
        zone = Zone.objects.create(name="trust", description="LAN Zone")
        zone.vrfs.add(self.vrf)

        self.assertEqual(zone.description, "LAN Zone")
        self.assertEqual(zone.name, "trust")
        self.assertEqual(zone.interfaces.count(), 0)
        self.assertEqual(zone.vrfs.first(), self.vrf)

    def test_zone_bound_to_multiple_devices(self):
        """A Zone can be bound to several Devices and each Device lists its Zones."""
        wan, lan = fixtures.bind_zone_devices()
        dfw = Device.objects.get(name="DFW02-WAN00")

        self.assertEqual(
            sorted(wan.devices.values_list("name", flat=True)),
            ["DFW02-WAN00", "HOU02-WAN00"],
        )
        self.assertEqual(sorted(dfw.zones.values_list("name", flat=True)), sorted([wan.name, lan.name]))

    def test_address_object_too_many_objects(self):
        """Tests to make sure only one address can be on an address object."""
        fqdn = FQDN.objects.create(name="test.local")
        iprange = IPRange.objects.create(start_address="10.0.0.1", end_address="10.0.0.5")

        with self.assertRaises(ValidationError):
            AddressObject.objects.create(name="failure", fqdn=fqdn, ip_range=iprange)

    def test_create_protocol_only_required(self):
        """Creates a protocol with only required fields."""
        protocol = ServiceObject.objects.create(
            name="HTTPS", port="8443", ip_protocol="TCP", status=Status.objects.get(name="Active")
        )

        self.assertEqual(protocol.description, "")
        self.assertEqual(protocol.name, "HTTPS")
        self.assertEqual(protocol.port, "8443")
        self.assertEqual(str(protocol), "HTTPS (TCP/8443)")

    def test_create_protocol_all_fields(self):
        """Creates a protocol with all fields."""
        protocol = ServiceObject.objects.create(
            name="HTTPS",
            port="8443",
            ip_protocol="TCP",
            status=Status.objects.get(name="Active"),
            description="Encrypted HTTP traffic",
        )

        self.assertEqual(protocol.description, "Encrypted HTTP traffic")
        self.assertEqual(protocol.name, "HTTPS")
        self.assertEqual(protocol.port, "8443")
        self.assertEqual(str(protocol), "HTTPS (TCP/8443)")

    def test_create_service_group_only_required(self):
        """Creates a service group with only required fields."""
        protocol = ServiceObject.objects.create(
            name="HTTPS", port="8443", ip_protocol="TCP", status=Status.objects.get(name="Active")
        )
        serv_grp = ServiceObjectGroup.objects.create(name="Web")
        serv_grp.service_objects.add(protocol)

        self.assertEqual(serv_grp.description, "")
        self.assertEqual(serv_grp.name, "Web")
        self.assertEqual(serv_grp.service_objects.first(), protocol)
        self.assertEqual(str(serv_grp), "Web")

    def test_create_service_group_all_fields(self):
        """Creates a service group with all fields."""
        protocol = ServiceObject.objects.create(
            name="HTTPS", port="8443", ip_protocol="TCP", status=Status.objects.get(name="Active")
        )
        serv_grp = ServiceObjectGroup.objects.create(name="Web", description="Web protocols")
        serv_grp.service_objects.add(protocol)

        self.assertEqual(serv_grp.description, "Web protocols")
        self.assertEqual(serv_grp.name, "Web")
        self.assertEqual(serv_grp.service_objects.first(), protocol)
        self.assertEqual(str(serv_grp), "Web")

    def test_create_user_only_required(self):
        """Creates a user with only required fields."""
        user = UserObject.objects.create(username="user123")

        self.assertEqual(user.username, "user123")
        self.assertEqual(user.name, "")
        self.assertEqual(str(user), "user123")

    def test_create_user_all_fields(self):
        """Creates a user with all fields."""
        user = UserObject.objects.create(username="user123", name="Foo Bar User")

        self.assertEqual(user.username, "user123")
        self.assertEqual(user.name, "Foo Bar User")
        self.assertEqual(str(user), "user123")

    def test_create_user_group_only_required(self):
        """Creates a user group with only required fields."""
        user = UserObject.objects.create(username="user123")
        user_group = UserObjectGroup.objects.create(name="group1")
        user_group.user_objects.add(user)

        self.assertEqual(user_group.description, "")
        self.assertEqual(user_group.name, "group1")
        self.assertEqual(user_group.user_objects.first(), user)
        self.assertEqual(str(user_group), "group1")

    def test_create_user_group_all_fields(self):
        """Creates a user group with all fields."""
        user = UserObject.objects.create(username="user123", name="Foo Bar User")
        user_group = UserObjectGroup.objects.create(name="group1", description="Test group 1.")
        user_group.user_objects.add(user)

        self.assertEqual(user_group.description, "Test group 1.")
        self.assertEqual(user_group.name, "group1")
        self.assertEqual(user_group.user_objects.first(), user)
        self.assertEqual(str(user_group), "group1")

    def test_create_fqdn_only_required(self):
        """Creates a fqdn with only required fields."""
        fqdn = FQDN.objects.create(name="test.local")

        self.assertEqual(fqdn.description, "")
        self.assertEqual(fqdn.name, "test.local")

    def test_create_fqdn_all_fields(self):
        """Creates a fqdn with all fields."""
        fqdn = FQDN.objects.create(name="test.local", description="test domain")

        self.assertEqual(fqdn.description, "test domain")
        self.assertEqual(fqdn.name, "test.local")


class TestServiceObject(TestCase):
    """Test ServiceObjects."""

    def test_service_port(self):
        """Test single port."""
        svc = ServiceObject.objects.create(
            name="HTTP", port="8088", ip_protocol="TCP", status=Status.objects.get(name="Active")
        )

        self.assertEqual(svc.port, "8088")

    def test_service_port_range(self):
        """Test port range."""
        svc = ServiceObject.objects.create(
            name="HTTP", port="8080-8088", ip_protocol="TCP", status=Status.objects.get(name="Active")
        )

        self.assertEqual(svc.port, "8080-8088")

    def test_service_port_empty(self):
        """Test port empty string."""
        svc = ServiceObject.objects.create(
            name="HTTP", port="", ip_protocol="TCP", status=Status.objects.get(name="Active")
        )

        self.assertEqual(svc.port, "")

    def test_service_port_omitted_equals_blank(self):
        """Test port blank."""
        svc = ServiceObject.objects.create(name="HTTP", ip_protocol="TCP", status=Status.objects.get(name="Active"))

        self.assertEqual(svc.port, "")

    def test_service_port_range_invalid(self):
        """Test port range."""
        with self.assertRaises(ValidationError):
            ServiceObject.objects.create(
                name="HTTP", port="8080-8088-999", ip_protocol="TCP", status=Status.objects.get(name="Active")
            )


class TestPolicyRuleModels(TestCase):
    """Test the PolicyRule model."""

    def setUp(self) -> None:
        """Create the data."""
        fixtures.create_policy_rule()

    def test_policyrule_rule_details(self):
        """Test method rule_details on PolicyRule model."""
        rule_details = PolicyRule.objects.first().rule_details()
        self.assertEqual(rule_details["log"], True)
        # sample a few keys to ensure they are in there, more complete test in to_json test
        keys = ["rule", "source_address_groups", "destination_address_groups", "action"]
        self.assertTrue(set(keys).issubset(rule_details.keys()))

    def test_policyrule_to_json(self):
        """Test method to_json on PolicyRule model."""
        obj = PolicyRule.objects.first()
        json_details = obj.to_json()
        self.assertEqual(json_details["display"], "Policy Rule 1 - req1")
        self.assertTrue(obj.source_users.filter(id=json_details["source_users"][0]["id"]).exists())
        self.assertTrue(obj.source_user_groups.filter(id=json_details["source_user_groups"][0]["id"]).exists())
        self.assertTrue(obj.source_addresses.filter(id=json_details["source_addresses"][0]["id"]).exists())
        self.assertTrue(obj.source_address_groups.filter(id=json_details["source_address_groups"][0]["id"]).exists())
        self.assertTrue(obj.destination_services.filter(id=json_details["destination_services"][0]["id"]).exists())


class TestPolicyModels(TestCase):
    """Test the Policy model."""

    def setUp(self) -> None:
        """Create the data."""
        fixtures.create_policy()

    def test_policy_policy_details(self):
        """Test method policy_details on Policy model."""
        policy_details = Policy.objects.first().policy_details[0]
        self.assertEqual(policy_details["log"], True)
        # sample a few keys to ensure they are in there, more complete test in to_json test
        keys = ["rule", "source_address_groups", "destination_address_groups", "action"]
        self.assertTrue(set(keys).issubset(policy_details.keys()))

    def test_policy_to_json(self):
        """Test method to_json on Policy model."""
        obj = Policy.objects.all()[2]
        json_details = obj.to_json()["policy_rules"][2]
        self.assertTrue(obj.policy_rules.filter(id=json_details["id"]).exists())


class TestNATPolicyRuleModels(TestCase):
    """Test the NATPolicyRule model."""

    def setUp(self) -> None:
        """Create the data."""
        fixtures.create_natpolicy_rule()

    def test_natpolicyrule_rule_details(self):
        """Test method rule_details on NATPolicyRule model."""
        rule_details = NATPolicyRule.objects.first().rule_details()
        self.assertEqual(rule_details["log"], True)
        # sample a few keys to ensure they are in there, more complete test in to_json test
        keys = ["rule", "original_source_address_groups", "translated_destination_address_groups", "remark"]
        self.assertTrue(set(keys).issubset(rule_details.keys()))

    def test_natpolicyrule_to_json(self):
        """Test method to_json on NATPolicyRule model."""
        obj = NATPolicyRule.objects.first()
        json_details = obj.to_json()
        self.assertEqual(json_details["display"], "NAT Policy Rule 1.1 - req1")
        self.assertTrue(
            obj.original_destination_services.filter(id=json_details["original_destination_services"][0]["id"]).exists()
        )
        self.assertTrue(
            obj.translated_destination_services.filter(
                id=json_details["translated_destination_services"][0]["id"]
            ).exists()
        )


class TestNATPolicyModels(TestCase):
    """Test the NATPolicy model."""

    def setUp(self) -> None:
        """Create the data."""
        fixtures.create_natpolicy()

    def test_policy_policy_details(self):
        """Test method policy_details on Policy model."""
        policy_details = NATPolicy.objects.first().policy_details[0]
        self.assertEqual(policy_details["log"], True)
        # sample a few keys to ensure they are in there, more complete test in to_json test
        keys = ["rule", "original_source_address_groups", "original_destination_address_groups", "remark"]
        self.assertTrue(set(keys).issubset(policy_details.keys()))

    def test_policy_to_json(self):
        """Test method to_json on Policy model."""
        obj = NATPolicyRule.objects.first()
        json_details = obj.to_json()
        self.assertEqual(json_details["name"], "NAT Policy Rule 1.1")
        self.assertTrue(
            obj.original_destination_services.filter(id=json_details["original_destination_services"][0]["id"]).exists()
        )
        self.assertTrue(
            obj.translated_destination_services.filter(
                id=json_details["translated_destination_services"][0]["id"]
            ).exists()
        )


class TestZoneGroupModels(TestCase):
    """Test the ZoneGroup model and how rules expand it."""

    def setUp(self) -> None:
        """Create the data."""
        self.outside, self.inside, self.everything = fixtures.create_zone_group()
        self.wan = Zone.objects.get(name="WAN")
        self.lan = Zone.objects.get(name="LAN")
        self.dmz = Zone.objects.get(name="DMZ")
        self.band, _, _ = fixtures.create_policy_band()

    def test_create_zone_group_only_required(self):
        """Create ZoneGroup with only required fields, and validate null description and __str__."""
        zone_group = ZoneGroup.objects.create(name="empty")

        self.assertEqual(zone_group.description, "")
        self.assertEqual(str(zone_group), "empty")
        self.assertEqual(zone_group.zones.count(), 0)

    def test_zone_group_reverse_relation(self):
        """A Zone lists every ZoneGroup it belongs to."""
        self.assertEqual(set(self.lan.zone_groups.all()), {self.inside, self.everything})

    def test_policy_rule_expanded_zones_without_zones(self):
        """A rule with no zones or zone groups expands to nothing (implicit any)."""
        rule = PolicyRule.objects.create(
            rule_type="panos", name="no zones", action="allow", band=self.band, position="header"
        )

        self.assertEqual(list(rule.expanded_source_zones()), [])
        self.assertEqual(list(rule.expanded_destination_zones()), [])

    def test_policy_rule_expanded_zones(self):
        """Zones set directly and zones reached through groups are combined without duplicates."""
        rule = PolicyRule.objects.create(
            rule_type="panos", name="zone groups", action="allow", band=self.band, position="header"
        )
        rule.source_zones.set([self.wan])
        rule.source_zone_groups.set([self.outside, self.inside])
        rule.destination_zone_groups.set([self.inside, self.everything])

        self.assertEqual(list(rule.expanded_source_zones()), [self.dmz, self.lan, self.wan])
        self.assertEqual(list(rule.expanded_destination_zones()), [self.dmz, self.lan, self.wan])

    def test_policy_rule_expanded_zones_reflects_group_changes(self):
        """Expansion is evaluated on demand, so later group membership changes are picked up."""
        rule = PolicyRule.objects.create(
            rule_type="panos", name="late change", action="allow", band=self.band, position="header"
        )
        rule.source_zone_groups.set([self.outside])
        self.assertEqual(list(rule.expanded_source_zones()), [self.wan])

        self.outside.zones.add(self.dmz)
        self.assertEqual(list(rule.expanded_source_zones()), [self.dmz, self.wan])

    def test_nat_policy_rule_expanded_zones(self):
        """NAT rules expand zone groups the same way as security rules."""
        rule = NATPolicyRule.objects.create(name="nat zone groups")
        rule.source_zone_groups.set([self.inside])
        rule.destination_zones.set([self.wan])

        self.assertEqual(list(rule.expanded_source_zones()), [self.dmz, self.lan])
        self.assertEqual(list(rule.expanded_destination_zones()), [self.wan])

    def test_rule_details_include_zone_groups(self):
        """rule_details exposes both the zones and the zone groups on each side."""
        rule = PolicyRule.objects.create(
            rule_type="panos", name="details", action="allow", band=self.band, position="header"
        )
        rule.source_zone_groups.set([self.inside])
        details = rule.rule_details()

        self.assertEqual(list(details["source_zone_groups"]), [self.inside])
        self.assertEqual(list(details["source_zones"]), [])
        self.assertTrue({"destination_zones", "destination_zone_groups"}.issubset(details.keys()))

    def test_zone_group_delete_protected_when_used_by_rule(self):
        """A ZoneGroup assigned to a rule can not be deleted while protect_on_delete is enabled."""
        rule = PolicyRule.objects.create(
            rule_type="panos", name="protected", action="allow", band=self.band, position="header"
        )
        rule.destination_zone_groups.set([self.outside])

        with self.assertRaises(ValidationError):
            self.outside.delete()

    def test_zone_delete_protected_when_in_zone_group(self):
        """A Zone that belongs to a ZoneGroup can not be deleted while protect_on_delete is enabled."""
        with self.assertRaises(ValidationError):
            self.dmz.delete()


class TestPolicyBandModels(TestCase):
    """Test the PolicyBand model and how it orders Policy Rules."""

    def setUp(self) -> None:
        """Create the data."""
        self.global_deny, self.universal, self.medium_trust = fixtures.create_policy_band()

    def _rule(self, name, band, position, index=None):
        return PolicyRule.objects.create(
            rule_type="panos", name=name, action="allow", band=band, position=position, index=index
        )

    def test_create_policy_band_only_required(self):
        """Create PolicyBand with only required fields, and validate null description and __str__."""
        band = PolicyBand.objects.create(name="Exceptions", index=5)

        self.assertEqual(band.description, "")
        self.assertEqual(str(band), "Exceptions")

    def test_bands_ordered_by_index(self):
        """Bands sort by index, not name."""
        self.assertEqual(list(PolicyBand.objects.all()), [self.global_deny, self.universal, self.medium_trust])

    def test_rules_ordered_by_band_before_rule_index(self):
        """A rule in an earlier band comes first even with a higher rule index."""
        late = self._rule("late", self.medium_trust, "header", index=1)
        early = self._rule("early", self.global_deny, "header", index=99)

        self.assertEqual(list(PolicyRule.objects.all()), [early, late])

    def test_header_rules_come_before_closer_rules(self):
        """Within a band, every Header rule comes before every Closer rule regardless of index."""
        closer = self._rule("closer", self.universal, "closer", index=1)
        header = self._rule("header", self.universal, "header", index=50)

        self.assertEqual(list(PolicyRule.objects.all()), [header, closer])

    def test_rules_without_index_come_last_within_position(self):
        """Rules with no index sort after indexed rules in the same band and position."""
        unindexed = self._rule("a unindexed", self.universal, "header")
        indexed = self._rule("z indexed", self.universal, "header", index=10)

        self.assertEqual(list(PolicyRule.objects.all()), [indexed, unindexed])

    def test_rules_sharing_an_index_are_ordered_by_name(self):
        """Rules may share an index, and break the tie by name so the order is stable."""
        second = self._rule("Block B", self.global_deny, "header", index=10)
        first = self._rule("Block A", self.global_deny, "header", index=10)

        self.assertEqual(list(PolicyRule.objects.all()), [first, second])

    def test_band_with_rules_can_not_be_deleted(self):
        """A PolicyBand that still has rules is protected from deletion."""
        self._rule("protected", self.universal, "header")

        with self.assertRaises(ProtectedError):
            self.universal.delete()

    def test_rule_details_include_band_and_position(self):
        """rule_details exposes the rule's band and position."""
        details = self._rule("details", self.universal, "closer").rule_details()

        self.assertEqual(details["band"], self.universal)
        self.assertEqual(details["position"], "closer")


class TestHostRelativeAddressObjects(TestCase):
    """Test Address Objects that resolve per host: a Device reference and the dynamic Subnet."""

    def setUp(self) -> None:
        """Create a host to render for and a second host to reference."""
        self.host = fixtures.create_linux_host("web01", "10.0.0.10")
        self.db = fixtures.create_linux_host("db01", "10.0.0.20")

    def test_dynamic_subnet_is_a_complete_address(self):
        """A dynamic value on its own satisfies the one address rule."""
        obj = AddressObject.objects.create(name="host subnet", dynamic="subnet")

        self.assertEqual(obj.get_address_info(), ("dynamic", "subnet"))
        self.assertTrue(obj.is_host_relative)

    def test_device_and_prefix_together_are_refused(self):
        """A Device counts as an address, so it can not be combined with another one."""
        prefix = self.host.primary_ip4.parent
        with self.assertRaises(ValidationError):
            AddressObject.objects.create(name="both", device=self.db, prefix=prefix)

    def test_subnet_resolves_to_the_prefix_of_the_host(self):
        """Subnet becomes the Prefix that holds the primary IP of the host being rendered."""
        obj = AddressObject.objects.create(name="host subnet", dynamic="subnet")

        self.assertEqual([str(i) for i in obj.resolve(self.host)], ["10.0.0.0/24"])

    def test_device_resolves_to_its_primary_ip(self):
        """A Device reference becomes that Device's primary IP, whichever host the rule is rendered for."""
        obj = AddressObject.objects.create(name="db01", device=self.db)

        self.assertEqual([str(i) for i in obj.resolve(self.host)], ["10.0.0.20/32"])

    def test_subnet_without_primary_ip_is_refused(self):
        """A host with no primary IP has no subnet to resolve to."""
        obj = AddressObject.objects.create(name="host subnet", dynamic="subnet")
        self.host.primary_ip4 = None
        self.host.save()

        with self.assertRaises(ValidationError):
            obj.resolve(self.host)

    def test_static_object_is_not_host_relative(self):
        """Ordinary Address Objects already hold their value."""
        obj = AddressObject.objects.create(name="subnet", prefix=self.host.primary_ip4.parent)

        self.assertFalse(obj.is_host_relative)

    def test_device_with_address_objects_can_not_be_deleted(self):
        """A Device referenced by an Address Object is protected from deletion."""
        AddressObject.objects.create(name="db01", device=self.db)

        with self.assertRaises((ProtectedError, ValidationError)):
            self.db.delete()


class TestRuleTypes(TestCase):
    """Test that PAN-OS and nftables rules require and refuse the right fields."""

    def setUp(self) -> None:
        """Create a band, a zone and a dynamic Address Object."""
        self.band, _, _ = fixtures.create_policy_band()
        self.zone = Zone.objects.create(name="trust")
        self.subnet = AddressObject.objects.create(name="host subnet", dynamic="subnet")

    def test_rule_type_is_required(self):
        """There is no default rule type."""
        with self.assertRaises(ValidationError) as ctx:
            PolicyRule(name="no type", action="allow").full_clean()
        self.assertIn("rule_type", ctx.exception.message_dict)

    def test_panos_needs_band_and_position(self):
        """A PAN-OS rule without a band or position is refused."""
        with self.assertRaises(ValidationError) as ctx:
            PolicyRule(name="no band", action="allow", rule_type="panos").full_clean()
        self.assertIn("band", ctx.exception.message_dict)
        self.assertIn("position", ctx.exception.message_dict)

    def test_nftables_needs_a_chain(self):
        """An nftables rule without a chain is refused."""
        with self.assertRaises(ValidationError) as ctx:
            PolicyRule(name="no chain", action="allow", rule_type="nftables").full_clean()
        self.assertIn("chain", ctx.exception.message_dict)

    def test_nftables_refuses_band_position_and_remark(self):
        """Bands, positions and remarks are PAN-OS concepts."""
        rule = PolicyRule(
            name="mixed", action="remark", rule_type="nftables", chain="input", band=self.band, position="header"
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertEqual(set(ctx.exception.message_dict), {"band", "position", "action"})

    def test_panos_refuses_a_chain(self):
        """Chains are an nftables concept."""
        rule = PolicyRule(
            rule_type="panos", name="chain", action="allow", band=self.band, position="header", chain="input"
        )
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertIn("chain", ctx.exception.message_dict)

    def test_valid_nftables_rule(self):
        """An nftables rule needs only a chain on top of the usual fields."""
        rule = PolicyRule(name="ssh", action="allow", rule_type="nftables", chain="input")
        rule.full_clean()

    def test_rule_type_can_not_change(self):
        """A saved rule keeps its type."""
        rule = PolicyRule.objects.create(name="ssh", action="allow", rule_type="nftables", chain="input")
        rule.rule_type = "panos"
        rule.chain = ""
        rule.band = self.band
        rule.position = "header"
        with self.assertRaises(ValidationError) as ctx:
            rule.full_clean()
        self.assertIn("rule_type", ctx.exception.message_dict)

    def test_nftables_refuses_zones(self):
        """Zones, users and applications only exist on PAN-OS."""
        with self.assertRaises(ValidationError) as ctx:
            PolicyRule.validate_relations("nftables", {"source_zones": [self.zone]})
        self.assertIn("source_zones", ctx.exception.message_dict)

    def test_nftables_accepts_host_relative_addresses(self):
        """nftables rules may use Device and dynamic Address Objects."""
        PolicyRule.validate_relations("nftables", {"source_addresses": [self.subnet]})

    def test_panos_refuses_host_relative_addresses(self):
        """A PAN-OS rule can not use an address that only resolves per host."""
        with self.assertRaises(ValidationError) as ctx:
            PolicyRule.validate_relations("panos", {"destination_addresses": [self.subnet]})
        self.assertIn("destination_addresses", ctx.exception.message_dict)

    def test_panos_refuses_groups_holding_host_relative_addresses(self):
        """The check looks inside Address Object Groups too."""
        group = AddressObjectGroup.objects.create(name="mixed")
        group.address_objects.set([self.subnet])
        with self.assertRaises(ValidationError) as ctx:
            PolicyRule.validate_relations("panos", {"source_address_groups": [group]})
        self.assertIn("source_address_groups", ctx.exception.message_dict)

    def test_nftables_rules_sort_after_panos_rules_by_chain_then_index(self):
        """Rules without a band sort last, then by chain and index."""
        output = PolicyRule.objects.create(name="out", action="allow", rule_type="nftables", chain="output", index=1)
        second = PolicyRule.objects.create(name="b", action="allow", rule_type="nftables", chain="input", index=2)
        first = PolicyRule.objects.create(name="a", action="allow", rule_type="nftables", chain="input", index=1)
        panos = PolicyRule.objects.create(
            rule_type="panos", name="pan", action="allow", band=self.band, position="closer", index=99
        )

        self.assertEqual(list(PolicyRule.objects.all()), [panos, first, second, output])


class TestHostRelativeUsage(TestCase):
    """Test that host relative Address Objects can not reach a PAN-OS or NAT rule by any path."""

    def setUp(self) -> None:
        """Create a PAN-OS rule, an nftables rule, a NAT rule, a static object and a dynamic object."""
        band, _, _ = fixtures.create_policy_band()
        self.panos = PolicyRule.objects.create(
            name="pan", action="allow", rule_type="panos", band=band, position="header"
        )
        self.nftables = PolicyRule.objects.create(name="nft", action="allow", rule_type="nftables", chain="input")
        self.nat = NATPolicyRule.objects.create(name="nat")
        self.host = fixtures.create_linux_host()
        self.static = AddressObject.objects.create(name="static", prefix=self.host.primary_ip4.parent)
        self.subnet = AddressObject.objects.create(name="host subnet", dynamic="subnet")
        self.zone = Zone.objects.create(name="trust")

    def test_nat_rule_refuses_host_relative_address(self):
        """NAT rules refuse host relative Address Objects, from the rule side and the object side."""
        with self.assertRaises(ValidationError), transaction.atomic():
            self.nat.original_source_addresses.add(self.subnet)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.subnet.translated_destination_nat_policy_rules.add(self.nat)

    def test_nat_rule_refuses_group_with_host_relative_address(self):
        """NAT rules refuse a group holding a host relative Address Object."""
        group = AddressObjectGroup.objects.create(name="dynamic group")
        group.address_objects.add(self.subnet)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.nat.original_destination_address_groups.add(group)

    def test_panos_rule_refuses_host_relative_address_on_add(self):
        """Adding a host relative object straight to a PAN-OS rule is refused."""
        with self.assertRaises(ValidationError), transaction.atomic():
            self.panos.source_addresses.add(self.subnet)

    def test_nftables_rule_refuses_zone_on_add(self):
        """Adding a zone straight to an nftables rule is refused."""
        with self.assertRaises(ValidationError), transaction.atomic():
            self.nftables.source_zones.add(self.zone)

    def test_group_used_by_panos_rule_refuses_host_relative_address(self):
        """A group a PAN-OS rule uses can not gain a host relative object, from either side."""
        group = AddressObjectGroup.objects.create(name="panos group")
        self.panos.destination_address_groups.add(group)
        with self.assertRaises(ValidationError), transaction.atomic():
            group.address_objects.add(self.subnet)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.subnet.address_object_groups.add(group)

    def test_group_used_by_nat_rule_refuses_host_relative_address(self):
        """A group a NAT rule uses can not gain a host relative object."""
        group = AddressObjectGroup.objects.create(name="nat group")
        self.nat.translated_source_address_groups.add(group)
        with self.assertRaises(ValidationError), transaction.atomic():
            group.address_objects.add(self.subnet)

    def test_group_used_only_by_nftables_rule_accepts_host_relative_address(self):
        """Groups used by nftables rules alone may hold host relative objects."""
        group = AddressObjectGroup.objects.create(name="nft group")
        self.nftables.source_address_groups.add(group)
        group.address_objects.add(self.subnet)

        self.assertIn(self.subnet, group.address_objects.all())

    def test_object_used_by_panos_rule_can_not_become_dynamic(self):
        """Turning a static object a PAN-OS rule uses into a dynamic one is refused."""
        self.panos.source_addresses.add(self.static)
        self.static.prefix = None
        self.static.dynamic = "subnet"
        with self.assertRaises(ValidationError), transaction.atomic():
            self.static.save()

    def test_object_in_group_used_by_nat_rule_can_not_reference_a_device(self):
        """Turning an object inside a group a NAT rule uses into a Device reference is refused."""
        group = AddressObjectGroup.objects.create(name="nat group")
        group.address_objects.add(self.static)
        self.nat.original_source_address_groups.add(group)
        self.static.prefix = None
        self.static.device = self.host
        with self.assertRaises(ValidationError), transaction.atomic():
            self.static.save()


class TestPolicyRuleTypes(TestCase):
    """Test that a Policy only holds rules of its own type."""

    def setUp(self) -> None:
        """Create a rule of each type and a Policy of each type."""
        band, _, _ = fixtures.create_policy_band()
        self.panos_rule = PolicyRule.objects.create(
            name="pan", action="allow", rule_type="panos", band=band, position="header"
        )
        self.nft_rule = PolicyRule.objects.create(name="nft", action="allow", rule_type="nftables", chain="input")
        self.panos_policy = Policy.objects.create(name="firewall", rule_type="panos")
        self.nft_policy = Policy.objects.create(name="web servers", rule_type="nftables")

    def test_rule_type_is_required(self):
        """There is no default rule type on a Policy."""
        with self.assertRaises(ValidationError) as ctx:
            Policy(name="no type").full_clean()
        self.assertIn("rule_type", ctx.exception.message_dict)

    def test_policy_accepts_rules_of_its_type(self):
        """Rules of the Policy's type can be added."""
        self.panos_policy.policy_rules.add(self.panos_rule)
        self.nft_policy.policy_rules.add(self.nft_rule)

        self.assertEqual(list(self.nft_policy.policy_rules.all()), [self.nft_rule])

    def test_policy_refuses_rules_of_another_type(self):
        """Rules of another type are refused, from the Policy side and the rule side."""
        with self.assertRaises(ValidationError), transaction.atomic():
            self.panos_policy.policy_rules.add(self.nft_rule)
        with self.assertRaises(ValidationError), transaction.atomic():
            self.panos_rule.policies.add(self.nft_policy)

    def test_rule_type_can_not_change(self):
        """A saved Policy keeps its rule type."""
        self.panos_policy.rule_type = "nftables"
        with self.assertRaises(ValidationError) as ctx:
            self.panos_policy.full_clean()
        self.assertIn("rule_type", ctx.exception.message_dict)
