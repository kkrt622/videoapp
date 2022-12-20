# Generated by Django 4.1.4 on 2022-12-20 04:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="uservideosettings",
            name="image_quality",
            field=models.CharField(
                choices=[("low", "低画質"), ("standard", "標準"), ("high", "高画質")],
                default="standard",
                max_length=20,
            ),
        ),
    ]