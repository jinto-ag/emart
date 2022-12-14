# Generated by Django 4.1.1 on 2022-09-30 04:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_wishlistmodel_products"),
    ]

    operations = [
        migrations.AddField(
            model_name="wishlistmodel",
            name="created_on",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="wishlistmodel",
            name="status",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="wishlistmodel",
            name="updated_on",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
