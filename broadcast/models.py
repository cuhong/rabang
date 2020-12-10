import uuid

from django.db import models
from django.utils import timezone
from solo.models import SingletonModel

from common.models import UUIDPkMixin, DateTimeMixin, PublicImageMixin
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


class BroadCast(SellerFkMixin, UUIDPkMixin, DateTimeMixin, PublicImageMixin, models.Model):
    class Meta:
        verbose_name = '방송'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    thumbnail = models.ImageField(
        null=False, blank=False,
        upload_to=broadcast_thumbnail_upload_to,
        storage=PublicFileStorage()
    )
    start_at = models.DateTimeField(null=False, blank=False, verbose_name='시작일시')
    end_at = models.DateTimeField(null=False, blank=False, verbose_name='종료일시')
    title = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목')
    notice = models.TextField(null=True, blank=True, verbose_name='공지사항')
    channel = models.OneToOneField(
        Channel, null=False, blank=False, verbose_name='채널', on_delete=models.PROTECT, default=create_channel
    )
