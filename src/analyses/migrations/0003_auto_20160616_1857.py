# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-16 18:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyses', '0002_auto_20160616_1724'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='genomereference',
            options={'get_latest_by': 'release_date', 'ordering': ('organism', 'source', '-release_date')},
        ),
        migrations.AddField(
            model_name='genomereference',
            name='release_date',
            field=models.DateField(blank=True, help_text='The date this genome reference is released.', null=True, verbose_name='Release date'),
        ),
    ]
