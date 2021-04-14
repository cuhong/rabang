from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from sequences import get_next_value

from account.models import UserFkMixin
from common.models import DateTimeMixin, UUIDPkMixin, SerialMixin
from payment.models import PayLedger, PayLedgerCancel, Paymethod, PaymentError
from product.models import Product, ProductOption


class MallError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


User = get_user_model()


def get_order_serial():
    with transaction.atomic():
        now = timezone.now()
        _sequence = get_next_value(f"order_{now.strftime('%Y%m%d')}")
        sequence = f"{now.strftime('%Y%m%d')}-{str(_sequence).zfill(10)}"
    return sequence


class Cart(UserFkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '카트'
        verbose_name_plural = verbose_name
        ordering = ('product', 'option', '-registered_at',)

    # 나중에 방송과 독립된 판매가 도입될 경우 broadcast 가 null인 케이스가 나온다. 지금은 반영 안함
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    option = models.ForeignKey(ProductOption, null=False, blank=False, verbose_name='상품옵션', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False, blank=False, verbose_name='수량')

    @classmethod
    def add(cls, user, product, quantity, option):
        # 방송중 상품을 카트에 담는 메서드
        if option not in product.productoption_set.all():
            raise MallError('상품과 옵션이 매칭되지 않습니다.')
        # 다른 방송 상품을 담은게 있는지 확인하고
        # 수량이 추가된다.
        try:
            cart = cls.objects.get(user=user, product=product, option=option)
        except cls.DoesNotExist:
            cart = cls.objects.create(user=user, product=product, option=option, quantity=quantity)
        else:
            cart.quantity = cart.quantity + quantity
            cart.save()
        return cart


class OrderSheet(SerialMixin, UserFkMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    """
    주문취소는 결제 발생 전 취소한 것
    """
    class Meta:
        verbose_name = '주문'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    SERIAL_LENGTH = 10
    status = models.IntegerField(
        choices=((0, '결제대기'), (1, '결제성공'), (2, '결제실패'), (3, '주문취소')), null=False, blank=False,
        default=0, verbose_name='상태'
    )
    payment_ledger = models.ForeignKey(PayLedger, null=True, blank=True, verbose_name='결제', on_delete=models.PROTECT)


class OrderSheetItem(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '주문 아이템'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    ordersheet = models.ForeignKey(OrderSheet, null=False, blank=False, verbose_name='주문서', on_delete=models.PROTECT)
    cart = models.ForeignKey(Cart, null=False, blank=False, verbose_name='카트', on_delete=models.PROTECT)
    delivery_fee = models.IntegerField(default=0, null=False, blank=False, verbose_name='배송비')
    amount_fee = models.IntegerField(default=0, null=False, blank=False, verbose_name='상품가')
    grand_total = models.IntegerField(default=0, null=False, blank=False, verbose_name='총계')