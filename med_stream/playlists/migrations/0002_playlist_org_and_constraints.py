import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
        ("playlists", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="playlist",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="playlists",
                to="organizations.organization",
            ),
        ),
        migrations.AddConstraint(
            model_name="playlist",
            constraint=models.UniqueConstraint(
                fields=("organization", "name"),
                name="uniq_playlist_name_per_organization",
            ),
        ),
        migrations.AddConstraint(
            model_name="playlistitem",
            constraint=models.UniqueConstraint(
                fields=("playlist", "order"),
                name="uniq_playlist_item_order_per_playlist",
            ),
        ),
    ]
