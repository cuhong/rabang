app_name = 'payment'

from django.urls import path
from payment import views

urlpatterns = [
    path('register/', views.PaymethodRegisterView.as_view(), name='register'),
]
