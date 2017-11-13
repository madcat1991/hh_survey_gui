from django.conf.urls import url

from main.views import RecsReviewListView, recs_review_view

app_name = "main"
urlpatterns = [
    url(r'^$', RecsReviewListView.as_view(), name='recsreviewlist'),
    url(r'^review/(?P<pk>[\w0-9]+)/$', recs_review_view, name='recsreviewview'),
]
