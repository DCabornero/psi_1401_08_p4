# Generated by Django 2.2.6 on 2019-11-01 19:00

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0011_auto_20191101_1858'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
