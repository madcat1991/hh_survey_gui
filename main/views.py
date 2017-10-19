import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, When, Case, BooleanField, Max
from django.shortcuts import render
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from main.filters import HHUserFilter
from main.models import HHUser, Booking
from main.table import HHUserTable


TOP_CLUSTERS = 3
TOP_ITEMS = 5


class HHUserListView(LoginRequiredMixin, FilterView, SingleTableView):
    model = HHUser
    table_class = HHUserTable
    filterset_class = HHUserFilter

    template_name = 'main/hhuser_list.html'
    paginate_by = 20

    def get_queryset(self):
        return HHUser.objects\
            .annotate(
                n_reviewers=Count("review__reviewer", distinct=True)
            )\
            .annotate(
                n_reviews_by_current_user=Count(
                    Case(
                        When(review__reviewer=self.request.user, then=1),
                        default=None
                    )
                )
            )\
            .annotate(
                is_reviewed=Case(
                    When(n_reviews_by_current_user__gt=0, then=True),
                    default=False,
                    output_field=BooleanField()
                ),
            )


@login_required
def eval_hh_user_view(request, code):
    req = requests.get(
        settings.API_URL,
        params={"uid": code, "top": TOP_CLUSTERS, "top_items": TOP_ITEMS}
    )
    data = req.json()["result"]

    cntx = {
        "code": code,
    }

    if data:
        cntx["has_recs"] = True
        cntx["descr"] = data["user"]
        cntx["bookings_summary"] = data["prev_bookings_summary"]

        cntx["last5_items"] = Booking.objects \
            .filter(hh_user__pk=code) \
            .values('item', 'item__name', 'item__uri', 'item__image_uri') \
            .annotate(max_dt=Max('dt')) \
            .order_by('-max_dt')[:TOP_ITEMS]

        for cl_id, cl_descr in data["user_cluster"].items():
            cntx["cluster_id"] = cl_id
            cntx["cluster_descr"] = cl_descr
            break
    else:
        cntx["info_msg"] = "No recommendations for user %s" % code

    return render(request, "main/hhuser_eval.html", context=cntx)
