# Generated by Django 5.0.3 on 2024-04-09 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_player_channel_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="player",
            old_name="channel_id",
            new_name="channel_name",
        ),
    ]
