# Generated by Django 4.1.4 on 2022-12-19 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_alter_user_options_user_follow_user_icon_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=50, unique=True, verbose_name="ユーザ名"),
        ),
    ]
