# Generated by Django 2.2.1 on 2019-06-16 16:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0005_remove_property_viewed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='last_viewed',
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]