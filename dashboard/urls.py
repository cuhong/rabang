from django.urls import path, include

from dashboard.views import IndexView, SellerLoginView, SellerLogoutView, ProductListView, ProductCreateView, \
    ProductImageView, ProductUpdateView, ProductAjaxView, ShowListView, ShowCreateView, ShowUpdateView, ShowDeleteView, \
    ShowView

app_name = 'seller'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('auth/login/', SellerLoginView.as_view(), name='login'),
    path('auth/logout/', SellerLogoutView.as_view(), name='logout'),
    path('product/', ProductListView.as_view(), name='product'),
    path('product/ajax/', ProductAjaxView.as_view(), name='product_ajax'),
    path('product/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<uuid:product_id>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('productimage/', ProductImageView.as_view(), name='productimage'),
    path('show/', ShowListView.as_view(), name='show'),
    path('show/create/', ShowCreateView.as_view(), name='show_create'),
    path('show/<uuid:show_id>/', ShowView.as_view(), name='lets_show'),
    path('show/<uuid:show_id>/update/', ShowUpdateView.as_view(), name='show_update'),
    path('show/<uuid:show_id>/delete/', ShowDeleteView.as_view(), name='show_delete'),
]
