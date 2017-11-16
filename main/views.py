import json
import random

import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Max, Case, When, BooleanField
from django.shortcuts import render, get_object_or_404
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from main.describer.booking import describe_booking_cluster
from main.describer.user import describe_user
from main.filters import RecsReviewFilter
from main.forms import RecsReviewQAForm, ClusterRecsReviewQAForm
from main.models import Booking, Item, RecsReview
from main.table import RecsReviewTable


TOP_CLUSTER_RECS = TOP_ITEM_RECS = 3
TOP_ITEMS_PER_CLUSTER = 5


class RecsReviewListView(LoginRequiredMixin, FilterView, SingleTableView):
    model = RecsReview
    table_class = RecsReviewTable
    filterset_class = RecsReviewFilter

    template_name = 'main/recs_review_list.html'
    paginate_by = 15

    def get_queryset(self):
        return RecsReview.objects.filter(reviewer=self.request.user)\
            .annotate(is_reviewed=Case(
                When(qa__isnull=True, then=0),
                default=1,
                output_field=BooleanField()
            ))\
            .order_by('is_reviewed')


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
        ).as_dict()
        for item in items
    ]


def get_item_recs_cntx(code):
    req = requests.get(
        settings.API_ITEM_RECS_URL,
        params={"uid": code, "top": TOP_ITEM_RECS}
    )
    data = req.json()["result"]

    cntx = {}
    if data:
        # user part
        cntx["descr"] = describe_user(data["user"])

        # preparing output in the right order
        rec_iids = [rec["propcode"] for rec in data["recs"]]
        rec_items = {obj.pk: obj for obj in Item.objects.filter(pk__in=rec_iids)}
        cntx["items"] = [
            rec_items[iid].as_dict(pos=i_pos)
            for i_pos, iid in enumerate(rec_iids)
        ]
    return cntx


def get_cluster_recs_cntx(code):
    req = requests.get(
        settings.API_CLUSTER_RECS_URL,
        params={"uid": code, "top": TOP_CLUSTER_RECS, "top_items": TOP_ITEMS_PER_CLUSTER}
    )
    data = req.json()["result"]

    cntx = {}
    if data:
        # user part
        cntx["descr"] = describe_user(data["user"])

        # collecting all the data about items from different clusters
        rec_items = set([prop["propcode"] for rec in data["recs"] for prop in rec["properties"]])
        rec_items = {obj.pk: obj for obj in Item.objects.filter(pk__in=rec_items)}

        random.seed(code)  # making selection user-specific

        # preparing output data
        cntx["items"] = []
        rec_iid_cluster = {}
        for cl_pos, rec in enumerate(data["recs"]):
            cl_id = rec["bg_id"]

            # cluster items
            cluster_items = [
                rec_items[prop["propcode"]].as_dict(pos=i_pos)
                for i_pos, prop in enumerate(rec["properties"])
            ]

            # selecting an item from cluster_items for recommendations
            # items from different clusters can intersect
            relevant_pos = [i for i, obj in enumerate(cluster_items) if obj["id"] not in rec_iid_cluster]
            rec_item = cluster_items[random.choice(relevant_pos)]
            cntx["items"].append(rec_item)

            # collecting clusters data for each recommended item
            rec_iid = rec_item["id"]
            rec_iid_cluster[rec_iid] = {
                "id": cl_id,
                "pos": cl_pos,
                "descr": describe_booking_cluster(rec["features"]),
                "items": cluster_items
            }

        cntx["rec_iid_cluster"] = rec_iid_cluster
    return cntx


@login_required
@transaction.atomic
def recs_review_view(request, pk):
    review_obj = get_object_or_404(RecsReview.objects.select_related(), pk=pk, reviewer=request.user)

    if review_obj.recs_type == RecsReview.RT_CONTENT_BASED:
        cntx = get_item_recs_cntx(review_obj.hh_user.pk)
    else:
        cntx = get_cluster_recs_cntx(review_obj.hh_user.pk)

    def _get_item_obj_from_items(iid, item_objs):
        for i_obj in item_objs:
            if i_obj["id"] == iid:
                return i_obj
        return None

    error_messages = []
    if request.method == 'POST':
        qa_form = RecsReviewQAForm(request.POST, instance=review_obj.qa)
        if not qa_form.is_valid():
            error_messages.append("Failed to save the items QA form, please contact the administrator")

        cluster_qa_form = ClusterRecsReviewQAForm(request.POST, instance=review_obj.cluster_qa)
        if review_obj.is_cl_recs_review() and not cluster_qa_form.is_valid():
            error_messages.append("Failed to save the cluster QA form, please contact the administrator")

        # selected recommended item
        main_item = _get_item_obj_from_items(request.POST.get("items"), cntx["items"])
        if main_item is None:
            error_messages.append("Please select a property")

        if not error_messages:
            if review_obj.is_cl_recs_review():
                cluster_data = cntx["rec_iid_cluster"][main_item["id"]]

                # selected cluster item
                cluster_item = _get_item_obj_from_items(request.POST.get("cluster_items"), cluster_data["items"])
                if cluster_item is None:
                    cluster_item = main_item

                # cluster_qa
                cluster_qa_instance = cluster_qa_form.save(commit=False)
                cluster_qa_instance.item_id = cluster_item["id"]
                cluster_qa_instance.position = cluster_item["pos"]
                cluster_qa_instance.save()
                review_obj.cluster_qa = cluster_qa_instance

                # qa
                qa_instance = qa_form.save(commit=False)
                qa_instance.item_id = main_item["id"]
                qa_instance.position = main_item["pos"]
                qa_instance.cluster_id = cluster_data["id"]
                qa_instance.cluster_position = cluster_data["pos"]
                qa_instance.save()
                review_obj.qa = qa_instance
            else:
                # qa
                qa_instance = qa_form.save(commit=False)
                qa_instance.item_id = main_item["id"]
                qa_instance.position = main_item["pos"]
                qa_instance.save()
                review_obj.qa = qa_instance

            # update review
            review_obj.save()
            cntx["info_message"] = "The review has been successfully submitted"
    else:
        qa_form = RecsReviewQAForm(instance=review_obj.qa)
        cluster_qa_form = ClusterRecsReviewQAForm(instance=review_obj.cluster_qa)

    if review_obj.qa:
        cntx["selected_rec_iid"] = review_obj.qa.item_id

    if review_obj.cluster_qa:
        cntx["selected_cluster_iid"] = json.dumps({
            review_obj.qa.cluster_id: review_obj.cluster_qa.item_id
        })

    if review_obj.is_cl_recs_review():
        cntx["rec_iid_cluster"] = json.dumps(cntx["rec_iid_cluster"])

    cntx["qa_form"] = qa_form
    cntx["cluster_qa_form"] = cluster_qa_form
    cntx["last5_items"] = get_items_booked_by_user(review_obj.hh_user.pk, TOP_ITEMS_PER_CLUSTER)
    cntx["review_obj"] = review_obj
    cntx["error_messages"] = error_messages
    return render(request, "main/recs_review_form.html", context=cntx)
