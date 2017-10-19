from django.contrib import admin
from main.models import HHUser, ItemClusterReview


class HHUserAdmin(admin.ModelAdmin):
    list_display = ('code', 'cluster_id')


class ItemClusterReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'hh_user', 'item_cluster_id', 'dt')


admin.site.register(HHUser, HHUserAdmin)
admin.site.register(ItemClusterReview, ItemClusterReviewAdmin)
