from django.contrib import admin

from product.models import Product, ProductOption, ProductImage


# class ProductOptionInline(admin.TabularInline):
#     model = ProductOption

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['registered_at', 'serial', 'name', 'original_price', 'sale_price']
    # inlines = [ProductOptionInline]


@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_diff', 'is_default', 'stock', 'sold_count']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    pass
