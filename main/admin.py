from django.contrib import admin
from main.models import HHUser, RecsClusterReview, HHUserRecsReview


class HHUserAdmin(admin.ModelAdmin):
    list_display = ('code', 'cluster_id')


class RecsClusterReviewAdmin(admin.ModelAdmin):
    list_display = ('cluster_id', 'cluster_pos', 'item', 'item_pos', 'answer', 'dt', 'review')


class HHUserRecsReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'hh_user', 'answer', 'recs_type', 'dt')


admin.site.register(HHUser, HHUserAdmin)
admin.site.register(RecsClusterReview, RecsClusterReviewAdmin)
admin.site.register(HHUserRecsReview, HHUserRecsReviewAdmin)
