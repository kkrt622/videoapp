# Generated by Django 4.1.4 on 2023-02-06 05:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0013_delete_videocomment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authenticationcode",
            name="code",
            field=models.CharField(max_length=4, verbose_name="認証コード"),
        ),
    ]
