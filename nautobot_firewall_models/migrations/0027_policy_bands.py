import uuid

import django.core.serializers.json
import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.extras.models.mixins
from django.db import migrations, models


def require_no_policy_rules(apps, schema_editor):
    """Stop the upgrade if Policy Rules exist, since every rule now needs a Policy Band and there is no safe default."""
    PolicyRule = apps.get_model("nautobot_firewall_models", "PolicyRule")
    if PolicyRule.objects.exists():
        raise RuntimeError(
            "Policy Rules now require a Policy Band and position, and this migration does not assign them. "
            "Export and delete the existing Policy Rules, upgrade, create the Policy Bands, then re-import the rules."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0132_approval_workflow_seed_data"),
        ("nautobot_firewall_models", "0026_zone_devices"),
    ]

    operations = [
        migrations.RunPython(require_no_policy_rules, migrations.RunPython.noop),
        migrations.CreateModel(
            name="PolicyBand",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("index", models.PositiveSmallIntegerField(unique=True)),
                ("description", models.CharField(blank=True, max_length=1024)),
                ("tags", nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name_plural": "Policy Bands",
                "ordering": ["index"],
            },
            bases=(
                nautobot.extras.models.mixins.DataComplianceModelMixin,
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
                models.Model,
            ),
        ),
        migrations.AddField(
            model_name="policyrule",
            name="band",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="policy_rules",
                to="nautobot_firewall_models.policyband",
            ),
        ),
        migrations.AddField(
            model_name="policyrule",
            name="position",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterModelOptions(
            name="policyrule",
            options={
                "ordering": [
                    "band__index",
                    models.Case(models.When(position="header", then=0), default=1),
                    models.OrderBy(models.F("index"), nulls_last=True),
                    "name",
                ],
                "verbose_name_plural": "Policy Rules",
            },
        ),
    ]
