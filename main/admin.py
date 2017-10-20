from django.contrib import admin
from main.models import HHUser, ItemClusterReview, UserReviewedHHUser


class HHUserAdmin(admin.ModelAdmin):
    list_display = ('code', 'cluster_id')


class ItemClusterReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'hh_user', 'item_cluster_id', 'dt')


class UserReviewedHHUserAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'hh_user', 'dt')


admin.site.register(HHUser, HHUserAdmin)
admin.site.register(ItemClusterReview, ItemClusterReviewAdmin)
admin.site.register(UserReviewedHHUser, UserReviewedHHUserAdmin)
