from django.conf.urls import url

from main.views import UserEvalCaseListView, eval_hh_user_cluster_recs_view, eval_hh_user_item_recs_view

app_name = "main"
urlpatterns = [
    url(r'^$', UserEvalCaseListView.as_view(), name='hhuserlist'),
    url(r'^(?P<code>[\w0-9]+)/$', eval_hh_user_cluster_recs_view, name='hhusereval'),
    url(r'^item/(?P<code>[\w0-9]+)/$', eval_hh_user_item_recs_view, name='hhuseritemeval'),
]
