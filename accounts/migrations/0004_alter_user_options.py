# Generated by Django 4.1.4 on 2022-12-20 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_alter_user_username"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name_plural": "ユーザー"},
        ),
    ]