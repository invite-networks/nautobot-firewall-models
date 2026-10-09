from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("nautobot_firewall_models", "0023_alter_addressobject_description_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CapircaPolicy",
        ),
    ]
