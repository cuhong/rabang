from django.urls import path, include

from mall.views import MallIndexView, ShowView, ShowLiveView, ShowChatView

app_name = 'mall'

urlpatterns = [
    path('', MallIndexView.as_view(), name='index'),
    path('product/<uuid:show_id>/', ShowView.as_view(), name='show'),
    path('show/<uuid:show_id>/', ShowLiveView.as_view(), name='show_live'),
    path('show/<uuid:show_id>/chat/', ShowChatView.as_view(), name='show_chat'),
]
