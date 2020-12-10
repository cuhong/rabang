from django.contrib import admin
from solo.admin import SingletonModelAdmin

from broadcast.models import BroadCast, Remonconfig


@admin.register(Remonconfig)
class RemonconfigAdmin(SingletonModelAdmin):
    pass


@admin.register(BroadCast)
class BroadCastAdmin(admin.ModelAdmin):
    list_display = ['seller', 'start_at', 'end_at', 'title']
