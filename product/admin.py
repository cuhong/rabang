from django.contrib import admin

from product.models import Product, ProductOption, ProductOptionDetail


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['registered_at', 'serial', 'name']


@admin.register(ProductOption)
class ProductOptionDetailAdmin(admin.ModelAdmin):
    list_display = ['product', 'original_price', 'sale_price']


@admin.register(ProductOptionDetail)
class ProductOptionDetailAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
