# Generated by Django 4.1.4 on 2023-01-20 03:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_alter_video_video_delete_uservideosettings"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_registered",
        ),
    ]
