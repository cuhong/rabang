from django.utils import timezone
from rest_framework import serializers

from broadcast.models import BroadCast, Remonconfig
from mall.models import Cart
from seller.serializers import SellerSimpleSerializer

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


class RemonCredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remonconfig
        fields = [
            'service_id', 'key'
        ]


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
            'id', 'seller', 'thumbnail', 'poster', 'start_at', 'end_at', 'sell_end_at', 'title', 'notice', 'channel',
            'channel_1', 'channel_2', 'channel_3',
            'target_sell_count', 'max_discount_rate', 'wait_count', 'viewer_count', 'im_wait', 'is_on'
        ]

    seller = SellerSimpleSerializer(read_only=True, required=False)
    wait_count = serializers.SerializerMethodField(read_only=True, required=False)
    viewer_count = serializers.SerializerMethodField(read_only=True, required=False)
    im_wait = serializers.SerializerMethodField(read_only=True, required=False)
    is_on = serializers.SerializerMethodField(read_only=True, required=False)

    def get_viewer_count(self, obj):
        return obj.viewer_count

    def get_wait_count(self, obj):
        return obj.broadcastwait_set.count()

    def get_im_wait(self, obj):
        return obj.im_wait > 0

    def get_is_on(self, obj):
        return obj.is_on
        # now = timezone.now()
        # return all([now >= obj.start_at, now <= obj.end_at])
