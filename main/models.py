from django.contrib.auth.models import User
from django.db import models


class HHUser(models.Model):
    code = models.CharField(max_length=11, unique=True, primary_key=True, verbose_name="user id")
    cluster_id = models.IntegerField(unique=True, verbose_name="user cluster id")

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "HH user"
        ordering = ['code']


class ItemClusterReview(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE)
    item_cluster_id = models.IntegerField(verbose_name="item cluster id")
    review_text = models.TextField(verbose_name="Review")
    dt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-dt']


class Item(models.Model):
    code = models.CharField(max_length=6, unique=True, primary_key=True, verbose_name="item id")
    uri = models.CharField(max_length=200, null=True)
    image_uri = models.CharField(max_length=200, null=True)
    name = models.CharField(max_length=200, null=True)

    class Meta:
        ordering = ['code']


class Booking(models.Model):
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE, related_name='booking')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    dt = models.DateTimeField()

    class Meta:
        ordering = ['-dt']


class UserReviewedHHUser(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE, related_name='review')
    dt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-dt']
