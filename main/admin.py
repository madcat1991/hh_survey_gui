from django.contrib import admin
from main.models import HHUser, RecsReview


class HHUserAdmin(admin.ModelAdmin):
    list_display = ('code', 'cluster_id')


class RecsReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'hh_user', 'recs_type', 'dt')


admin.site.register(HHUser, HHUserAdmin)
admin.site.register(RecsReview, RecsReviewAdmin)
