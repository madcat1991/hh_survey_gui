# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-09 16:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_userevalcaseview'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userevalcaseview',
            options={'managed': False, 'ordering': ['hh_user']},
        ),
        migrations.AlterField(
            model_name='hhuserrecsreview',
            name='answer',
            field=models.CharField(choices=[('1', "All the items match the user's preference and have a high variety"), ('2', "All the items match the user's preference, but are similar to each other"), ('3', "Some of the items match the user's preference"), ('4', "The items don't match the user's preference")], default='1', max_length=1, verbose_name='Review'),
        ),
        migrations.AlterField(
            model_name='recsclusterreview',
            name='answer',
            field=models.CharField(choices=[('1', 'The property perfectly fits the user'), ('2', "The property doesn't completely fit the user, but the cluster does"), ('3', "The property doesn't fit the user, but the cluster does"), ('4', 'Neither the property nor the cluster fit the user')], default='1', max_length=1, verbose_name='Review'),
        ),
        migrations.AlterField(
            model_name='userevalcase',
            name='hh_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.HHUser', verbose_name='HH user'),
        ),
    ]
