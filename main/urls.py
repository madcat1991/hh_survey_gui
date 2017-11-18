from django.conf.urls import url

from main.views import RecsReviewListView, recs_review_view, property_view

app_name = "main"
urlpatterns = [
    url(r'^$', RecsReviewListView.as_view(), name='recsreviewlist'),
    url(r'^review/(?P<pk>\d+)/$', recs_review_view, name='recsreviewview'),
    url(r'^property/(?P<propcode>[\w0-9]+)/$', property_view, name='propertyview'),
]
