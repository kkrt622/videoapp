# Generated by Django 4.1.4 on 2023-01-02 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_alter_user_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=50, verbose_name="ユーザ名"),
        ),
    ]