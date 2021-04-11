from django.contrib import admin

from show.models import Show


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ['serial', 'title', 'start_at', 'end_at', 'product', 'is_visible']
    list_filter = ['is_visible']