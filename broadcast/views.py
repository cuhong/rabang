import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from broadcast.models import BroadCast, Remonconfig


class CasterView(View):
    def get(self, request, broadcast_id):
        broadcast = BroadCast.objects.select_related('channel', 'seller__user', 'seller').get(id=broadcast_id)
        if broadcast.end_at < timezone.now():
            return HttpResponse('<span>종료된 방송입니다</span>', content_type='text/html')
        if broadcast.seller.user != request.user:
            return HttpResponse('<span>권한이 없습니다.</span>', content_type='text/html')
        remon_credential = Remonconfig.get_credential()
        context = {"broadcast": broadcast, "remon_credential": remon_credential}
        return render(request, 'broadcast/caster.html', context=context)


class BroadCastAdminView(View):
    def get(self, request, broadcast_id):
        broadcast = BroadCast.objects.select_related('channel', 'seller__user', 'seller').get(id=broadcast_id)
        if broadcast.end_at < timezone.now():
            return HttpResponse('<span>종료된 방송입니다</span>', content_type='text/html')
        if broadcast.seller.user != request.user:
            return HttpResponse('<span>권한이 없습니다.</span>', content_type='text/html')
        remon_credential = Remonconfig.get_credential()
        context = {"broadcast": broadcast, "remon_credential": remon_credential}
        return render(request, 'broadcast/broadcast_admin.html', context=context)
