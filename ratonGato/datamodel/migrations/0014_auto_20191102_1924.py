# Generated by Django 2.2.6 on 2019-11-02 19:24

import datamodel.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0013_auto_20191101_2225'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='cat_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='games_as_cat', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='game',
            name='mouse_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='games_as_mouse', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='game',
            name='status',
            field=datamodel.models.GameStatus(blank=True, choices=[(0, 0), (1, 1), (2, 2)], default=0),
        ),
    ]
