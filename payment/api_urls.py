app_name = 'payment_api'

from django.urls import path
from payment import api_views as views

urlpatterns = [
    path('', views.PaymethodView.as_view(), name='paymethod'),
]
