import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from solo.models import SingletonModel

from common.models import UUIDPkMixin, DateTimeMixin, PublicImageMixin
from product.models import Product
from rabang.storages import PublicFileStorage
from seller.models import SellerFkMixin

User = get_user_model()


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
    u = uuid.uuid4()
    return "/".join(['broadcast', timezone.now().strftime("%Y/%m/%d"), str(u), filename])


class BroadCast(SellerFkMixin, UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '방송'
        verbose_name_plural = verbose_name
        ordering = ('start_at',)

    thumbnail = models.ImageField(
        null=False, blank=False,
        upload_to=broadcast_thumbnail_upload_to,
        storage=PublicFileStorage(),
        verbose_name='썸네일',
        help_text='방송 리스트에 보일 4:3 비율의 이미지'
    )
    poster = models.ImageField(
        null=False, blank=False,
        upload_to=broadcast_thumbnail_upload_to,
        storage=PublicFileStorage(),
        verbose_name='포스터',
        help_text='영상재생 대기중 보여질 1:1.7 비율의 이미지'
    )
    start_at = models.DateTimeField(null=False, blank=False, verbose_name='시작일시')
    end_at = models.DateTimeField(null=False, blank=False, verbose_name='종료일시')
    sell_end_at = models.DateTimeField(null=False, blank=False, verbose_name='판매 종료일시')
    payment_end_at = models.DateTimeField(null=False, blank=False, verbose_name='결제 종료일시')
    title = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목')
    notice = models.TextField(null=True, blank=True, verbose_name='공지사항')
    channel = models.IntegerField(null=True, blank=True, verbose_name='채널')
    channel_1 = models.OneToOneField(
        Channel, null=False, blank=False, verbose_name='채널 1', on_delete=models.PROTECT, default=create_channel,
        related_name='br_1'
    )
    channel_2 = models.OneToOneField(
        Channel, null=False, blank=False, verbose_name='채널 2', on_delete=models.PROTECT, default=create_channel,
        related_name='br_2'
    )
    channel_3 = models.OneToOneField(
        Channel, null=False, blank=False, verbose_name='채널 3', on_delete=models.PROTECT, default=create_channel,
        related_name='br_3'
    )
    target_sell_count = models.IntegerField(
        null=True, blank=True, verbose_name='판매수량 목표', help_text='0으로 설정시 무조건 할인 미설정시 판매수량 비례 할인 없음'
    )
    max_discount_rate = models.IntegerField(default=0, null=True, blank=True, verbose_name='최대 할인율(%)')
    fixed_quantity_count = models.IntegerField(null=True, blank=True, verbose_name='방송종료시 구매수량')
    products = models.ManyToManyField(Product, blank=False, verbose_name='상품')

    @property
    def is_sell_available(self):
        # 방송 종결처리 기준
        if self.fixed_quantity_count is not None:
            return False
        # 판매 종료일시 기준
        if timezone.now() > self.sell_end_at:
            return False
        return True

    def get_order_quantity_count(self):
        # 해당 방송에 대한 총 주문 수량을 계산한다.
        # from mall.models import Order
        # quantity_count = Order.objects.filter(
        #     broadcast=self,
        #     status=0
        # ).aggregate(quantity_count=Coalesce(Sum('quantity'), Value(0)))['quantity_count']
        # return quantity_count
        pass

    @property
    def is_quantity_fixed(self):
        # 방송 종료 후 판매확정 수량으로 판단
        return False if self.fixed_quantity_count is None else True

    @property
    def calculate_sale_rate(self):
        # 백분률로 표시된 할인률(% 단위)을 반환한다.
        # 방송 중엔 방송 판매 수량으로 계산하고 방송 종료시엔 방송종료시 구매수량 기준으로 할인율을 계산한다.
        # 선형보간
        if self.target_sell_count == 0:
            return self.max_discount_rate
        if self.target_sell_count is None:
            return 0
        order_quantity_count = self.fixed_quantity_count if self.is_quantity_fixed else self.get_order_quantity_count()
        return int(order_quantity_count * self.target_sell_count / self.max_discount_rate)

    def finish_broadcast(self):
        # 방송 종료 후 후처리 및 결제 처리
        # 카트 삭제도 해야함
        # TODO 방송 끝나기 n분전 카트에 있는거 알림 나가야함
        self.fixed_quantity_count = self.get_order_quantity_count()
        self.save()

    def set_wait(self, user):
        # 알림 설정
        wait, created = BroadCastWait.objects.get_or_create(broadcast=self, user=user)
        return created

    def unset_wait(self, user):
        # 알림 설정 해제
        try:
            wait = BroadCastWait.objects.get(broadcast=self, user=user)
        except BroadCastWait.DoesNotExist:
            return False
        else:
            wait.delete()
            return True

    def viewer_enter(self, user):
        viewer = BroadCastViewer.objects.create(broadcast=self, user=user, action=BroadCastViewer.ENTER)

    def viewer_leave(self, user):
        viewer = BroadCastViewer.objects.create(broadcast=self, user=user, action=BroadCastViewer.LEAVE)


class BroadCastWait(DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '방송 알림'
        verbose_name_plural = verbose_name
        unique_together = ('broadcast', 'user')

    broadcast = models.ForeignKey(BroadCast, null=False, blank=False, verbose_name='방송', on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT)


class BroadCastViewer(DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '방송 시청자'
        verbose_name_plural = verbose_name

    ENTER = 1
    LEAVE = -1
    ACTION_CHOICES = (
        (ENTER, '입장'),
        (LEAVE, '퇴장')
    )
    broadcast = models.ForeignKey(BroadCast, null=False, blank=False, verbose_name='방송', on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT)
    action = models.IntegerField(choices=ACTION_CHOICES, null=False, blank=False, verbose_name='행동')
