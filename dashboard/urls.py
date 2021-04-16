from django.urls import path, include

from dashboard.views import IndexView, SellerLoginView, SellerLogoutView, ProductListView, ProductCreateView, \
    ProductImageView

app_name = 'seller'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('auth/login/', SellerLoginView.as_view(), name='login'),
    path('auth/logout/', SellerLogoutView.as_view(), name='logout'),
    path('product/', ProductListView.as_view(), name='product'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('productimage/', ProductImageView.as_view(), name='productimage'),
]
