app_name = 'mall_api'

from django.urls import path
from mall import api_views as views

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/<int:cart_id>/', views.CartDetailView.as_view(), name='cart_detail'),
]
