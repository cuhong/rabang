import uuid

from django.db import models, transaction
from sequences import get_next_value

from rabang.storages import PublicFileStorage


class SerialMixin(models.Model):
    class Meta:
        abstract = True

    SERIAL_PREFIX = None
    SERIAL_LENGTH = 10

    serial = models.CharField(max_length=100, null=True, blank=True, verbose_name='일련번호', editable=False)

    @classmethod
    def _get_serial(cls):
        with transaction.atomic():
            _sequence = get_next_value(f"{cls._meta.app_label}__{cls._meta.model_name}")
            sequence = f"{cls.SERIAL_PREFIX}-{str(_sequence).zfill(10)}"
        return sequence

    @transaction.atomic
    def set_serial(self):
        if self.serial:
            raise Exception('이미 시리얼이 부여되었습니다.')
        self.serial = self._get_serial()
        self.save()
        return self.serial

    @classmethod
    def populate_serial(cls):
        with transaction.atomic():
            instance_list = cls.objects.select_for_update().filter(serial=None)
            for instance in instance_list:
                instance.set_serial()


class UUIDPkMixin(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(
        default=uuid.uuid4, null=False, blank=False,
        primary_key=True, db_index=True, unique=True,
        editable=False
    )


class DateTimeMixin(models.Model):
    class Meta:
        abstract = True

    registered_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )


class PublicImageMixin(models.Model):
    class Meta:
        abstract = True

    UPLOAD_TO_FUNCTION = ''
    file = models.ImageField(null=False, blank=False, upload_to=UPLOAD_TO_FUNCTION, storage=PublicFileStorage())
