app_name = 'broadcast'

from django.urls import path
from broadcast import views

urlpatterns = [
    path('caster/<uuid:broadcast_id>/', views.CasterView.as_view(), name='caster'),
]
