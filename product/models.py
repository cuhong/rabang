from django.db import models
from django.utils import timezone
from ordered_model.models import OrderedModel

from common.models import SerialMixin, UUIDPkMixin, DateTimeMixin, PublicImageMixin
from seller.models import SellerFkMixin


class ProductImage(SellerFkMixin, UUIDPkMixin, DateTimeMixin, PublicImageMixin, models.Model):
    class Meta:
        verbose_name = '상품이미지'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    UPLOAD_TO_FUNCTION = lambda instance, filename: "/".join(['product', timezone.now().strftime("%Y/%m/%d")])


class Product(SellerFkMixin, SerialMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '상품'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    SERIAL_PREFIX = "PRD"
    name = models.CharField(max_length=300, null=False, blank=False, unique=True, verbose_name='상품명')
    thumbnail = models.ForeignKey(ProductImage, null=False, blank=False, verbose_name='썸네일', on_delete=models.PROTECT)
    description = models.TextField(null=False, blank=False, verbose_name='상세설명')

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


class ProductOption(SerialMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '상품옵션'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    SERIAL_PREFIX = "SO"
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    original_price = models.IntegerField(null=True, blank=True, verbose_name='정가')
    sale_price = models.IntegerField(null=False, blank=False, verbose_name='기본 판매가')
    is_default = models.BooleanField(default=False, verbose_name='기본상품')

    def __str__(self):
        option_dict = ProductOptionDetail.objects.values('name', 'value').filter(product_option=self)
        return "/".join([f"{k}: {v}" for k, v in option_dict.items()])


class ProductOptionDetail(models.Model):
    class Meta:
        verbose_name = '상품옵션상세'
        verbose_name_plural = verbose_name
        ordering = ('name', 'value')

    product_option = models.ForeignKey(ProductOption, null=False, blank=False, verbose_name='상품옵션',
                                       on_delete=models.PROTECT)
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name='이름')
    value = models.CharField(max_length=100, null=False, blank=False, verbose_name='값')

    def __str__(self):
        return f"{self.name}: {self.value}"
