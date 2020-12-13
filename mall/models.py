from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from sequences import get_next_value

from account.models import UserFkMixin
from broadcast.models import BroadCast
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
        ordering = ('-registered_at',)

    broadcast = models.ForeignKey(BroadCast, null=False, blank=False, verbose_name='방송', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    option = models.ForeignKey(ProductOption, null=False, blank=False, verbose_name='상품옵션', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False, blank=False, verbose_name='수량')

    @classmethod
    def add(cls, user, broadcast, product, quantity, option):
        # 방송중 상품을 카트에 담는 메서드
        if broadcast.broadcastproduct_set.filter(product=product).exists() is False:
            raise MallError('상품과 방송이 매칭되지 않습니다.')
        if broadcast.is_sell_available is False:
            raise MallError('판매중인 상품이 아닙니다.')
        if option not in product.productoption_set.all():
            raise MallError('상품과 옵션이 매칭되지 않습니다.')
        # 중복된 상품 여부를 확인하고 추가한다.
        cart, created = cls.objects.get_or_create(
            user=user, broadcast=broadcast, product=product, option=option, defaults={"quantity": quantity}
        )
        if not created:
            cart.quantity = F('quantity') + quantity
            cart.save()
        return cart

    @transaction.atomic
    def to_order(self, paymethod):
        if self.broadcast.is_sell_available is False:
            raise MallError('판매중인 상품이 아닙니다.')
        if self.user != paymethod.user:
            raise MallError('결제수단 소지자와 주문자가 상이합니다.')
        # 주문서로 넘길땐 중복된 상품을 체크하지 않는다.
        order = Order.objects.create(
            user=self.user,
            broadcast=self.broadcast,
            product=self.product,
            option=self.option,
            paymethod=paymethod,
            quantity=self.quantity,
            serial=get_order_serial(),
            original_price=self.option.original_price * self.quantity,
            sale_price=self.option.sale_price * self.quantity,
            status=0
        )
        order.save()
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
    original_price = models.PositiveIntegerField(null=False, blank=False, verbose_name='정가 계')  # 표시용 정가
    sale_price = models.PositiveIntegerField(null=False, blank=False, verbose_name='기본 판매가 계')  # 판매시 표시금액
    benefit_price = models.PositiveIntegerField(null=True, blank=True, verbose_name='할인 판매가 계')  # 결제시 금액
    paymethod = models.ForeignKey(Paymethod, null=False, blank=False, verbose_name='결제수단', on_delete=models.PROTECT)
    status = models.IntegerField(
        choices=((0, '결제대기'), (1, '결제성공'), (2, '결제실패'), (3, '주문취소')), null=False, blank=False,
        default=0, verbose_name='상태'
    )
    payment_ledger = models.ForeignKey(PayLedger, null=True, blank=True, verbose_name='결제', on_delete=models.PROTECT)

    def calculate_unit_benefit_price(self):
        sale_rate, is_fixed = self.broadcast.get_order_quantity_count
        unit_benefit_price = (self.option.sale_price * (1 - sale_rate / 100))
        return unit_benefit_price, is_fixed

    @transaction.atomic
    def get_order_detail_serial(self):
        with transaction.atomic():
            _sequence = get_next_value(self.serial)
            sequence = f"{self.serial}-{str(_sequence).zfill(3)}"
        return sequence

    def pay(self):
        if self.status != 0:
            raise MallError(f'주문이 {self.get_status_display()} 상태 입니다.')
        try:
            unit_benefit_price, is_fixed = self.calculate_unit_benefit_price()
            total_benefit_price = unit_benefit_price * self.quantity
            ledger = self.paymethod.pay(
                total_benefit_price, 0, self.user, str(self.id), f"{self.product.name} / {self.option.name}"
            )
            self.status = 1
            self.benefit_price = total_benefit_price
            self.payment_ledger = ledger

            for i in range(self.quantity):
                order_detail = OrderDetail.objects.create(
                    serial=self.get_order_detail_serial(),
                    unit_benefit_price=unit_benefit_price,
                    order=self,
                    status=0
                )
        except PaymentError as e:
            self.status = 2
        self.save()


class OrderDetail(SerialMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '주문 상품'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    order = models.ForeignKey(Order, null=True, blank=True, verbose_name='주문서', on_delete=models.PROTECT)
    status = models.IntegerField(
        choices=(
            (0, '주문완료'), (1, '상품준비중'), (2, '출고작업중'), (3, '배송중'), (4, '배송완료'),
            (5, '구매확정'), (6, '취소요청'), (7, '취소'), (8, '반품')
        ), null=False, blank=False, default=0, verbose_name='상태'
    )
    unit_benefit_price = models.PositiveIntegerField(null=True, blank=True, verbose_name='할인 판매가')
    payment_ledger_cancel = models.ForeignKey(
        PayLedgerCancel, null=True, blank=True, verbose_name='결제취소', on_delete=models.PROTECT
    )
