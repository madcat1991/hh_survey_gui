from django.contrib import admin
from main.models import HHUser, RecsReview, RecsReviewQA, RecsReviewSelectedItem


class HHUserAdmin(admin.ModelAdmin):
    list_display = ('code', 'cluster_id')


class RecsReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'hh_user', 'recs_type', 'qa', 'dt')


class RecsReviewQAAdmin(admin.ModelAdmin):
    list_display = ('pk', 'quality_qa', 'diversity_qa', 'easiness_qa', 'happiness_qa')


class RecsReviewSelectedItemAdmin(admin.ModelAdmin):
    list_display = ('review', 'item', 'position')


admin.site.register(HHUser, HHUserAdmin)
admin.site.register(RecsReview, RecsReviewAdmin)
admin.site.register(RecsReviewQA, RecsReviewQAAdmin)
admin.site.register(RecsReviewSelectedItem, RecsReviewSelectedItemAdmin)
