# Generated by Django 2.2.6 on 2019-11-01 18:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0010_auto_20191101_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 11, 1, 18, 58, 51, 280285)),
        ),
    ]
