from django.test import TestCase

from payment.models import *

paymethod = Paymethod.objects.first()
user = User.objects.first()
ledger = paymethod.pay(
    amount=1000,
    tax_free=100,
    user=user,
    uid="payid001",
    pay_title="테스트결제001"
)
