app_name = 'broadcast_api'

from django.urls import path
from broadcast import api_views as views

urlpatterns = [
    path('live/', views.LiveBroadCastView.as_view(), name='live'),
    path('remon/', views.GetRemonConfigView.as_view(), name='remon')
]
