from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


LIKERT_SCALE = (
    ("sa", "Strongly agree"),
    ("ag", "Agree"),
    ("nt", "Neutral"),
    ("dg", "Disagree"),
    ("sd", "Strongly disagree"),
)


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


class RecsReview(models.Model):
    N_REVIEW_PER_USER = 60

    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE, verbose_name="HH user")

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
    qa = models.ForeignKey("main.RecsReviewQA", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return "%s review of %s's %s recs" % (self.reviewer, self.hh_user, self.recs_type)

    class Meta:
        verbose_name = "Recommendations review"
        ordering = ['-dt']


class RecsReviewQA(models.Model):
    quality_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="I liked the recommendations provided by the system",
        default=None
    )
    diversity_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="The recommendations contained a lot of variety",
        default=None
    )
    easiness_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="Selecting the best properties was easy",
        default=None
    )
    happiness_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="I am happy with the properties I have chosen",
        default=None
    )

    def __str__(self):
        return "%s" % self.pk

    class Meta:
        verbose_name = "QA about recommendations"
        verbose_name_plural = "QAs about recommendations"


class RecsReviewSelectedItem(models.Model):
    review = models.ForeignKey(RecsReview, on_delete=models.CASCADE, related_name='selected_item')
    item = models.ForeignKey(Item)
    position = models.IntegerField(
        verbose_name="Item position", validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return "%s" % self.pk

    class Meta:
        verbose_name = "Selected item for a user"
        verbose_name_plural = "Selected items for a user"
        ordering = ['pk']
