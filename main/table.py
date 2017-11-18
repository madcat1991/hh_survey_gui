from django_tables2 import A, Table, LinkColumn, BooleanColumn

from main.models import RecsReview


class RecsReviewTable(Table):
    hh_user = LinkColumn("main:recsreviewview", args=[A('pk')])
    is_reviewed = BooleanColumn()

    class Meta:
        model = RecsReview
        order_by = ['hh_user']
        fields = ('hh_user', 'recs_type', 'is_reviewed')
        attrs = {'class': 'paleblue'}
