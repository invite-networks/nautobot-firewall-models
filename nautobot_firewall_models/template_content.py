"""Extensions of baseline Nautobot views."""

from django.core.exceptions import ObjectDoesNotExist
from nautobot.apps.ui import TemplateExtension


class HostFirewall(TemplateExtension):  # pylint: disable=abstract-method
    """Show the Firewall a Device or Virtual Machine is bound to, with a link to its Policy Rules."""

    def right_page(self):
        """Add the Firewall card to the right side of the detail view."""
        try:
            firewall = self.context["object"].firewall
        except ObjectDoesNotExist:
            firewall = None
        return self.render("nautobot_firewall_models/inc/host_firewall.html", extra_context={"firewall": firewall})


class DeviceFirewall(HostFirewall):  # pylint: disable=abstract-method
    """Show a Device's Firewall."""

    model = "dcim.device"


class VirtualMachineFirewall(HostFirewall):  # pylint: disable=abstract-method
    """Show a Virtual Machine's Firewall."""

    model = "virtualization.virtualmachine"


template_extensions = [DeviceFirewall, VirtualMachineFirewall]
