app_name = 'account_api'

from django.urls import path
from account import api_views as views

urlpatterns = [
    path('login/', views.LoginApiView.as_view(), name='login'),
    path('check/', views.IsAuthenticated.as_view(), name='check'),
]
