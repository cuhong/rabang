import uuid

from django.db import models
from django.db.models import Sum
from django.utils import timezone
from solo.models import SingletonModel

from common.models import UUIDPkMixin, DateTimeMixin, PublicImageMixin
from product.models import Product
from rabang.storages import PublicFileStorage
from seller.models import SellerFkMixin


class Remonconfig(SingletonModel):
    service_id = models.CharField(max_length=300, null=True, blank=True, verbose_name='아이디')
    key = models.CharField(max_length=300, null=True, blank=True, verbose_name='키')

    @classmethod
    def get_credential(cls):
        config = cls.get_solo()
        if any([config.service_id is None, config.key is None]):
            raise Exception('리모트몬스터 계정이 설정되지 않았습니다.')
        credential = {
            "serviceId": config.service_id,
            "key": config.key
        }
        return credential


class Channel(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '라이브캐스트'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)


def create_channel():
    return Channel.objects.create()


def broadcast_thumbnail_upload_to(instance, filename):
    return "/".join(['broadcast', timezone.now().strftime("%Y/%m/%d")])


class BroadCast(SellerFkMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '방송'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    thumbnail = models.ImageField(
        null=False, blank=False,
        upload_to=broadcast_thumbnail_upload_to,
        storage=PublicFileStorage(),
        verbose_name='썸네일'
    )
    start_at = models.DateTimeField(null=False, blank=False, verbose_name='시작일시')
    end_at = models.DateTimeField(null=False, blank=False, verbose_name='종료일시')
    sell_end_at = models.DateTimeField(null=False, blank=False, verbose_name='판매 종료일시')
    payment_end_at = models.DateTimeField(null=False, blank=False, verbose_name='결제 종료일시')
    title = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목')
    notice = models.TextField(null=True, blank=True, verbose_name='공지사항')
    channel = models.OneToOneField(
        Channel, null=False, blank=False, verbose_name='채널', on_delete=models.PROTECT, default=create_channel
    )
    sale_threshold_1 = models.IntegerField(null=True, blank=True, verbose_name='할인구간 1')
    sale_threshold_2 = models.IntegerField(null=True, blank=True, verbose_name='할인구간 2')
    sale_threshold_3 = models.IntegerField(null=True, blank=True, verbose_name='할인구간 3')
    sale_rate_1 = models.IntegerField(null=True, blank=True, verbose_name='할인율(%) 1')
    sale_rate_2 = models.IntegerField(null=True, blank=True, verbose_name='할인율(%) 2')
    sale_rate_3 = models.IntegerField(null=True, blank=True, verbose_name='할인율(%) 3')
    fixed_quantity_count = models.IntegerField(null=True, blank=True, verbose_name='총 주문 수량')

    @property
    def is_sell_available(self):
        # 판매 종료일시 기준
        if self.sell_end_at:
            return timezone.now() <= self.sell_end_at
        else:
            return True

    @property
    def get_order_quantity_count(self):
        # 해당 방송에 대한 총 주문 수량을 계산한다.
        from mall.models import Order
        quantity_count = Order.objects.filter(
            broadcast=self,
            status=0
        ).aggregate(quantity_count=Sum('quantity'))['quantity_count'] or 0
        return quantity_count

    @property
    def calculate_sale_rate(self):
        # 백분률로 표시된 할인률을 반환한다.
        is_fixed = False if self.fixed_quantity_count is None else True
        order_quantity_count = self.fixed_quantity_count if is_fixed is True else self.get_order_quantity_count
        if order_quantity_count >= self.sale_threshold_3:
            return self.sale_rate_3, is_fixed
        elif order_quantity_count >= self.sale_threshold_2:
            return self.sale_rate_2, is_fixed
        elif order_quantity_count >= self.sale_threshold_1:
            return self.sale_rate_1, is_fixed
        else:
            return 0, is_fixed

    def finish_broadcast(self):
        # 방송 종료 후 후처리 및 결제 처리
        self.fixed_quantity_count = self.get_order_quantity_count
        self.save()


class BroadcastProduct(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '방송상품'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    broadcast = models.ForeignKey(BroadCast, null=False, blank=False, verbose_name='방송', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
