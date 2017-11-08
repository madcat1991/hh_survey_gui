import django_tables2 as tables

from main.models import UserEvalCaseView


class UserEvalCaseViewTable(tables.Table):
    # code = tables.LinkColumn('main:hhusereval', args=[tables.A('pk')])

    class Meta:
        model = UserEvalCaseView
        order_by = ['is_reviewed']
        fields = ('hh_user', 'recs_type', 'is_reviewed')
        attrs = {'class': 'paleblue'}
