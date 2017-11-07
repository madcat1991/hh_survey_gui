from django.conf.urls import url

from main.views import HHUserListView, eval_hh_user_cluster_recs_view, eval_hh_user_item_recs_view

app_name = "main"
urlpatterns = [
    url(r'^$', HHUserListView.as_view(), name='hhuserlist'),
    url(r'^(?P<code>[\w0-9]+)/$', eval_hh_user_cluster_recs_view, name='hhusereval'),
    url(r'^item/(?P<code>[\w0-9]+)/$', eval_hh_user_item_recs_view, name='hhuseritemeval'),
]
