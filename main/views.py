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
from main.forms import RecsReviewQAForm
from main.models import Booking, Item, RecsReview, RecsReviewSelectedItem
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


@login_required
def eval_hh_user_cluster_recs_view(request, code):
    # WARNING!!! we assume that recommendations doesn't change over time!!!
    cntx = get_cluster_recs_cntx(code)
    cntx["code"] = code
    cntx["last5_items"] = get_items_booked_by_user(code, TOP_ITEMS_PER_CLUSTER)
    # cntx["cluster_review_answers"] = RecsClusterReview.REVIEW_ANSWERS
    # cntx["review_answers"] = RecsReview.REVIEW_ANSWERS

    error_messages = []
    if cntx["has_recs"]:
        if request.method == 'POST':
            # user review answer
            user_answer = request.POST.get("user_review")
            if user_answer:
                cntx["user_answer"] = user_answer
            else:
                error_messages.append(
                    "Fill the evaluation of the items selected for the user"
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
                        "Fill the evaluation of the item selected for the cluster #%s" % cl_id
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
                            "Select existing item for the cluster #%s" % cl_id
                        )
                else:
                    error_messages.append(
                        "Select an item for the cluster #%s" % cl_id
                    )

                # data to create/update cluster review objects
                cluster_review_data.append(
                    (cl_id, cl_pos, {"item_id": item_id, "item_pos": item_pos, "answer": cl_answer})
                )

            if not error_messages:
                r_obj, is_created = RecsReview.objects.update_or_create(
                    {"answer": user_answer}, reviewer=request.user, hh_user_id=code,
                    recs_type=RecsReview.RT_CLUSTER_BASED
                )

                # for cl_id, cl_pos, cl_dict in cluster_review_data:
                #     RecsClusterReview.objects.update_or_create(
                #         cl_dict, review=r_obj, cluster_id=cl_id, cluster_pos=cl_pos
                #     )

                cntx["info_message"] = "The review has been successfully submitted"
        else:
            try:
                recs_review_obj = RecsReview.objects.get(
                    reviewer=request.user, hh_user__pk=code,
                    recs_type=RecsReview.RT_CLUSTER_BASED
                )
            except RecsReview.DoesNotExist:
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
    return render(request, "main/hhuser_cluster_recs_eval.html", context=cntx)


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
        cntx["clusters"] = {}
        cntx["items"] = []
        for cl_pos, rec in enumerate(data["recs"]):
            cl_id = rec["bg_id"]

            cluster_items = [
                rec_items[prop["propcode"]].as_dict(pos=i_pos, cl_id=cl_id)
                for i_pos, prop in enumerate(rec["properties"])
            ]

            rec_item_pos = random.randrange(0, len(cluster_items))
            cntx["items"].append(cluster_items[rec_item_pos])

            cntx["clusters"][cl_id] = {
                "pos": cl_pos,
                "descr": describe_booking_cluster(rec["features"]),
                "items": cluster_items
            }
    return cntx


@login_required
@transaction.atomic
def recs_review_view(request, pk):
    review_obj = get_object_or_404(RecsReview.objects.select_related(), pk=pk, reviewer=request.user)

    if review_obj.recs_type == RecsReview.RT_CONTENT_BASED:
        cntx = get_item_recs_cntx(review_obj.hh_user.pk)
    else:
        cntx = get_cluster_recs_cntx(review_obj.hh_user.pk)

    error_messages = []
    if request.method == 'POST':
        qa_form = RecsReviewQAForm(request.POST, instance=review_obj.qa)

        # selected items
        selected_items = []
        selected_iids = set(request.POST.getlist("items", []))
        for i_pos, i_obj in enumerate(cntx["items"]):
            if i_obj["id"] in selected_iids:
                selected_items.append(i_obj)

        if len(selected_items) > 0:
            if qa_form.is_valid():
                # delete old items
                review_obj.selected_item.all().delete()

                # create news
                for i_obj in selected_items:
                    obj = RecsReviewSelectedItem(review=review_obj, item_id=i_obj["id"], position=i_obj["pos"])
                    if review_obj.recs_type == RecsReview.RT_CLUSTER_BASED:
                        cl = cntx["clusters"][i_obj["cl_id"]]
                        obj.cluster_id = i_obj["cl_id"]
                        obj.cluster_position = cl["pos"]
                    obj.save()

                # save QA
                qa_instance = qa_form.save()

                # update review
                review_obj.qa = qa_instance
                review_obj.save()

                cntx["info_message"] = "The review has been successfully submitted"
        else:
            error_messages.append("Please select at least one property")
    else:
        qa_form = RecsReviewQAForm(instance=review_obj.qa)
        selected_iids = {obj.item_id for obj in review_obj.selected_item.all()}

    for i_obj in cntx["items"]:
        if i_obj["id"] in selected_iids:
            i_obj["selected"] = True

    cntx["last5_items"] = get_items_booked_by_user(review_obj.hh_user.pk, TOP_ITEMS_PER_CLUSTER)
    cntx["qa_form"] = qa_form
    cntx["review_obj"] = review_obj
    cntx["error_messages"] = error_messages
    return render(request, "main/recs_review_form.html", context=cntx)
