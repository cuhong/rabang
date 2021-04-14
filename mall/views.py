from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from show.models import Show, Chat


class MallIndexView(View):
    def get(self, request):
        show_list = Show.objects.filter(end_at__gte=timezone.now(), is_visible=True)
        return render(request, 'index.html', context={"show_list": show_list})


class ShowView(View):
    def get(self, request, show_id):
        show = get_object_or_404(Show.objects.select_related('product'), id=show_id)
        hide_header = request.GET.get('hideHeader', 'false') == 'true'
        return render(request, 'product/description.html', {"show": show, 'hide_header': hide_header})


class ShowLiveView(View):
    def get(self, request, show_id):
        show = get_object_or_404(Show.objects.select_related('product'), id=show_id)
        return render(request, 'show/live.html', {"show": show})


class ShowChatView(View):
    def get(self, request, show_id):
        last_seen = int(request.GET.get('lastSeen'))
        chat_list = Chat.objects.values('msg', 'id').filter(show_id=show_id, id__gt=last_seen)
        response_data = {"result": True, "chat_list": list(chat_list)}
        return JsonResponse(response_data)

    def post(self, request, show_id):
        show = get_object_or_404(Show.objects.select_related('product'), id=show_id)
        chat = Chat.objects.create(show=show, msg=request.POST.get('msg'))
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
