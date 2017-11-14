# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-14 08:21
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_populate_hh_bookings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recsreview',
            options={'ordering': ['-dt'], 'verbose_name': 'Recommendations review'},
        ),
        migrations.AddField(
            model_name='recsreviewselecteditem',
            name='cluster_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recsreviewselecteditem',
            name='cluster_position',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='recsreview',
            name='qa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.RecsReviewQA'),
        ),
        migrations.AlterField(
            model_name='recsreviewqa',
            name='diversity_qa',
            field=models.CharField(choices=[('sa', 'Strongly agree'), ('ag', 'Agree'), ('nt', 'Neutral'), ('dg', 'Disagree'), ('sd', 'Strongly disagree')], default=None, max_length=2, verbose_name='The recommendations contained a lot of variety'),
        ),
        migrations.AlterField(
            model_name='recsreviewqa',
            name='easiness_qa',
            field=models.CharField(choices=[('sa', 'Strongly agree'), ('ag', 'Agree'), ('nt', 'Neutral'), ('dg', 'Disagree'), ('sd', 'Strongly disagree')], default=None, max_length=2, verbose_name='Selecting the best properties was easy'),
        ),
        migrations.AlterField(
            model_name='recsreviewqa',
            name='happiness_qa',
            field=models.CharField(choices=[('sa', 'Strongly agree'), ('ag', 'Agree'), ('nt', 'Neutral'), ('dg', 'Disagree'), ('sd', 'Strongly disagree')], default=None, max_length=2, verbose_name='I am happy with the properties I have chosen'),
        ),
        migrations.AlterField(
            model_name='recsreviewqa',
            name='quality_qa',
            field=models.CharField(choices=[('sa', 'Strongly agree'), ('ag', 'Agree'), ('nt', 'Neutral'), ('dg', 'Disagree'), ('sd', 'Strongly disagree')], default=None, max_length=2, verbose_name='I liked the recommendations provided by the system'),
        ),
        migrations.AlterField(
            model_name='recsreviewselecteditem',
            name='review',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='selected_item', to='main.RecsReview'),
        ),
    ]