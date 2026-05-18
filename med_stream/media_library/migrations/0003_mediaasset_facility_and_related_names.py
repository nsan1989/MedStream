import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facilities", "0011_alter_facility_facility_admin_and_more"),
        ("media_library", "0002_mediaasset_organization_and_constraints"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mediaasset",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="media_organization",
                to="organizations.organization",
            ),
        ),
        migrations.AddField(
            model_name="mediaasset",
            name="facility",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="media_facility",
                to="facilities.facility",
            ),
        ),
    ]
