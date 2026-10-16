from django.db import migrations, models


class Migration(migrations.Migration):
    """Split a Policy Rule's log into log at session start and log at session end.

    The existing log value carries over to log at session end. Log at session start is new and off.
    """

    dependencies = [
        ("nautobot_firewall_models", "0037_final_position"),
    ]

    operations = [
        migrations.RenameField(model_name="policyrule", old_name="log", new_name="log_end"),
        migrations.AlterField(
            model_name="policyrule",
            name="log_end",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="policyrule",
            name="log_start",
            field=models.BooleanField(default=False),
        ),
    ]
