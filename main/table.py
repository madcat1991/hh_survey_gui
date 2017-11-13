from django_tables2 import A, Table, LinkColumn

from main.models import RecsReview


class RecsReviewTable(Table):
    hh_user = LinkColumn("main:recsreviewview", args=[A('pk')])

    class Meta:
        model = RecsReview
        order_by = ['is_reviewed']
        fields = ('hh_user', 'recs_type', 'is_reviewed')
        attrs = {'class': 'paleblue'}
