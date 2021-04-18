from django.db import models
from django.db.models import Case, When, F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from show.models import Show, Chat, ShowStatus


class MallIndexView(View):
    def get(self, request):
        show_list = Show.objects.filter(
            end_at__gte=timezone.now(), status__in=[ShowStatus.APPROVED, ShowStatus.ONAIR]
        )
        return render(request, 'index.html', context={"show_list": show_list})


class ShowView(View):
    def get(self, request, show_id):
        show = get_object_or_404(Show.objects.select_related('product'), id=show_id)
        hide_header = request.GET.get('hideHeader', 'false') == 'true'
        return render(request, 'product/description.html', {"show": show, 'hide_header': hide_header})


class ShowLiveView(View):
    def get(self, request, show_id):
        show = get_object_or_404(Show.objects.select_related('product').prefetch_related('chat_set'), id=show_id)
        last_chat_id = show.chat_set.last().id if show.chat_set.last() else 1
        return render(request, 'show/live.html', {"show": show, "last_chat_id": last_chat_id})


class ShowChatView(View):
    def get(self, request, show_id):
        last_seen = int(request.GET.get('lastSeen'))
        chat_list = Chat.objects.values(
            'msg', 'id', 'user__name', 'user__seller__name'
        ).filter(show_id=show_id, id__gt=last_seen).annotate(
            is_mine=Case(
                When(user_id=request.user.id, then=True), default=False, output_field=models.BooleanField()
            ),
            is_seller=Case(
                When(show__product__seller__user_id=F('user_id'), then=True), default=False, output_field=models.BooleanField()
            )
        )
        user_id = request.user.id
        response_data = {"result": True, "chat_list": list(chat_list)}
        return JsonResponse(response_data)

    def post(self, request, show_id):
        user = request.user if request.user.is_authenticated else None
        show = get_object_or_404(Show.objects.select_related('product'), id=show_id)
        chat = Chat.objects.create(show=show, msg=request.POST.get('msg'), user=user)
        response_data = {"result": True}
        return JsonResponse(response_data)

# class Chat(DateTimeMixin, models.Model):
#     class Meta:
#         verbose_name = '채팅'
#         verbose_name_plural = verbose_name
#         ordering = ('registered_at',)
#
#     show = models.ForeignKey(Show, null=False, blank=False, on_delete=models.PROTECT, verbose_name='쇼')
#     msg = models.CharField(max_length=1000, null=False, blank=False, verbose_name='메시지')
#
