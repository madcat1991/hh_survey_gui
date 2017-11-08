from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
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

    def __str__(self):
        return self.code

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
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE, related_name='review')

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
        return 'User "%s" about %s recs of HH user "%s": %s' % \
               (self.reviewer, self.recs_type, self.hh_user, self.answer)

    class Meta:
        verbose_name = "HH user recommendations review"
        ordering = ['-dt']


class RecsClusterReview(models.Model):
    cluster_id = models.IntegerField(
        verbose_name="Item cluster id", validators=[MinValueValidator(0)], null=True,
    )
    cluster_pos = models.IntegerField(
        verbose_name="Cluster position", validators=[MinValueValidator(0)], null=True,
    )

    item = models.ForeignKey(Item)
    item_pos = models.IntegerField(
        verbose_name="Item position", validators=[MinValueValidator(0)]
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

    review = models.ForeignKey(HHUserRecsReview, on_delete=models.CASCADE, related_name="cluster_review")
    dt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recommended cluster review"
        ordering = ['-dt']


class AbstractUserEvalCase(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE, verbose_name="HH user")
    recs_type = models.CharField(
        max_length=2,
        choices=HHUserRecsReview.RECS_TYPES,
        verbose_name="Type of recommendations",
        blank=False
    )

    class Meta:
        abstract = True


class UserEvalCase(AbstractUserEvalCase):
    N_CASES_PER_USER = 60

    class Meta:
        verbose_name = "User evaluation case"


class UserEvalCaseView(AbstractUserEvalCase):
    is_reviewed = models.BooleanField()

    class Meta:
        managed = False
        db_table = "main_userevalcase_view"
