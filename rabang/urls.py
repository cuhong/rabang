from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('api/account/', include('account.api_urls', namespace='account_api')),
    path('api/broadcast/', include('broadcast.api_urls', namespace='broadcast_api')),
    path('broadcast/', include('broadcast.urls', namespace='broadcast')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('api/payment/', include('payment.api_urls', namespace='payment_api')),
    path('api/mall/', include('mall.api_urls', namespace='mall_api')),
    path('api/product/', include('product.api_urls', namespace='product_api')),
]
