from django.contrib import admin
from solo.admin import SingletonModelAdmin

from broadcast.models import BroadCast, Remonconfig, BroadcastProduct


@admin.register(Remonconfig)
class RemonconfigAdmin(SingletonModelAdmin):
    pass


class BroadcastProductInline(admin.TabularInline):
    model = BroadcastProduct

@admin.register(BroadCast)
class BroadCastAdmin(admin.ModelAdmin):
    list_display = ['seller', 'start_at', 'end_at', 'title']
    inlines = [BroadcastProductInline]
