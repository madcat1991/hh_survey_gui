# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-07 16:27
from __future__ import unicode_literals

import csv
import random

from django.conf import settings
from django.db import migrations


MIN_GOOD_IIDS = 5
MAX_GOOD_IIDS = 10
N_GOOD_UIDS = 100


def get_uid_to_ug(ug_file_path):
    """ The function creates the index uid -> ug_id.

    :param ug_file_path: a path to the file containing information about user clusters
    :return: uid -> ug_id, dict
    """
    uid_to_ug = {}

    with open(ug_file_path) as f:
        # skipping
        while not next(f).startswith("Cluster"):
            pass

        cl_id = 0
        for line in f:
            if line.startswith("Users:"):
                for uid in line.lstrip("Users:").split(","):
                    uid = uid.strip()
                    uid_to_ug[uid] = cl_id
            elif line.startswith("Cluster"):
                cl_id += 1
    return uid_to_ug


def populate_hh_users(apps, schema_editor):
    Item = apps.get_model('main', 'Item')
    HHUser = apps.get_model('main', 'HHUser')

    uid_to_ug = get_uid_to_ug(settings.USER_CLUSTERS_JSON_PATH)

    good_iids = set(Item.objects.filter(uri__isnull=False).values_list('code', flat=True))

    # collecting good items of each user
    with open(settings.BOOKING_CSV_PATH) as f:
        csv_reader = csv.reader(f)
        next(csv_reader)  # skipping header

        uid_items = {}
        for row in csv_reader:
            if row:
                code, propcode = row[0], row[4]
                if code in uid_to_ug and propcode in good_iids:
                    uid_items.setdefault(code, set()).add(propcode)

    # selecting only users having from 5 to 10 good items
    good_uids = [
        uid for uid, iids in uid_items.items()
        if MIN_GOOD_IIDS <= len(iids) <= MAX_GOOD_IIDS
    ]
    print("Number of good uids: %s" % len(good_uids))

    # selecting users in such a way, that maximizes the coverage of clusters
    random.shuffle(good_uids)

    selected_ug_uid_pairs = {}
    for uid in good_uids:
        ug_id = uid_to_ug[uid]
        if ug_id not in selected_ug_uid_pairs:
            selected_ug_uid_pairs[ug_id] = uid
            if len(selected_ug_uid_pairs) == N_GOOD_UIDS:
                break
    print("Final number of hh users: %s" % len(selected_ug_uid_pairs))

    # selecting random
    for ug, uid in selected_ug_uid_pairs.items():
        user = HHUser(code=uid, cluster_id=uid_to_ug[uid])
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_populate_hh_items'),
    ]

    operations = [
        migrations.RunPython(populate_hh_users),
    ]
