import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, When, Case, BooleanField, Max
from django.shortcuts import render
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from main.filters import HHUserFilter
from main.models import HHUser, Booking, Item, ItemClusterReview
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


def get_items_booked_by_user(code, n_latest):
    items = Booking.objects \
        .filter(hh_user__pk=code) \
        .values('item', 'item__name', 'item__uri', 'item__image_uri') \
        .annotate(max_dt=Max('dt')) \
        .order_by('-max_dt')[:n_latest]
    return [
        Item(
            code=item["item"],
            name=item["item__name"],
            uri=item["item__uri"],
            image_uri=item["item__image_uri"]
        )
        for item in items
    ]


def get_recs_cntx(code):
    req = requests.get(
        settings.API_URL,
        params={"uid": code, "top": TOP_CLUSTERS, "top_items": TOP_ITEMS}
    )
    data = req.json()["result"]

    cntx = {}
    if data:
        cntx["has_recs"] = True
        cntx["descr"] = data["user"]
        cntx["bookings_summary"] = data["prev_bookings_summary"]

        # user cluster info
        cl_id, cl_descr = list(data["user_cluster"].items())[0]
        cntx["cluster_id"] = cl_id
        cntx["cluster_descr"] = cl_descr

        recommended_items = set([prop["propcode"] for rec in data["recs"] for prop in rec["properties"]])
        recommended_items = {obj.pk: obj for obj in Item.objects.filter(pk__in=recommended_items)}

        cntx["clusters"] = []
        for rec in data["recs"]:
            cluster_data = {
                "cluster_id": rec["bg_id"],
                "features": rec["features"],
                "items": [recommended_items[prop["propcode"]] for prop in rec["properties"]]
            }
            cntx["clusters"].append(cluster_data)
    else:
        cntx["has_recs"] = False
    return cntx


@login_required
def eval_hh_user_view(request, code):
    reviews_by_cl_ids = {
        obj.item_cluster_id: obj
        for obj in ItemClusterReview.objects.filter(reviewer=request.user, hh_user__pk=code)
    }

    cntx = get_recs_cntx(code)
    cntx["code"] = code
    cntx["last5_items"] = get_items_booked_by_user(code, TOP_ITEMS)

    if cntx["has_recs"]:
        if request.method == 'POST':
            cntx["info_msg"] = "Reviews for HH user %s have been updated" % code
            cluster_ids = [cluster["cluster_id"] for cluster in cntx["clusters"]]
            for cl_id in cluster_ids:
                key = 'review_cluster_%s' % cl_id
                review_text = request.POST.get(key, "").strip()

                review_obj = reviews_by_cl_ids.get(cl_id)
                if review_obj is None and review_text:
                    review_obj = ItemClusterReview(
                        reviewer=request.user,
                        item_cluster_id=cl_id,
                        review_text=review_text
                    )
                    review_obj.hh_user_id = code
                    review_obj.save()
                    reviews_by_cl_ids[cl_id] = review_obj
                elif review_obj is not None:
                    if not review_text:
                        review_obj.delete()
                        reviews_by_cl_ids.pop(cl_id)
                    elif review_obj.review_text != review_text:
                        review_obj.review_text = review_text
                        review_obj.save()

        for cluster in cntx["clusters"]:
            cl_id = cluster["cluster_id"]
            cluster["review"] = reviews_by_cl_ids[cl_id].review_text if cl_id in reviews_by_cl_ids else ""

    return render(request, "main/hhuser_eval.html", context=cntx)
