from django.conf.urls import url

from main.views import UserEvalCaseListView, eval_hh_user_cluster_recs_view, eval_hh_user_item_recs_view

app_name = "main"
urlpatterns = [
    url(r'^$', UserEvalCaseListView.as_view(), name='evallist'),
    url(r'^cluster/(?P<code>[\w0-9]+)/$', eval_hh_user_cluster_recs_view, name='hhuserclustereval'),
    url(r'^item/(?P<code>[\w0-9]+)/$', eval_hh_user_item_recs_view, name='hhuseritemeval'),
]
