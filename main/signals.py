import logging
import random

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from main.models import HHUser, RecsReview


logger = logging.getLogger(__name__)


@receiver(post_save, sender=User, dispatch_uid="user_on_insert")
def user_on_insert_handler(sender, instance, created, **kwargs):
    if created:
        logger.info('Creating evaluation cases for a user "%s"', instance)
        uids = HHUser.objects.values_list('code', flat=True)
        recs_types = [key for key, value in RecsReview.RECS_TYPES]
        pairs = [(uid, rt) for uid in uids for rt in recs_types]

        pairs = random.sample(pairs, RecsReview.N_REVIEW_PER_USER)

        for uid, rt in pairs:
            case = RecsReview(reviewer=instance, hh_user_id=uid, recs_type=rt)
            case.save()
        logger.info('Evaluation cases for a user "%s" have been created', instance)
