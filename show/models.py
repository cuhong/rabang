import os

from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from common.models import SerialMixin, DateTimeMixin, UUIDPkMixin
from product.models import Product
from rabang.storages import PublicFileStorage

User = get_user_model()


def poster_upload_to(instance, filename):
    return os.path.join('show', 'poster', 'image', timezone.localdate().strftime("%Y/%m/%d"), filename)


def poster_video_upload_to(instance, filename):
    return os.path.join('show', 'poster', 'video', timezone.localdate().strftime("%Y/%m/%d"), filename)


class ShowError(Exception):
    CODE_DICT = {
        401: "HLS 경로가 설정되지 않았습니다.",
        402: "방송 종료 시간 경과",
        403: "쇼 상태가 승인 대기중이 아닙니다.",
        404: "쇼 상태가 승인 상태가 아닙니다.",
        405: "쇼 상태가 송출중 상태가 아닙니다.",
        406: "쇼가 삭제 불가능한 상태 입니다.",
        407: "쇼 상태가 승인 거절 상태가 아닙니다.",
    }

    def __init__(self, code):
        self.code = code
        self.msg = self.CODE_DICT.get(code, "기타 에러")


class ShowStatus(models.TextChoices):
    PENDING = 'pending', '승인 대기중'
    APPROVED = 'approved', '승인'
    DENY = 'deny', '승인 거절'
    ONAIR = 'onair', '송출중'
    OFFAIR = 'offair', '송출 종료'
    DELETE = 'delte', '삭제'


class Show(SerialMixin, DateTimeMixin, UUIDPkMixin, models.Model):
    class Meta:
        verbose_name = '쇼'
        verbose_name_plural = verbose_name
        ordering = ('start_at',)

    SERIAL_PREFIX = "SHOW"
    SERIAL_LENGTH = "3"

    title = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목(내부용)')
    title_display = models.CharField(max_length=300, null=False, blank=False, verbose_name='제목(표시용)')
    description = models.TextField(null=False, blank=False, verbose_name='쇼 소개')
    poster = models.ImageField(null=False, blank=False, upload_to=poster_upload_to, storage=PublicFileStorage())
    poster_video = models.FileField(
        null=True, blank=True, upload_to=poster_video_upload_to, storage=PublicFileStorage()
    )
    start_at = models.DateTimeField(null=False, blank=False, verbose_name='시작시간')
    end_at = models.DateTimeField(null=False, blank=False, verbose_name='종료시간')
    product = models.ForeignKey(Product, null=True, blank=False, verbose_name='상품', on_delete=models.PROTECT)
    status = models.CharField(
        max_length=20,
        choices=ShowStatus.choices, default=ShowStatus.PENDING, null=False, blank=False, verbose_name='상태'
    )
    notification_group = models.ManyToManyField(User, blank=True, verbose_name='알림 그룹')
    hls_path = models.TextField(null=True, blank=True, verbose_name='HLS 경로')
    history = HistoricalRecords()

    def delete_show(self, user):
        if self.status not in [ShowStatus.PENDING, ShowStatus.DENY]:
            raise ShowError(406)
        self.status = ShowStatus.DELETE
        self._history_user = user
        self.save()

    @property
    def is_live(self):
        now = timezone.now()
        return all([
            self.start_at <= now,
            self.end_at >= now,
            self.status == ShowStatus.ONAIR
        ])

    def deny(self, user):
        if self.end_at < timezone.now():
            raise ShowError(402)
        if self.status != ShowStatus.PENDING:
            raise ShowError(403)
        self.status = ShowStatus.DENY
        self._history_user = user
        self.save()

    def undeny(self, user):
        if self.status != ShowStatus.DENY:
            raise ShowError(407)
        self.status = ShowStatus.PENDING
        self._history_user = user
        self.save()

    def approve(self, user):
        if self.hls_path is None:
            raise ShowError(401)
        if self.end_at < timezone.now():
            raise ShowError(402)
        if self.status != ShowStatus.PENDING:
            raise ShowError(403)

        self.status = ShowStatus.APPROVED
        self._history_user = user
        self.save()

    def unapprove(self, user):
        if self.status != ShowStatus.APPROVED:
            raise ShowError(404)
        self.status = ShowStatus.PENDING
        self._history_user = user
        self.save()

    def on_air(self, user):
        if self.status != ShowStatus.APPROVED:
            raise ShowError(404)
        self.status = ShowStatus.ONAIR
        self._history_user = user
        self.save()

    def off_air(self, user):
        if self.status != ShowStatus.ONAIR:
            raise ShowError(405)
        self.status = ShowStatus.OFFAIR
        self._history_user = user
        self.save()


class Chat(DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '채팅'
        verbose_name_plural = verbose_name
        ordering = ('registered_at',)

    show = models.ForeignKey(Show, null=False, blank=False, on_delete=models.PROTECT, verbose_name='쇼')
    user = models.ForeignKey(User, null=True, blank=True, verbose_name='작성자', on_delete=models.PROTECT)
    msg = models.CharField(max_length=1000, null=False, blank=False, verbose_name='메시지')
