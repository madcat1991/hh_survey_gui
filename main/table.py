import django_tables2 as tables

from main.models import UserEvalCaseView


class UserEvalCaseViewTable(tables.Table):
    hh_user = tables.LinkColumn()

    class Meta:
        model = UserEvalCaseView
        order_by = ['is_reviewed']
        fields = ('hh_user', 'recs_type', 'is_reviewed')
        attrs = {'class': 'paleblue'}
