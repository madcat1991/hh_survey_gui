from django.contrib import admin
from main.models import HHUser, RecsReview, RecsReviewQA, ClusterRecsReviewQA


class HHUserAdmin(admin.ModelAdmin):
    list_display = ('code', 'cluster_id')


class RecsReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'reviewer', 'hh_user', 'recs_type', 'qa', 'cluster_qa', 'dt')


class RecsReviewQAAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'item', 'position', 'cluster_id', 'cluster_position',
        'quality_qa', 'diversity_qa', 'easiness_qa', 'happiness_qa'
    )


class ClusterRecsReviewQAAdmin(admin.ModelAdmin):
    list_display = ('pk', 'item', 'position', 'usefulness_qa', 'choice_qa')


admin.site.register(HHUser, HHUserAdmin)
admin.site.register(RecsReview, RecsReviewAdmin)
admin.site.register(RecsReviewQA, RecsReviewQAAdmin)
admin.site.register(ClusterRecsReviewQA, ClusterRecsReviewQAAdmin)
