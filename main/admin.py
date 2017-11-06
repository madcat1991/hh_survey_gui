from django.contrib import admin
from main.models import HHUser


class HHUserAdmin(admin.ModelAdmin):
    list_display = ('code', 'cluster_id')


admin.site.register(HHUser, HHUserAdmin)
