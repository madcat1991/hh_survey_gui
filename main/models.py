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


class HHUserRecsReview(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE)

    RA_1 = "1"
    RA_2 = "2"
    RA_3 = "3"
    RA_4 = "4"
    REVIEW_ANSWERS = (
        (RA_1, "Answer 1"),
        (RA_2, "Answer 2"),
        (RA_3, "Answer 3"),
        (RA_4, "Answer 4"),
    )
    answer = models.CharField(
        max_length=1,
        choices=REVIEW_ANSWERS,
        default=RA_1,
        verbose_name="Review",
        blank=False,
    )

    RT_CONTENT_BASED = "cb"
    RT_CLUSTER_BASED = "cl"
    RECS_TYPES = (
        (RT_CONTENT_BASED, "Content-based"),
        (RT_CLUSTER_BASED, "Cluster-based")
    )
    recs_type = models.CharField(
        max_length=2,
        choices=RECS_TYPES,
        default=RT_CLUSTER_BASED,
        verbose_name="Type of recommendations",
        blank=False,
    )
    dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s about '%s' recs of %s: %s" % \
               (self.reviewer, self.recs_type, self.hh_user, self.answer)


class RecsItemReview(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_pos = models.IntegerField(
        verbose_name="Item position", validators=[MinValueValidator(0)]
    )

    cluster_id = models.IntegerField(
        verbose_name="Item cluster id", validators=[MinValueValidator(0)], null=True,
    )
    cluster_pos = models.IntegerField(
        verbose_name="Cluster position", validators=[MinValueValidator(0)], null=True,
    )

    RA_1 = "1"
    RA_2 = "2"
    RA_3 = "3"
    RA_4 = "4"
    REVIEW_ANSWERS = (
        (RA_1, "Answer 1"),
        (RA_2, "Answer 2"),
        (RA_3, "Answer 3"),
        (RA_4, "Answer 4"),
    )
    answer = models.CharField(
        max_length=1,
        choices=REVIEW_ANSWERS,
        default=RA_1,
        verbose_name="Review",
        blank=False,
    )

    user_review = models.ForeignKey(HHUserRecsReview, on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now=True)
