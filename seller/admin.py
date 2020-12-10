from django.contrib import admin

from seller.models import Seller, SellerImage


@admin.register(SellerImage)
class SellerImageAdmin(admin.ModelAdmin):
    pass


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'contact', 'email']
    fieldsets = (
        (None, {"fields": ('user', 'name', 'profile', 'contact', 'email')}),
        ("대표자", {"fields": ('rep_name', 'rep_contact', 'rep_email')}),
        ("영업담당자", {"fields": ('sales_name', 'sales_contact', 'sales_email')}),
        ("CS 담당자", {"fields": ('cs_name', 'cs_contact', 'cs_email')}),
        ("배송 담당자", {"fields": ('logistic_name', 'logistic_contact', 'logistic_email')})
    )
