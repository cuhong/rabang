app_name = 'broadcast'

from django.urls import path
from broadcast import views

urlpatterns = [
    path('caster/<uuid:broadcast_id>/', views.CasterView.as_view(), name='caster'),
    path('admin/<uuid:broadcast_id>/', views.BroadCastAdminView.as_view(), name='admin'),
    path('show/<uuid:broadcast_id>/', views.BoradCastView.as_view(), name='show'),
]
