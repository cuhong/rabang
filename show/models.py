import os

from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from common.models import SerialMixin, DateTimeMixin, UUIDPkMixin
from product.models import Product
from rabang.storages import PublicFileStorage

User = get_user_model()


def poster_upload_to(instance, filename):
    return os.path.join('show', 'poster', 'image', timezone.localdate().strftime("%Y/%m/%d"), filename)


def poster_video_upload_to(instance, filename):
    return os.path.join('show', 'poster', 'video', timezone.localdate().strftime("%Y/%m/%d"), filename)


class Show(SerialMixin, DateTimeMixin, UUIDPkMixin, models.Model):
    class Meta:
        verbose_name = '쇼'
        verbose_name_plural = verbose_name
        ordering = ('start_at',)

    SERIAL_PREFIX = "SHOW"
    SERIAL_LENGTH = "3"

    title = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목(내부용)')
    title_display = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목(표시용)')
    description = RichTextField(null=False, blank=False, verbose_name='쇼 소개')
    poster = models.ImageField(null=False, blank=False, upload_to=poster_upload_to, storage=PublicFileStorage())
    poster_video = models.FileField(
        null=True, blank=True, upload_to=poster_video_upload_to, storage=PublicFileStorage()
    )
    start_at = models.DateTimeField(null=False, blank=False, verbose_name='시작시간')
    end_at = models.DateTimeField(null=False, blank=False, verbose_name='종료시간')
    product = models.ForeignKey(Product, null=True, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    is_visible = models.BooleanField(default=True, null=False, blank=False, verbose_name='노출')
    notification_group = models.ManyToManyField(User, blank=True, verbose_name='알림 그룹')
    hls_path = models.TextField(null=True, blank=True, verbose_name='HLS 경로')

    @property
    def is_live(self):
        if self.is_visible is False:
            return False
        now = timezone.now()
        return all([self.start_at <= now, self.end_at >= now])
