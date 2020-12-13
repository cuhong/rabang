app_name = 'product_api'

from django.urls import path
from product import api_views as views

urlpatterns = [
    path('<uuid:product_id>/', views.ProductDetailView.as_view(), name='product'),
]
