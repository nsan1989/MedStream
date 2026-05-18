import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("facilities", "0011_alter_facility_facility_admin_and_more"),
        ("playlists", "0002_playlist_org_and_constraints"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlist",
            name="facility",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="playlists",
                to="facilities.facility",
            ),
        ),
    ]
