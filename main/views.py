import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, When, Case, BooleanField, Max
from django.shortcuts import render
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from main.filters import HHUserFilter
from main.models import HHUser, Booking, Item, HHUserRecsReview, RecsClusterReview
from main.table import HHUserTable


TOP_CLUSTER_RECS = TOP_ITEM_RECS = 3
TOP_ITEMS_PER_CLUSTER = 5


class HHUserListView(LoginRequiredMixin, FilterView, SingleTableView):
    model = HHUser
    table_class = HHUserTable
    filterset_class = HHUserFilter

    template_name = 'main/hhuser_list.html'
    paginate_by = 20

    def get_queryset(self):
        # WARNING!!! we assume that recommendations doesn't change over time!!!
        return HHUser.objects\
            .annotate(
                n_reviews=Count("review__reviewer")
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


def get_cluster_recs_cntx(code):
    req = requests.get(
        settings.API_CLUSTER_RECS_URL,
        params={"uid": code, "top": TOP_CLUSTER_RECS, "top_items": TOP_ITEMS_PER_CLUSTER}
    )
    data = req.json()["result"]

    cntx = {}
    if data:
        cntx["has_recs"] = True

        # user part
        cl_id, cl_descr = list(data["user_cluster"].items())[0]
        cntx["cluster_id"] = cl_id
        cntx["cluster_descr"] = cl_descr
        cntx["descr"] = data["user"]
        cntx["bookings_summary"] = data["prev_bookings_summary"]

        # collecting all the data about items from different clusters
        recommended_items = set([prop["propcode"] for rec in data["recs"] for prop in rec["properties"]])
        recommended_items = {obj.pk: obj for obj in Item.objects.filter(pk__in=recommended_items)}

        # preparing output data describing clusters
        cntx["clusters"] = []
        for rec in data["recs"]:
            cluster_items = [
                {"id": prop["propcode"], "obj": recommended_items[prop["propcode"]]}
                for prop in rec["properties"]
            ]

            cntx["clusters"].append({
                "id": rec["bg_id"],
                "features": rec["features"],
                "items": cluster_items
            })
    else:
        cntx["has_recs"] = False
    return cntx


def get_item_recs_cntx(code):
    req = requests.get(
        settings.API_ITEM_RECS_URL,
        params={"uid": code, "top": TOP_ITEM_RECS}
    )
    data = req.json()["result"]

    cntx = {}
    if data:
        cntx["has_recs"] = True

        # user part
        cntx["descr"] = data["user"]
        cntx["bookings_summary"] = data["prev_bookings_summary"]

        # preparing output in the right order
        rec_iids = [rec["propcode"] for rec in data["recs"]]
        rec_item_objs = {obj.pk: obj for obj in Item.objects.filter(pk__in=rec_iids)}
        cntx["items"] = [{"id": iid, "obj": rec_item_objs[iid]} for iid in rec_iids]
    else:
        cntx["has_recs"] = False
    return cntx


@login_required
def eval_hh_user_cluster_recs_view(request, code):
    # WARNING!!! we assume that recommendations doesn't change over time!!!
    cntx = get_cluster_recs_cntx(code)
    cntx["code"] = code
    cntx["last5_items"] = get_items_booked_by_user(code, TOP_ITEMS_PER_CLUSTER)
    cntx["cluster_review_answers"] = RecsClusterReview.REVIEW_ANSWERS
    cntx["review_answers"] = HHUserRecsReview.REVIEW_ANSWERS

    error_messages = []
    if cntx["has_recs"]:
        if request.method == 'POST':
            # user review answer
            user_answer = request.POST.get("user_review")
            if user_answer:
                cntx["user_answer"] = user_answer
            else:
                error_messages.append(
                    "Fill the evaluation of the selected for the user items"
                )

            # cluster evaluation
            cluster_review_data = []
            for cl_pos, cl_obj in enumerate(cntx["clusters"]):
                cl_id = cl_obj["id"]

                # cluster review
                cl_answer = request.POST.get("cluster_%s_reviews" % cl_id)
                if cl_answer:
                    cl_obj["answer"] = cl_answer
                else:
                    error_messages.append(
                        "Fill the evaluation of the item selected for cluster %s" % cl_id
                    )

                # selected item
                item_id = item_pos = None
                selected_item = request.POST.get("cluster_%s_items" % cl_id)
                if selected_item:
                    selected_item = selected_item.replace("item_", "")
                    for i_pos, i_obj in enumerate(cl_obj["items"]):
                        if i_obj["id"] == selected_item:
                            item_id, item_pos = selected_item, i_pos
                            i_obj["selected"] = True
                            break
                    else:
                        error_messages.append(
                            "Select existing item for cluster %s" % cl_id
                        )
                else:
                    error_messages.append(
                        "Select item for cluster %s" % cl_id
                    )

                # data to create/update cluster review objects
                cluster_review_data.append(
                    (cl_id, cl_pos, {"item_id": item_id, "item_pos": item_pos, "answer": cl_answer})
                )

            if not error_messages:
                r_obj, is_created = HHUserRecsReview.objects.update_or_create(
                    {"answer": user_answer}, reviewer=request.user, hh_user_id=code,
                    recs_type=HHUserRecsReview.RT_CLUSTER_BASED
                )

                for cl_id, cl_pos, cl_dict in cluster_review_data:
                    RecsClusterReview.objects.update_or_create(
                        cl_dict, review=r_obj, cluster_id=cl_id, cluster_pos=cl_pos
                    )

                cntx["info_message"] = "The review has been successfully stored"
        else:
            try:
                recs_review_obj = HHUserRecsReview.objects.get(
                    reviewer=request.user, hh_user__pk=code,
                    recs_type=HHUserRecsReview.RT_CLUSTER_BASED
                )
            except HHUserRecsReview.DoesNotExist:
                recs_review_obj = None

            if recs_review_obj is not None:
                cntx["user_answer"] = recs_review_obj.answer

                cluster_reviews = {
                    obj.cluster_id: (obj.item_id, obj.answer)
                    for obj in recs_review_obj.cluster_review.all()
                }

                # populating selections within a cluster
                for cl_obj in cntx["clusters"]:
                    item_id, answer = cluster_reviews[cl_obj["id"]]
                    cl_obj["answer"] = answer
                    for i_obj in cl_obj["items"]:
                        if item_id == i_obj["id"]:
                            i_obj["selected"] = True
                            break

    cntx["error_messages"] = error_messages
    return render(request, "main/hhuser_eval.html", context=cntx)


@login_required
def eval_hh_user_item_recs_view(request, code):
    # WARNING!!! we assume that recommendations doesn't change over time!!!
    cntx = get_item_recs_cntx(code)
    cntx["code"] = code
    cntx["last5_items"] = get_items_booked_by_user(code, TOP_ITEMS_PER_CLUSTER)
    cntx["review_answers"] = HHUserRecsReview.REVIEW_ANSWERS

    error_messages = []
    if cntx["has_recs"]:
        if request.method == 'POST':
            # user review answer
            user_answer = request.POST.get("user_review")
            if user_answer:
                cntx["user_answer"] = user_answer
            else:
                error_messages.append(
                    "Fill the evaluation of the selected for the user items"
                )

            if not error_messages:
                HHUserRecsReview.objects.update_or_create(
                    {"answer": user_answer}, reviewer=request.user, hh_user_id=code,
                    recs_type=HHUserRecsReview.RT_CONTENT_BASED
                )
                cntx["info_message"] = "The review has been successfully stored"
        else:
            try:
                recs_review_obj = HHUserRecsReview.objects.get(
                    reviewer=request.user, hh_user__pk=code,
                    recs_type=HHUserRecsReview.RT_CONTENT_BASED
                )
            except HHUserRecsReview.DoesNotExist:
                recs_review_obj = None

            if recs_review_obj is not None:
                cntx["user_answer"] = recs_review_obj.answer

    cntx["error_messages"] = error_messages
    return render(request, "main/hhuser_item_recs_eval.html", context=cntx)
