# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-16 17:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analyses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genomereference',
            name='newer_reference',
            field=models.ForeignKey(blank=True, help_text='If new version of the genome reference of the same organism and source exists, link the reference here. For example, UCSC mm9 can set its newer reference to UCSC mm10.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='analyses.GenomeReference', verbose_name='newer version'),
        ),
    ]
