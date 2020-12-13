from rest_framework import serializers

from broadcast.models import BroadCast
from mall.models import Cart

"""


    broadcast = models.ForeignKey(BroadCast, null=False, blank=False, verbose_name='방송', on_delete=models.PROTECT)
    product = models.ForeignKey(Product, null=False, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    option = models.ForeignKey(ProductOption, null=False, blank=False, verbose_name='상품옵션', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(null=False, blank=False, verbose_name='수량')
"""

"""
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
"""


class BroadCastSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadCast
        fields = [
            'id', 'thumbnail', 'title', 'notice'
        ]


class BroadCastSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadCast
        fields = [
            'id', 'thumbnail', 'start_at', 'end_at', 'sell_end_at', 'title', 'notice', 'channel',
            'sale_threshold_1', 'sale_threshold_2', 'sale_threshold_3', 'sale_rate_1', 'sale_rate_2', 'sale_rate_3'
        ]
