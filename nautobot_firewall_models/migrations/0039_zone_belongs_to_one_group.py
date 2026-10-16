import django.db.models.deletion
from django.db import migrations, models


def assign_zone_groups(apps, schema_editor):
    """Give every Zone the one Zone Group it belongs to, or stop if a Zone has none or several."""
    Zone = apps.get_model("nautobot_firewall_models", "Zone")
    problems = []
    for zone in Zone.objects.all():
        groups = list(zone.zone_groups.all())
        if len(groups) != 1:
            problems.append(f"{zone.name} ({len(groups)} groups)")
            continue
        zone.zone_group = groups[0]
        zone.save()
    if problems:
        raise RuntimeError(
            "Every Zone must now belong to exactly one Zone Group. Fix the membership of these Zones, then upgrade: "
            + ", ".join(problems)
        )


def restore_zone_groups(apps, schema_editor):
    """Put each Zone back in its Zone Group's zone list."""
    Zone = apps.get_model("nautobot_firewall_models", "Zone")
    for zone in Zone.objects.all():
        zone.zone_group.zones.add(zone)


class Migration(migrations.Migration):
    """Bind each Zone to one required Zone Group, chosen on the Zone, in place of the Zone Group's zone list."""

    dependencies = [
        ("nautobot_firewall_models", "0038_policy_rule_log_start_end"),
    ]

    operations = [
        migrations.AddField(
            model_name="zone",
            name="zone_group",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="members",
                to="nautobot_firewall_models.zonegroup",
            ),
        ),
        migrations.RunPython(assign_zone_groups, restore_zone_groups),
        migrations.RemoveField(model_name="zonegroup", name="zones"),
        migrations.AlterField(
            model_name="zone",
            name="zone_group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="zones",
                to="nautobot_firewall_models.zonegroup",
            ),
        ),
    ]
