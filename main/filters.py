import django_filters

from main.models import RecsReview


class RecsReviewFilter(django_filters.FilterSet):
    hh_user__pk = django_filters.CharFilter(label='HH user', lookup_expr='icontains')
    is_reviewed = django_filters.BooleanFilter(label='Is reviewed')

    class Meta:
        model = RecsReview
        fields = ['hh_user__pk', 'is_reviewed']

