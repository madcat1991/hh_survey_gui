# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-19 14:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_populate_hh_bookings'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='image_uri',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
