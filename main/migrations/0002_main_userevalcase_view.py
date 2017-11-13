# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-13 10:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("DROP VIEW IF EXISTS main_recsreview_view;"),
        migrations.RunSQL("""
                CREATE VIEW main_recsreview_view 
                AS 
                SELECT 
                    c.id,
                    c.reviewer_id,
                    c.hh_user_id, 
                    c.recs_type,
                    CASE WHEN r.id IS NULL THEN 0 ELSE 1 END AS is_reviewed
                FROM main_userevalcase c
                    JOIN main_hhuser h ON c.hh_user_id = h.code
                    LEFT JOIN  main_recsreview r ON c.hh_user_id = r.hh_user_id 
                        AND c.reviewer_id = r.reviewer_id
                        AND c.recs_type = r.recs_type;
            """),
    ]
