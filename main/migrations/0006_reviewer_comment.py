# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 12:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_text_changes'),
    ]

    operations = [
        migrations.AddField(
            model_name='recsreview',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Reviewer comment'),
        ),
    ]
