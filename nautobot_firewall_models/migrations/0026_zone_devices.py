from django.db import migrations, models


def bind_zones_to_interface_devices(apps, schema_editor):
    """Bind each Zone to the Devices that own the Interfaces already assigned to it."""
    Zone = apps.get_model("nautobot_firewall_models", "Zone")
    through = Zone.devices.through
    rows = Zone.interfaces.through.objects.values_list("zone_id", "interface__device_id").distinct()
    through.objects.bulk_create(
        [through(zone_id=zone_pk, device_id=device_pk) for zone_pk, device_pk in rows if device_pk],
        ignore_conflicts=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0014_location_status_data_migration"),
        ("nautobot_firewall_models", "0025_zone_groups"),
    ]

    operations = [
        migrations.AddField(
            model_name="zone",
            name="devices",
            field=models.ManyToManyField(blank=True, related_name="zones", to="dcim.device"),
        ),
        migrations.RunPython(bind_zones_to_interface_devices, migrations.RunPython.noop),
    ]
