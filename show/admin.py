from django.contrib import admin, messages
from inline_actions.admin import InlineActionsModelAdminMixin

from show.models import Show, ShowStatus, ShowError


@admin.register(Show)
class ShowAdmin(InlineActionsModelAdminMixin, admin.ModelAdmin):
    list_display = ['serial', 'title', 'start_at', 'end_at', 'product', 'status']
    list_filter = ['status']
    search_fields = ['title__icontains', 'title_display__icontains', 'product__name__icontains']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_inline_actions(self, request, obj=None):
        actions = super(ShowAdmin, self).get_inline_actions(request, obj)
        if obj:
            if obj.status == ShowStatus.ONAIR:
                actions.append('off_air')
            if obj.status == ShowStatus.PENDING:
                actions.append('approve_show')
            elif obj.status == ShowStatus.APPROVED:
                actions.append('unapprove_show')
                actions.append('on_air')
            if obj.status == ShowStatus.PENDING:
                actions.append('deny_show')
            elif obj.status == ShowStatus.DENY:
                actions.append('undeny_show')
            if obj.status in [ShowStatus.PENDING, ShowStatus.DENY]:
                actions.append('delete_show')
        return actions

    def delete_show(self, request, obj, parent_obj=None):
        title = obj.title
        try:
            obj.delete_show(user=request.user)
        except ShowError as e:
            messages.error(request, e.msg)
        else:
            messages.success(request, f"{title}이 삭제되었습니다.")

    delete_show.short_description = '삭제'

    def approve_show(self, request, obj, parent_obj=None):
        title = obj.title
        try:
            obj.approve(user=request.user)
        except ShowError as e:
            messages.error(request, e.msg)
        else:
            messages.success(request, f"{title}이 승인되었습니다..")

    approve_show.short_description = '승인'

    def unapprove_show(self, request, obj, parent_obj=None):
        title = obj.title
        try:
            obj.unapprove(user=request.user)
        except ShowError as e:
            messages.error(request, e.msg)
        else:
            messages.success(request, f"{title}이 승인 취소되었습니다..")

    unapprove_show.short_description = '승인취소'

    def deny_show(self, request, obj, parent_obj=None):
        title = obj.title
        try:
            obj.deny(user=request.user)
        except ShowError as e:
            messages.error(request, e.msg)
        else:
            messages.success(request, f"{title}이 반려되었습니다..")

    deny_show.short_description = '반려'

    def undeny_show(self, request, obj, parent_obj=None):
        title = obj.title
        try:
            obj.undeny(user=request.user)
        except ShowError as e:
            messages.error(request, e.msg)
        else:
            messages.success(request, f"{title}이 반려 취소되었습니다.")

    undeny_show.short_description = '반려 취소'

    def on_air(self, request, obj, parent_obj=None):
        title = obj.title
        try:
            obj.on_air(user=request.user)
        except ShowError as e:
            messages.error(request, e.msg)
        else:
            messages.success(request, f"{title}의 방송이 시작됩니다.")

    on_air.short_description = 'OnAir'

    def off_air(self, request, obj, parent_obj=None):
        title = obj.title
        try:
            obj.off_air(user=request.user)
        except ShowError as e:
            messages.error(request, e.msg)
        else:
            messages.success(request, f"{title}의 방송이 종료되었습니다.")

    off_air.short_description = 'OffAir'
