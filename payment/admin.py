from django.contrib import admin
from solo.admin import SingletonModelAdmin

from payment.models import IMPConfig, Paymethod, PayLedger, PayLedgerCancel


@admin.register(IMPConfig)
class IMPConfigAdmin(SingletonModelAdmin):
    pass


@admin.register(Paymethod)
class PaymethodAdmin(admin.ModelAdmin):
    list_display = ['registered_at', 'card_name', 'card_nickname', 'user', 'status']
    list_filter = ['status']


class PayLedgerCancelInline(admin.TabularInline):
    model = PayLedgerCancel
    readonly_fields = [
        'payment', 'amount', 'tax_free', 'uid', 'imp_uid', 'pay_title', 'reason',
        'status', 'error', 'data'
    ]


@admin.register(PayLedger)
class PayLedgerAdmin(admin.ModelAdmin):
    list_display = ['registered_at', 'user', 'paymethod', 'amount', 'tax_free', 'pay_title', 'status']
    list_filter = ['status']
    readonly_fields = [
        "id", "registered_at", "updated_at", "user", "paymethod", "amount", "tax_free", "uid",
        "imp_uid", "pay_title", "status", "data", "error"
    ]
    inlines = [PayLedgerCancelInline]
