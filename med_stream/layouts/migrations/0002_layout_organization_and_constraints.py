import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("layouts", "0001_initial"),
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="layout",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="layouts",
                to="organizations.organization",
            ),
        ),
        migrations.AddConstraint(
            model_name="layout",
            constraint=models.UniqueConstraint(
                fields=("organization", "name"),
                name="uniq_layout_name_per_organization",
            ),
        ),
    ]
