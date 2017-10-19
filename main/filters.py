import django_filters

from main.models import HHUser


class HHUserFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(lookup_expr='icontains')
    is_reviewed = django_filters.BooleanFilter(label='Is reviewed')

    class Meta:
        model = HHUser
        fields = ['code', 'is_reviewed']

