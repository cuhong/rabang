from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import View

from show.models import Show


class MallIndexView(View):
    def get(self, request):
        show_list = Show.objects.filter(end_at__gte=timezone.now(), is_visible=True)
        return render(request, 'index.html', context={"show_list": show_list})


class ShowView(View):
    def get(self, request, show_id):
        show = get_object_or_404(Show.objects.select_related('product'), id=show_id)
        return render(request, 'product/description.html', {"show": show})


class ShowLiveView(View):
    def get(self, request, show_id):
        show = get_object_or_404(Show.objects.select_related('product'), id=show_id)
        return render(request, 'show/live.html', {"show": show})
