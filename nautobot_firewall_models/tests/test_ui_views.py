"""Unit tests for views."""

# ruff: noqa: F403, F405
# pylint: disable=invalid-name
# pylint: disable=duplicate-code
from django.urls import reverse
from nautobot.apps.testing import TestCase, ViewTestCases, post_data
from nautobot.extras.models import Status
from nautobot.ipam.models import Prefix
from nautobot.users.models import ObjectPermission

from nautobot_firewall_models.models import *  # pylint: disable=unused-wildcard-import, wildcard-import

from . import fixtures


class FQDNUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Protocol viewsets."""

    model = FQDN
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        status = Status.objects.get(name="Active").id
        cls.form_data = {"name": "test.local", "status": status}
        fixtures.create_fqdn()
        cls.csv_data = (
            "name,status",
            "foo.bar.com,Active",
            "bar.foo.com,Active",
            "bar.baz.foo.com,Active",
        )


class AddressObjectUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the AddressObject viewsets."""

    model = AddressObject
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_addr_obj()
        prefix = Prefix.objects.first()
        status = Status.objects.get(name="Active").id
        AddressObject.objects.create(name="deleteableobj1", prefix=prefix)
        AddressObject.objects.create(name="deleteableobj2", prefix=prefix)
        AddressObject.objects.create(name="deleteableobj3", prefix=prefix)

        cls.form_data = {"name": "obj1", "prefix": prefix.id, "status": status}
        cls.csv_data = (
            "name,prefix,status",
            f"csvobj1,{prefix.id},Active",
            f"csvobj2,{prefix.id},Active",
            f"csvobj3,{prefix.id},Active",
        )


class AddressObjectGroupUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the AddressObjectGroup viewsets."""

    model = AddressObjectGroup
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_addr_group()
        status = Status.objects.get(name="Active").id
        addr_obj = AddressObject.objects.first()
        AddressObjectGroup.objects.create(name="deleteableobj1")
        AddressObjectGroup.objects.create(name="deleteableobj2")
        AddressObjectGroup.objects.create(name="deleteableobj3")
        # The form takes Address Objects and nested groups through one combined picker.
        cls.form_data = {"name": "test1", "address_objects_and_groups": [f"object:{addr_obj.id}"], "status": status}
        cls.csv_data = (
            "name,address_objects,status",
            f'csvobj1,"{addr_obj.id}",Active',
            f'csvobj2,"{addr_obj.id}",Active',
            f'csvobj3,"{addr_obj.id}",Active',
        )


class ApplicationObjectUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the ApplicationObject viewsets."""

    model = ApplicationObject
    bulk_edit_data = {"description": "bulk test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_app_obj()
        ApplicationObject.objects.create(name="deleteableobj1")
        ApplicationObject.objects.create(name="deleteableobj2")
        ApplicationObject.objects.create(name="deleteableobj3")
        status = Status.objects.get(name="Active").id
        cls.form_data = {"name": "obj1", "risk": 1, "status": status}
        cls.csv_data = (
            "name,risk,status",
            "csvobj1,1,Active",
            "csvobj2,2,Active",
            "csvobj3,3,Active",
        )


class ApplicationObjectGroupUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the ApplicationObjectGroup viewsets."""

    model = ApplicationObjectGroup
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_app_group()
        status = Status.objects.get(name="Active").id
        app_obj = ApplicationObject.objects.first()
        ApplicationObjectGroup.objects.create(name="deleteableobj1")
        ApplicationObjectGroup.objects.create(name="deleteableobj2")
        ApplicationObjectGroup.objects.create(name="deleteableobj3")
        cls.form_data = {"name": "test1", "application_objects": [app_obj.id], "status": status}
        cls.csv_data = (
            "name,application_objects,status",
            f'csvobj1,"{app_obj.id}",Active',
            f'csvobj2,"{app_obj.id}",Active',
            f'csvobj3,"{app_obj.id}",Active',
        )


class ServiceObjectUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the ServiceObject viewsets."""

    model = ServiceObject
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        ServiceObject.objects.create(name="deleteableobj1", ip_protocol="TCP")
        ServiceObject.objects.create(name="deleteableobj2", ip_protocol="TCP")
        ServiceObject.objects.create(name="deleteableobj3", ip_protocol="TCP")
        status = Status.objects.get(name="Active").id
        cls.form_data = {"name": "HTTP", "port": "8088", "status": status, "ip_protocol": "TCP"}
        fixtures.create_svc_obj()
        cls.csv_data = (
            "name,port,ip_protocol,status",
            "csvobj1,1,TCP,Active",
            "csvobj2,2,TCP,Active",
            "csvobj3,3,TCP,Active",
        )


class ServiceObjectGroupUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the ServiceGroup viewsets."""

    model = ServiceObjectGroup
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_svc_group()
        svc_obj = ServiceObject.objects.first()
        status = Status.objects.get(name="Active").id
        ServiceObjectGroup.objects.create(name="deleteableobj1")
        ServiceObjectGroup.objects.create(name="deleteableobj2")
        ServiceObjectGroup.objects.create(name="deleteableobj3")
        cls.form_data = {"name": "test1", "service_objects": [svc_obj.id], "status": status}
        cls.csv_data = (
            "name,service_objects,status",
            f'csvobj1,"{svc_obj.id}",Active',
            f'csvobj2,"{svc_obj.id}",Active',
            f'csvobj3,"{svc_obj.id}",Active',
        )


class UserObjectUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the User viewsets."""

    model = UserObject
    bulk_edit_data = {"name": "User Name 123"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        status = Status.objects.get(name="Active").id
        UserObject.objects.create(username="deleteableobj1", name="deleteableobj1")
        UserObject.objects.create(username="deleteableobj2", name="deleteableobj2")
        UserObject.objects.create(username="deleteableobj3", name="deleteableobj3")
        cls.form_data = {"username": "test1", "name": "Foo", "status": status}
        fixtures.create_user_obj()
        cls.csv_data = (
            "name,username,status",
            "csvobj1,csvuser1,Active",
            "csvobj2,csvuser2,Active",
            "csvobj3,csvuser3,Active",
        )


class UserObjectGroupUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the UserGroup viewsets."""

    model = UserObjectGroup
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_user_group()
        user = UserObject.objects.first()
        status = Status.objects.get(name="Active").id
        UserObjectGroup.objects.create(name="deleteableobj1")
        UserObjectGroup.objects.create(name="deleteableobj2")
        UserObjectGroup.objects.create(name="deleteableobj3")
        cls.form_data = {"name": "test1", "user_objects": [user.id], "status": status}
        cls.csv_data = (
            "name,user_objects,status",
            f'csvobj1,"{user.id}",Active',
            f'csvobj2,"{user.id}",Active',
            f'csvobj3,"{user.id}",Active',
        )


class ZoneUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Zone viewsets."""

    model = Zone
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for UI calls."""
        status = Status.objects.get(name="Active").id
        Zone.objects.create(name="deleteableobj1")
        Zone.objects.create(name="deleteableobj2")
        Zone.objects.create(name="deleteableobj3")
        cls.form_data = {"name": "trust", "status": status}
        fixtures.create_zone()
        cls.csv_data = (
            "name,status",
            "csvobj1,Active",
            "csvobj2,Active",
            "csvobj3,Active",
        )


class ZoneGroupUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the ZoneGroup viewsets."""

    model = ZoneGroup
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for UI calls."""
        fixtures.create_zone_group()
        zone = Zone.objects.first()
        status = Status.objects.get(name="Active").id
        ZoneGroup.objects.create(name="deleteableobj1")
        ZoneGroup.objects.create(name="deleteableobj2")
        ZoneGroup.objects.create(name="deleteableobj3")
        cls.form_data = {"name": "test1", "zones": [zone.id], "status": status}
        cls.csv_data = (
            "name,zones,status",
            f'csvobj1,"{zone.id}",Active',
            f'csvobj2,"{zone.id}",Active',
            f'csvobj3,"{zone.id}",Active',
        )


class PolicyBandUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the PolicyBand viewsets."""

    model = PolicyBand
    bulk_edit_data = {"description": "bulk test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for UI calls."""
        fixtures.create_policy_band()
        PolicyBand.objects.create(name="deleteableobj1", index=101)
        PolicyBand.objects.create(name="deleteableobj2", index=102)
        PolicyBand.objects.create(name="deleteableobj3", index=103)
        cls.form_data = {"name": "No Trust", "index": 15}
        cls.csv_data = (
            "name,index",
            "csvobj1,201",
            "csvobj2,202",
            "csvobj3,203",
        )


class PolicyRuleUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the PolicyRule viewsets."""

    model = PolicyRule
    bulk_edit_data = {"description": "bulk test update description"}

    def _get_url(self, action, instance=None):
        """Open the PAN-OS form directly, since Add without a rule type shows the type chooser instead."""
        url = super()._get_url(action, instance)
        return f"{url}?rule_type=panos" if action == "add" else url

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_policy_rule()
        band = PolicyBand.objects.first()
        src_usr = UserObject.objects.first()
        src_addr = AddressObject.objects.first()
        dest_addr = AddressObject.objects.last()
        status = Status.objects.get(name="Active").id
        svc = ServiceObject.objects.first()
        PolicyRule.objects.create(
            rule_type="panos", band=band, position="header", name="deleteableobj1", action="deny", index=1
        )
        PolicyRule.objects.create(
            rule_type="panos", band=band, position="header", name="deleteableobj2", action="deny", index=1
        )
        PolicyRule.objects.create(
            rule_type="panos", band=band, position="header", name="deleteableobj3", action="deny", index=1
        )
        cls.form_data = {
            # pylint: disable=R0801
            "band": band.id,
            "position": "header",
            # The form takes objects and their groups through one combined picker per field.
            "source_users_and_groups": [f"object:{src_usr.id}"],
            "source_addresses_and_groups": [f"object:{src_addr.id}"],
            "destination_addresses_and_groups": [f"object:{dest_addr.id}"],
            "action": "deny",
            "log": True,
            "destination_services_and_groups": [f"object:{svc.id}"],
            "name": "test rule",
            "status": status,
        }
        cls.csv_data = (
            "name,rule_type,action,band,position,index,status",
            "csvobj1,panos,deny,Global Deny,header,1,Active",
            "csvobj2,panos,deny,Global Deny,header,2,Active",
            "csvobj3,panos,deny,Global Deny,closer,3,Active",
        )


class PolicyUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Policy viewsets."""

    model = Policy
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_policy()
        pol_rule = PolicyRule.objects.first()
        status = Status.objects.get(name="Active").id
        Policy.objects.create(rule_type="panos", name="deleteableobj1")
        Policy.objects.create(rule_type="panos", name="deleteableobj2")
        Policy.objects.create(rule_type="panos", name="deleteableobj3")
        cls.form_data = {
            "name": "test 2",
            "rule_type": "panos",
            "policy_rules": [pol_rule.id],
            "description": "Test desc",
            "status": status,
        }
        cls.csv_data = (
            "name,rule_type,policy_rules,status",
            f'csvobj1,panos,"{pol_rule.id}",Active',
            f'csvobj2,panos,"{pol_rule.id}",Active',
            f'csvobj3,panos,"{pol_rule.id}",Active',
        )

    def test_device_weight_permissions(self):
        """Test that the device weights cannot be updated without dcim.change_device and nautobot_firewall_models.change_policy permissions."""
        # Remove all user permissions and add view permissions for dcim.device and nautobot_firewall_models.policy
        ObjectPermission.objects.all().delete()
        self.add_permissions("dcim.view_device", "nautobot_firewall_models.view_policy")

        # Retrieve the policy view and assert that the weight form field is disabled
        fixtures.assign_policies()
        policy = Policy.objects.get(name="Policy 2")

        weight = policy.policydevicem2m_set.first().weight
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="device-weight-input1" type="number" name="{policy.assigned_devices.first().pk}" value="{weight}" disabled>',
            html=True,
        )

        # Assert that trying to submit the form with insufficient permissions fails
        post_request = {
            "path": reverse("plugins:nautobot_firewall_models:policy_devices", kwargs={"pk": policy.pk}),
            "data": post_data({str(policy.assigned_devices.first().pk): "150"}),
        }
        self.assertHttpStatus(self.client.post(**post_request), 403)

        # Give the user "change" permissions
        self.add_permissions("dcim.change_device", "nautobot_firewall_models.change_policy")

        # Form field is no longer disabled
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="device-weight-input1" type="number" name="{policy.assigned_devices.first().pk}" value="{weight}">',
            html=True,
        )

        # Post succeeds
        self.assertHttpStatus(self.client.post(**post_request), 302)

    def test_dynamicgroup_weight_permissions(self):
        """Test that the dynamicgroup weights cannot be updated without dcim.change_dynamicgroup and nautobot_firewall_models.change_policy permissions."""

        # Remove all user permissions and add view permissions for dcim.device and nautobot_firewall_models.policy
        ObjectPermission.objects.all().delete()
        self.add_permissions("extras.view_dynamicgroup", "nautobot_firewall_models.view_policy")

        # Retrieve the policy view and assert that the weight form field is disabled
        fixtures.assign_policies()
        policy = Policy.objects.get(name="Policy 3")

        weight = policy.policydynamicgroupm2m_set.first().weight
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="dynamicgroup-weight-input1" type="number" name="{policy.assigned_dynamic_groups.first().pk}" value="{weight}" disabled>',
            html=True,
        )

        # Assert that trying to submit the form with insufficient permissions fails
        post_request = {
            "path": reverse("plugins:nautobot_firewall_models:policy_dynamic-groups", kwargs={"pk": policy.pk}),
            "data": post_data({str(policy.assigned_dynamic_groups.first().pk): "150"}),
        }
        self.assertHttpStatus(self.client.post(**post_request), 403)

        # Give the user "change" permissions
        self.add_permissions("extras.change_dynamicgroup", "nautobot_firewall_models.change_policy")

        # Form field is no longer disabled
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="dynamicgroup-weight-input1" type="number" name="{policy.assigned_dynamic_groups.first().pk}" value="{weight}">',
            html=True,
        )

        # Post succeeds
        self.assertHttpStatus(self.client.post(**post_request), 302)


class NATPolicyRuleUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Policy viewsets."""

    model = NATPolicyRule
    bulk_edit_data = {"log": False}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_natpolicy_rule()
        src_addr = AddressObject.objects.first()
        dest_addr = AddressObject.objects.last()
        svc = ServiceObject.objects.first()
        status = Status.objects.get(name="Active").id
        NATPolicyRule.objects.create(name="deleteableobj1")
        NATPolicyRule.objects.create(name="deleteableobj2")
        NATPolicyRule.objects.create(name="deleteableobj3")
        cls.form_data = {
            # The form takes objects and their groups through one combined picker per field.
            "original_source_addresses_and_groups": [f"object:{src_addr.id}"],
            "original_destination_addresses_and_groups": [f"object:{dest_addr.id}"],
            "translated_destination_addresses_and_groups": [f"object:{src_addr.id}"],
            "log": True,
            "original_destination_services_and_groups": [f"object:{svc.id}"],
            "name": "test rule",
            "status": status,
        }
        cls.csv_data = (
            "name,log,status",
            "csvrule1,True,Active",
            "csvrule2,True,Active",
            "csvrule3,True,Active",
        )


class NATPolicyUIViewTest(ViewTestCases.PrimaryObjectViewTestCase):
    """Test the Policy viewsets."""

    model = NATPolicy
    bulk_edit_data = {"description": "test update description"}

    @classmethod
    def setUpTestData(cls):
        """Create test data for API calls."""
        fixtures.create_natpolicy()
        status = Status.objects.get(name="Active").id
        nat_pol_rule = NATPolicyRule.objects.first()
        NATPolicy.objects.create(name="deleteableobj1")
        NATPolicy.objects.create(name="deleteableobj2")
        NATPolicy.objects.create(name="deleteableobj3")
        cls.form_data = {"status": status, "name": "test 1", "nat_policy_rules": [nat_pol_rule.id]}
        cls.csv_data = (
            "name,nat_policy_rules,status",
            f'csvrule1,"{nat_pol_rule.id}",Active',
            f'csvrule2,"{nat_pol_rule.id}",Active',
            f'csvrule3,"{nat_pol_rule.id}",Active',
        )

    def test_device_weight_permissions(self):
        """Test that the device weights cannot be updated without dcim.change_device and nautobot_firewall_models.change_natpolicy permissions."""
        # Remove all user permissions and add view permissions for dcim.device and nautobot_firewall_models.natpolicy
        ObjectPermission.objects.all().delete()
        self.add_permissions("dcim.view_device", "nautobot_firewall_models.view_natpolicy")

        # Retrieve the policy view and assert that the weight form field is disabled
        fixtures.assign_policies()
        policy = NATPolicy.objects.get(name="NAT Policy 2")

        weight = policy.natpolicydevicem2m_set.first().weight
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="device-weight-input1" type="number" name="{policy.assigned_devices.first().pk}" value="{weight}" disabled>',
            html=True,
        )

        # Assert that trying to submit the form with insufficient permissions fails
        post_request = {
            "path": reverse("plugins:nautobot_firewall_models:natpolicy_devices", kwargs={"pk": policy.pk}),
            "data": post_data({str(policy.assigned_devices.first().pk): "150"}),
        }
        self.assertHttpStatus(self.client.post(**post_request), 403)

        # Give the user "change" permissions
        self.add_permissions("dcim.change_device", "nautobot_firewall_models.change_natpolicy")

        # Form field is no longer disabled
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="device-weight-input1" type="number" name="{policy.assigned_devices.first().pk}" value="{weight}">',
            html=True,
        )

        # Post succeeds
        self.assertHttpStatus(self.client.post(**post_request), 302)

    def test_dynamicgroup_weight_permissions(self):
        """Test that the dynamicgroup weights cannot be updated without dcim.change_dynamicgroup and nautobot_firewall_models.change_natpolicy permissions."""

        # Remove all user permissions and add view permissions for dcim.device and nautobot_firewall_models.natpolicy
        ObjectPermission.objects.all().delete()
        self.add_permissions("extras.view_dynamicgroup", "nautobot_firewall_models.view_natpolicy")

        # Retrieve the policy view and assert that the weight form field is disabled
        fixtures.assign_policies()
        policy = NATPolicy.objects.get(name="NAT Policy 3")

        weight = policy.natpolicydynamicgroupm2m_set.first().weight
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="dynamicgroup-weight-input1" type="number" name="{policy.assigned_dynamic_groups.first().pk}" value="{weight}" disabled>',
            html=True,
        )

        # Assert that trying to submit the form with insufficient permissions fails
        post_request = {
            "path": reverse("plugins:nautobot_firewall_models:natpolicy_dynamic-groups", kwargs={"pk": policy.pk}),
            "data": post_data({str(policy.assigned_dynamic_groups.first().pk): "150"}),
        }
        self.assertHttpStatus(self.client.post(**post_request), 403)

        # Give the user "change" permissions
        self.add_permissions("extras.change_dynamicgroup", "nautobot_firewall_models.change_natpolicy")

        # Form field is no longer disabled
        response = self.client.get(policy.get_absolute_url())
        self.assertContains(
            response,
            f'<input id="dynamicgroup-weight-input1" type="number" name="{policy.assigned_dynamic_groups.first().pk}" value="{weight}">',
            html=True,
        )

        # Post succeeds
        self.assertHttpStatus(self.client.post(**post_request), 302)


class PolicyRuleTypeUIViewTest(TestCase):
    """Test the rule type chooser and the form each rule type opens."""

    @classmethod
    def setUpTestData(cls):
        """Create a dynamic Address Object to use on an nftables rule."""
        cls.subnet = AddressObject.objects.create(name="host subnet", dynamic="subnet")
        cls.url = reverse("plugins:nautobot_firewall_models:policyrule_add")

    def setUp(self):
        """Grant access to add Policy Rules."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_policyrule",
            "nautobot_firewall_models.view_policyrule",
            "nautobot_firewall_models.view_addressobject",
            "extras.view_status",
        )

    def test_add_without_rule_type_shows_the_chooser(self):
        """Add asks for the rule type first and links to the form for each type."""
        response = self.client.get(self.url)

        self.assertHttpStatus(response, 200)
        self.assertContains(response, f"{self.url}?rule_type=panos")
        self.assertContains(response, f"{self.url}?rule_type=nftables")

    def test_nftables_form_hides_panos_fields(self):
        """The nftables form shows a chain and no band, position, zones, users or applications."""
        response = self.client.get(f"{self.url}?rule_type=nftables")

        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'name="chain"')
        for field in ("band", "position", "source_zones", "source_users", "applications"):
            self.assertNotContains(response, f'name="{field}"')

    def test_negate_checkboxes_only_on_panos_form(self):
        """The PAN-OS form has the negate checkboxes and the nftables form does not."""
        panos = self.client.get(f"{self.url}?rule_type=panos")
        nftables = self.client.get(f"{self.url}?rule_type=nftables")

        for field in ("negate_source", "negate_destination"):
            self.assertContains(panos, f'name="{field}"')
            self.assertNotContains(nftables, f'name="{field}"')

    def test_create_panos_rule_with_negated_source(self):
        """Posting the PAN-OS form saves the negate checkboxes, and the expanded rule marks the negated side."""
        self.add_permissions("nautobot_firewall_models.view_policyband")
        band, _, _ = fixtures.create_policy_band()
        data = {
            "rule_type": "panos",
            "name": "not internal",
            "band": band.pk,
            "position": "header",
            "action": "allow",
            "negate_source": True,
            "status": Status.objects.get(name="Active").pk,
        }
        response = self.client.post(f"{self.url}?rule_type=panos", post_data(data))

        self.assertHttpStatus(response, 302)
        rule = PolicyRule.objects.get(name="not internal")
        self.assertEqual((rule.negate_source, rule.negate_destination), (True, False))
        self.assertContains(self.client.get(rule.get_absolute_url()), "Matches every address except these")

    def test_panos_form_hides_the_chain_and_source_services(self):
        """The PAN-OS form has no chain and no source services, which PAN-OS security rules do not support."""
        response = self.client.get(f"{self.url}?rule_type=panos")

        self.assertHttpStatus(response, 200)
        self.assertContains(response, 'name="band"')
        self.assertNotContains(response, 'name="chain"')
        self.assertNotContains(response, 'name="source_services_and_groups"')
        self.assertContains(response, 'name="destination_services_and_groups"')

    def test_create_nftables_rule(self):
        """Posting the nftables form creates an nftables rule."""
        status = Status.objects.get(name="Active")
        data = {
            "rule_type": "nftables",
            "name": "allow subnet",
            "chain": "input",
            "action": "allow",
            "source_addresses": [self.subnet.pk],
            "status": status.pk,
        }
        response = self.client.post(f"{self.url}?rule_type=nftables", post_data(data))

        self.assertHttpStatus(response, 302)
        rule = PolicyRule.objects.get(name="allow subnet")
        self.assertEqual((rule.rule_type, rule.chain, rule.band), ("nftables", "input", None))


class ObjectOrGroupPickerUIViewTest(TestCase):
    """Test the single pickers that list objects and their groups together, e.g. Zones and Zone Groups."""

    @classmethod
    def setUpTestData(cls):
        """Create a band, a Zone and a Zone Group."""
        cls.band, _, _ = fixtures.create_policy_band()
        cls.zone = Zone.objects.create(name="trust")
        cls.group = ZoneGroup.objects.create(name="inside")
        cls.status = Status.objects.get(name="Active")
        cls.rule_url = reverse("plugins:nautobot_firewall_models:policyrule_add")
        cls.nat_url = reverse("plugins:nautobot_firewall_models:natpolicyrule_add")

    def setUp(self):
        """Grant access to add rules and view what they reference."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_policyrule",
            "nautobot_firewall_models.change_policyrule",
            "nautobot_firewall_models.view_policyrule",
            "nautobot_firewall_models.add_natpolicyrule",
            "nautobot_firewall_models.view_natpolicyrule",
            "nautobot_firewall_models.view_policyband",
            "nautobot_firewall_models.view_zone",
            "nautobot_firewall_models.view_zonegroup",
            "nautobot_firewall_models.view_addressobject",
            "nautobot_firewall_models.view_addressobjectgroup",
            "nautobot_firewall_models.view_serviceobject",
            "nautobot_firewall_models.view_serviceobjectgroup",
            "extras.view_status",
        )

    def _rule_data(self, **data):
        return post_data(
            {
                "rule_type": "panos",
                "name": "zoned",
                "band": self.band.pk,
                "position": "header",
                "action": "allow",
                "status": self.status.pk,
                **data,
            }
        )

    def test_form_shows_one_searching_picker_per_field(self):
        """Each field has one picker that searches the grouped objects API, and the separate pickers are gone."""
        response = self.client.get(f"{self.rule_url}?rule_type=panos")

        self.assertHttpStatus(response, 200)
        for name, kind in (
            ("source_zones", "zones"),
            ("destination_addresses", "addresses"),
            ("destination_services", "services"),
            ("source_users", "users"),
            ("applications", "applications"),
        ):
            self.assertContains(response, f'name="{name}_and_groups"')
            self.assertContains(response, f'data-url="/api/plugins/firewall/grouped-objects/{kind}/"')
            self.assertNotContains(response, f'name="{name}"')
        # Options are searched as the user types, so nothing unselected is rendered.
        self.assertNotContains(response, f'value="object:{self.zone.pk}"')

    def test_picker_saves_zones_and_groups(self):
        """The picker's selection is split back into the Zone and Zone Group fields."""
        data = self._rule_data(
            source_zones_and_groups=[f"object:{self.zone.pk}", f"group:{self.group.pk}"],
            destination_zones_and_groups=[f"group:{self.group.pk}"],
        )
        response = self.client.post(f"{self.rule_url}?rule_type=panos", data)

        self.assertHttpStatus(response, 302)
        rule = PolicyRule.objects.get(name="zoned")
        self.assertEqual(list(rule.source_zones.all()), [self.zone])
        self.assertEqual(list(rule.source_zone_groups.all()), [self.group])
        self.assertEqual(list(rule.destination_zones.all()), [])
        self.assertEqual(list(rule.destination_zone_groups.all()), [self.group])

    def test_edit_form_selects_saved_zones_and_groups(self):
        """Editing a rule preselects its saved Zones and Zone Groups in the picker."""
        rule = PolicyRule.objects.create(
            name="saved", action="allow", rule_type="panos", band=self.band, position="header"
        )
        rule.source_zones.set([self.zone])
        rule.source_zone_groups.set([self.group])

        response = self.client.get(reverse("plugins:nautobot_firewall_models:policyrule_edit", kwargs={"pk": rule.pk}))

        self.assertHttpStatus(response, 200)
        content = response.content.decode()
        self.assertRegex(content, rf'value="object:{self.zone.pk}"\s+selected')
        self.assertRegex(content, rf'value="group:{self.group.pk}"\s+selected')

    def test_picker_only_offers_zones_the_user_may_view(self):
        """A Zone the user may not view is not offered and can not be submitted."""
        ObjectPermission.objects.filter(object_types__model="zone").delete()

        response = self.client.post(
            f"{self.rule_url}?rule_type=panos", self._rule_data(source_zones_and_groups=[f"object:{self.zone.pk}"])
        )

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Select a valid choice.")
        self.assertFalse(PolicyRule.objects.filter(name="zoned").exists())

    def test_nat_rule_picker_saves_zones_and_groups(self):
        """NAT rules use the same picker."""
        data = post_data(
            {
                "name": "nat zoned",
                "status": self.status.pk,
                "source_zones_and_groups": [f"group:{self.group.pk}"],
                "destination_zones_and_groups": [f"object:{self.zone.pk}"],
            }
        )
        response = self.client.post(self.nat_url, data)

        self.assertHttpStatus(response, 302)
        rule = NATPolicyRule.objects.get(name="nat zoned")
        self.assertEqual(list(rule.source_zone_groups.all()), [self.group])
        self.assertEqual(list(rule.destination_zones.all()), [self.zone])

    def test_picker_saves_addresses_services_and_their_groups(self):
        """Addresses and services use the same picker and save to their object and group fields."""
        address = AddressObject.objects.create(name="web", dynamic="subnet")
        address_group = AddressObjectGroup.objects.create(name="web servers")
        service = ServiceObject.objects.create(name="HTTPS", port="443", ip_protocol="TCP")
        service_group = ServiceObjectGroup.objects.create(name="web ports")
        data = post_data(
            {
                "rule_type": "nftables",
                "name": "web",
                "chain": "input",
                "action": "allow",
                "status": self.status.pk,
                "source_addresses_and_groups": [f"object:{address.pk}", f"group:{address_group.pk}"],
                "destination_services_and_groups": [f"object:{service.pk}", f"group:{service_group.pk}"],
            }
        )
        response = self.client.post(f"{self.rule_url}?rule_type=nftables", data)

        self.assertHttpStatus(response, 302)
        rule = PolicyRule.objects.get(name="web")
        self.assertEqual(list(rule.source_addresses.all()), [address])
        self.assertEqual(list(rule.source_address_groups.all()), [address_group])
        self.assertEqual(list(rule.destination_services.all()), [service])
        self.assertEqual(list(rule.destination_service_groups.all()), [service_group])

    def test_nat_form_has_no_source_service_pickers(self):
        """The NAT form has destination service pickers but no source service pickers."""
        response = self.client.get(self.nat_url)

        self.assertHttpStatus(response, 200)
        for name in ("original_source_services", "translated_source_services"):
            self.assertNotContains(response, f'name="{name}_and_groups"')
        for name in ("original_destination_services", "translated_destination_services"):
            self.assertContains(response, f'name="{name}_and_groups"')

    def test_nftables_form_has_no_zone_picker(self):
        """nftables rules have no zones, so the form has no zone picker but keeps the address picker."""
        response = self.client.get(f"{self.rule_url}?rule_type=nftables")

        self.assertNotContains(response, 'name="source_zones_and_groups"')
        self.assertContains(response, 'name="source_addresses_and_groups"')

    def test_picker_saves_users_applications_and_their_groups(self):
        """Users and applications use the same picker on PAN-OS rules."""
        self.add_permissions(
            "nautobot_firewall_models.view_userobject",
            "nautobot_firewall_models.view_userobjectgroup",
            "nautobot_firewall_models.view_applicationobject",
            "nautobot_firewall_models.view_applicationobjectgroup",
        )
        user = UserObject.objects.create(username="jdoe", name="J Doe")
        user_group = UserObjectGroup.objects.create(name="admins")
        application = ApplicationObject.objects.create(name="ssh")
        application_group = ApplicationObjectGroup.objects.create(name="remote access")
        data = self._rule_data(
            source_users_and_groups=[f"object:{user.pk}", f"group:{user_group.pk}"],
            applications_and_groups=[f"object:{application.pk}", f"group:{application_group.pk}"],
        )
        response = self.client.post(f"{self.rule_url}?rule_type=panos", data)

        self.assertHttpStatus(response, 302)
        rule = PolicyRule.objects.get(name="zoned")
        self.assertEqual(list(rule.source_users.all()), [user])
        self.assertEqual(list(rule.source_user_groups.all()), [user_group])
        self.assertEqual(list(rule.applications.all()), [application])
        self.assertEqual(list(rule.application_groups.all()), [application_group])

    def test_malformed_value_is_refused(self):
        """A value that is not object:<uuid> or group:<uuid> is refused."""
        response = self.client.post(
            f"{self.rule_url}?rule_type=panos", self._rule_data(source_zones_and_groups=["zone:not-a-uuid"])
        )

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "Select a valid choice.")


class ManagedLocallyUIViewTest(TestCase):
    """Test the Managed Locally checks on the group and Address Object forms."""

    def setUp(self):
        """Grant access to Address Objects and their groups."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_addressobject",
            "nautobot_firewall_models.view_addressobject",
            "nautobot_firewall_models.add_addressobjectgroup",
            "nautobot_firewall_models.view_addressobjectgroup",
            "extras.view_status",
        )
        self.managed = Status.objects.get(name="Managed Locally")

    def test_create_managed_locally_address_object_by_name_only(self):
        """The Address Object form accepts a Managed Locally object with only a name."""
        response = self.client.post(
            reverse("plugins:nautobot_firewall_models:addressobject_add"),
            post_data({"name": "High risk IP addresses", "status": self.managed.pk}),
        )

        self.assertHttpStatus(response, 302)
        self.assertTrue(AddressObject.objects.filter(name="High risk IP addresses").exists())

    def test_managed_locally_group_form_refuses_members(self):
        """The group form refuses members on a Managed Locally group."""
        member = AddressObject.objects.create(name="local", dynamic="subnet")
        response = self.client.post(
            reverse("plugins:nautobot_firewall_models:addressobjectgroup_add"),
            post_data(
                {"name": "High risk", "status": self.managed.pk, "address_objects_and_groups": [f"object:{member.pk}"]}
            ),
        )

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "A Managed Locally group is defined on the firewall")
        self.assertFalse(AddressObjectGroup.objects.filter(name="High risk").exists())


class NestedAddressGroupUIViewTest(TestCase):
    """Test the Address Object Group form's combined picker for Address Objects and nested groups."""

    def setUp(self):
        """Grant access to Address Objects and their groups."""
        super().setUp()
        self.add_permissions(
            "nautobot_firewall_models.add_addressobjectgroup",
            "nautobot_firewall_models.change_addressobjectgroup",
            "nautobot_firewall_models.view_addressobjectgroup",
            "nautobot_firewall_models.view_addressobject",
            "extras.view_status",
        )
        self.status = Status.objects.get(name="Active")
        self.url = reverse("plugins:nautobot_firewall_models:addressobjectgroup_add")

    def test_form_shows_one_picker_for_objects_and_groups(self):
        """The group form has one searching picker in place of the separate Address Object field."""
        response = self.client.get(self.url)

        self.assertContains(response, 'name="address_objects_and_groups"')
        self.assertContains(response, 'data-url="/api/plugins/firewall/grouped-objects/addresses/"')
        self.assertNotContains(response, 'name="address_objects"')

    def test_picker_saves_objects_and_nested_groups(self):
        """The picker's selection is split into Address Objects and nested groups."""
        member = AddressObject.objects.create(name="office", dynamic="subnet")
        child = AddressObjectGroup.objects.create(name="child")
        data = {
            "name": "parent",
            "status": self.status.pk,
            "address_objects_and_groups": [f"object:{member.pk}", f"group:{child.pk}"],
        }
        response = self.client.post(self.url, post_data(data))

        self.assertHttpStatus(response, 302)
        parent = AddressObjectGroup.objects.get(name="parent")
        self.assertEqual(list(parent.address_objects.all()), [member])
        self.assertEqual(list(parent.address_object_groups.all()), [child])

    def test_form_refuses_a_loop(self):
        """Editing a group to contain a group that already contains it is refused."""
        parent = AddressObjectGroup.objects.create(name="parent")
        child = AddressObjectGroup.objects.create(name="child")
        parent.address_object_groups.add(child)
        data = {"name": "child", "status": self.status.pk, "address_objects_and_groups": [f"group:{parent.pk}"]}
        response = self.client.post(
            reverse("plugins:nautobot_firewall_models:addressobjectgroup_edit", kwargs={"pk": child.pk}),
            post_data(data),
        )

        self.assertHttpStatus(response, 200)
        self.assertContains(response, "A group can not contain itself")
