"""Constants file."""

from django.conf import settings

PLUGIN_CFG = settings.PLUGINS_CONFIG.get("nautobot_firewall_models", {})

# This is used to determine which status slug names are valid
ALLOW_STATUS = ["Active"]
if PLUGIN_CFG.get("allowed_status"):
    ALLOW_STATUS = PLUGIN_CFG["allowed_status"]
