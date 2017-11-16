from django.conf import settings
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

    def url(self):
        return settings.HH_URL + self.uri if self.uri is not None else None

    def image_url(self):
        return settings.HH_IMAGE_URL + self.image_uri if self.image_uri is not None else settings.HH_DEFAULT_IMAGE_URL

    def as_dict(self, **extend):
        item = {
            "id": self.code,
            "name": self.name,
            "url": self.url(),
            "image_url": self.image_url(),
        }
        item.update(extend)
        return item

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
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE, verbose_name="Customer")

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
    cluster_qa = models.ForeignKey("main.ClusterRecsReviewQA", on_delete=models.SET_NULL, null=True, blank=True)

    def is_cl_recs_review(self):
        return self.recs_type == self.RT_CLUSTER_BASED

    def __str__(self):
        return "%s review of %s's %s recs" % (self.reviewer, self.hh_user, self.recs_type)

    class Meta:
        verbose_name = "Recommendations review"
        ordering = ['-dt']


class RecsReviewQA(models.Model):
    item = models.ForeignKey(Item)
    position = models.IntegerField(
        verbose_name="Item position", validators=[MinValueValidator(0)]
    )

    cluster_id = models.IntegerField(null=True, blank=True)
    cluster_position = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )

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
        verbose_name="Selecting the best property was easy",
        default=None
    )
    happiness_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="I am happy with the property I have chosen",
        default=None
    )

    def __str__(self):
        return "%s" % self.pk

    class Meta:
        verbose_name = "QA about recommendations"
        verbose_name_plural = "QAs about recommendations"


class ClusterRecsReviewQA(models.Model):
    item = models.ForeignKey(Item, verbose_name="New item")
    position = models.IntegerField(
        verbose_name="New position", validators=[MinValueValidator(0)]
    )

    usefulness_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="Looking at these additional properties is useful for choosing the most relevant property",
        default=None
    )
    choice_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="Looking at these additional properties make easier to choose the most relevant property",
        default=None
    )

    def __str__(self):
        return "%s" % self.pk

    class Meta:
        verbose_name = "Cluster QA"
        verbose_name_plural = "Cluster QAs"
