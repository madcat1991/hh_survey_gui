import django_tables2 as tables

from main.models import HHUser


class HHUserTable(tables.Table):
    code = tables.LinkColumn('main:hhusereval', args=[tables.A('pk')])

    class Meta:
        model = HHUser
        order_by = ('is_reviewed', 'n_reviewers')
        fields = ('code', 'n_reviewers', 'is_reviewed')
        attrs = {'class': 'paleblue'}
