# Generated by Django 4.1.4 on 2022-12-19 07:06

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"verbose_name_plural": "User"},
        ),
        migrations.AddField(
            model_name="user",
            name="follow",
            field=models.ManyToManyField(
                related_name="followed", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="icon",
            field=models.ImageField(blank=True, upload_to="icon/", verbose_name="アイコン"),
        ),
        migrations.AddField(
            model_name="user",
            name="profile",
            field=models.TextField(max_length=500, null=True, verbose_name="プロフィール"),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="メールアドレス"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(max_length=50, null=True, verbose_name="ユーザ名"),
        ),
    ]
