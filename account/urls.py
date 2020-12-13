app_name = 'account'

from django.urls import path
from account import views as views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
]
