from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone
from sequences import get_next_value

from account.models import UserFkMixin
from broadcast.models import BroadCast
from common.models import DateTimeMixin, UUIDPkMixin, SerialMixin
from product.models import Product, ProductOption

User = get_user_model()


class Cart(UserFkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '카트'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    broadcast = models.ForeignKey(BroadCast, null=False, blank=False, verbose_name='방송', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    option = models.ForeignKey(ProductOption, null=True, blank=True, verbose_name='상품옵션', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False, blank=False, verbose_name='수량')
    is_delete = models.BooleanField(default=False, verbose_name='삭제여부')

    @transaction.atomic
    def to_order(self):
        order = Order.objects.create(
            user=self.user,
            broadcast=self.broadcast,
            product=self.product,
            option=self.option,
            quantity=self.quantity,
            status=0
        )
        self.delete()
        return order


class Order(SerialMixin, UserFkMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    """
    주문취소는 결제 발생 전 취소한 것
    """

    class Meta:
        verbose_name = '주문'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    SERIAL_LENGTH = 10
    broadcast = models.ForeignKey(BroadCast, null=False, blank=False, verbose_name='방송', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    option = models.ForeignKey(ProductOption, null=True, blank=True, verbose_name='상품옵션', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False, blank=False, verbose_name='최초 구매수량')
    status = models.IntegerField(
        choices=((0, '결제대기'), (1, '결제성공'), (2, '결제실패'), (3, '주문취소')), null=False, blank=False,
        default=0, verbose_name='상태'
    )

    @classmethod
    def _get_serial(cls):
        with transaction.atomic():
            now = timezone.now()
            _sequence = get_next_value(f"order_{now.strftime('%Y%m%d')}")
            sequence = f"{now.strftime('%Y%m%d')}-{str(_sequence).zfill(10)}"
        return sequence


class OrderDetail(SerialMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '주문 상품'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    order = models.ForeignKey(Order, null=True, blank=True, verbose_name='주문서', on_delete=models.PROTECT)
    status = models.IntegerField(
        choices=((0, '정상'), (1, '취소/환불')), null=False, blank=False, default=0, verbose_name='상태'
    )

    @transaction.atomic
    def _get_serial(self):
        with transaction.atomic():
            _sequence = get_next_value(self.order.serial)
            sequence = f"{self.order.serial}-{str(_sequence).zfill(3)}"
        return sequence
