from django.db import models, transaction
from django.utils import timezone
from ordered_model.models import OrderedModel

from common.models import SerialMixin, UUIDPkMixin, DateTimeMixin, PublicImageMixin
from seller.models import SellerFkMixin


class ProductError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class ProductImage(SellerFkMixin, UUIDPkMixin, DateTimeMixin, PublicImageMixin, models.Model):
    class Meta:
        verbose_name = '상품이미지'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    UPLOAD_TO_FUNCTION = lambda instance, filename: "/".join(['product', timezone.now().strftime("%Y/%m/%d")])


class ProductOption(SerialMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '상품옵션'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    SERIAL_PREFIX = "SO"
    name = models.CharField(max_length=300, null=False, blank=False, unique=True, verbose_name='옵션명')
    thumbnail = models.ForeignKey(ProductImage, null=False, blank=False, verbose_name='썸네일', on_delete=models.PROTECT)
    original_price = models.IntegerField(null=True, blank=True, verbose_name='정가')
    sale_price = models.IntegerField(null=False, blank=False, verbose_name='기본 판매가')
    is_default = models.BooleanField(default=False, verbose_name='기본상품')
    stock = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='재고', help_text='입력하지 않을 경우 재고 무한'
    )
    sold_count = models.IntegerField(default=0, null=False, blank=False, verbose_name='누적 판매수량')

    def __str__(self):
        return self.name

    @transaction.atomic
    def is_orderable(self, broadcast):
        return self.sold_count + broadcast <= self.stock


class Product(SellerFkMixin, SerialMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '상품'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    SERIAL_PREFIX = "PRD"
    name = models.CharField(max_length=300, null=False, blank=False, unique=True, verbose_name='상품명')
    thumbnail = models.ForeignKey(ProductImage, null=False, blank=False, verbose_name='썸네일', on_delete=models.PROTECT)
    simple_description = models.CharField(max_length=2000, null=False, blank=False, verbose_name='간단설명')
    description = models.TextField(null=False, blank=False, verbose_name='상세설명')
    options = models.ManyToManyField(ProductOption, blank=False, verbose_name='옵션')

    def __str__(self):
        return self.name


class ProductDetail(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name = '상품고시'
        verbose_name_plural = verbose_name

    order_with_respect_to = 'product'
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    key = models.CharField(max_length=200, null=False, blank=False, verbose_name='키')
    value = models.TextField(null=False, blank=False, verbose_name='값')
