# Generated by Django 2.2.6 on 2019-11-01 16:13

import datamodel.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cat1', models.IntegerField(blank=True)),
                ('cat2', models.IntegerField(blank=True)),
                ('cat3', models.IntegerField(blank=True)),
                ('cat4', models.IntegerField(blank=True)),
                ('mouse', models.IntegerField(blank=True)),
                ('cat_turn', models.BooleanField(blank=True)),
                ('status', datamodel.models.GameStatus(blank=True, choices=[('CREATED', 'CREATED'), ('ACTIVE', 'ACTIVE'), ('FINISHED', 'FINISHED')])),
                ('cat_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Cat_user_foreign_key', to=settings.AUTH_USER_MODEL)),
                ('mouse_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Mouse_user_foreign_key', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin', models.IntegerField(blank=True)),
                ('target', models.IntegerField(blank=True)),
                ('date', models.DateTimeField(blank=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datamodel.Game')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
