from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('mall.urls', namespace='mall')),
    path('admin/', admin.site.urls),
    path('rest-auth/', include('rest_auth.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('api/account/', include('account.api_urls', namespace='account_api')),
    path('payment/', include('payment.urls', namespace='payment')),
    path('api/payment/', include('payment.api_urls', namespace='payment_api')),
    path('api/mall/', include('mall.api_urls', namespace='mall_api')),
    path('api/product/', include('product.api_urls', namespace='product_api')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('pwa.urls'))
]

admin.site.site_header = "라방"
admin.site.site_title = "라방"
admin.site.index_title = "라방"
