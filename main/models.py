from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


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

    class Meta:
        verbose_name = "Recommendations review"


class RecsReviewQA(models.Model):
    review = models.ForeignKey(RecsReview, on_delete=models.CASCADE)
    quality_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="I liked the recommendations provided by the system",
        blank=False,
    )
    diversity_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="The recommendations contained a lot of variety",
        blank=False,
    )
    easiness_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="Selecting the best properties was easy",
        blank=False,
    )
    happiness_qa = models.CharField(
        max_length=2,
        choices=LIKERT_SCALE,
        verbose_name="I am happy with the properties I have chosen",
        blank=False,
    )

    class Meta:
        verbose_name = "QA about recommendations"
        verbose_name_plural = "QAs about recommendations"


class RecsReviewSelectedItem(models.Model):
    review = models.ForeignKey(RecsReview, on_delete=models.CASCADE)
    item = models.ForeignKey(Item)
    position = models.IntegerField(
        verbose_name="Item position", validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "Selected item for a user"
        verbose_name_plural = "Selected items for a user"
        ordering = ['pk']


class AbstractUserEvalCase(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    hh_user = models.ForeignKey(HHUser, on_delete=models.CASCADE, verbose_name="HH user")
    recs_type = models.CharField(
        max_length=2,
        choices=RecsReview.RECS_TYPES,
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

    def get_absolute_url(self):
        if self.recs_type == RecsReview.RT_CLUSTER_BASED:
            return reverse("main:hhuserclustereval", args=[self.hh_user])
        elif self.recs_type == RecsReview.RT_CONTENT_BASED:
            return reverse("main:hhuseritemeval", args=[self.hh_user])
        raise Exception("Wrong recs_type value: %s" % self.recs_type)

    class Meta:
        ordering = ['hh_user']
        managed = False
        db_table = "main_userevalcase_view"
