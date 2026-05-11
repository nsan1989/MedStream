import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("media_library", "0001_initial"),
        ("organizations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mediaasset",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="media_assets",
                to="organizations.organization",
            ),
        ),
        migrations.AddConstraint(
            model_name="mediaasset",
            constraint=models.UniqueConstraint(
                fields=("organization", "title"),
                name="uniq_media_asset_title_per_organization",
            ),
        ),
    ]
