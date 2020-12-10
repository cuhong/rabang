from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from common.models import UUIDPkMixin, DateTimeMixin, PublicImageMixin

User = get_user_model()


def sellerimage_upload_to(instnace, filename):
    return "/".join(['seller', timezone.now().strftime("%Y/%m/%d")])


class SellerImage(UUIDPkMixin, DateTimeMixin, PublicImageMixin, models.Model):
    class Meta:
        verbose_name = '셀러이미지'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    UPLOAD_TO_FUNCTION = sellerimage_upload_to


class Seller(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '셀러'
        verbose_name_plural = verbose_name

    user = models.OneToOneField(User, null=False, blank=False, verbose_name='소유자 계정', on_delete=models.PROTECT)
    name = models.CharField(max_length=100, null=False, blank=False, unique=True, verbose_name='셀러명')
    profile = models.ForeignKey(SellerImage, null=True, blank=True, verbose_name='이미지', on_delete=models.PROTECT)
    contact = models.CharField(max_length=100, null=False, blank=False, verbose_name='대표 연락처')
    email = models.CharField(max_length=100, null=False, blank=False, verbose_name='대표 이메일')
    # 대표자
    rep_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='대표자 실명')
    rep_contact = models.CharField(max_length=100, null=False, blank=False, verbose_name='대표자 연락처')
    rep_email = models.CharField(max_length=100, null=False, blank=False, verbose_name='대표자 이메일')
    # 영업 담당자
    sales_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='영업담당자 실명')
    sales_contact = models.CharField(max_length=100, null=False, blank=False, verbose_name='영업담당자 연락처')
    sales_email = models.CharField(max_length=100, null=False, blank=False, verbose_name='영업담당자 이메일')
    # CS 담당자
    cs_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='cs담당자 실명')
    cs_contact = models.CharField(max_length=100, null=False, blank=False, verbose_name='cs담당자 연락처')
    cs_email = models.CharField(max_length=100, null=False, blank=False, verbose_name='cs담당자 이메일')
    # 배송 담당자
    logistic_name = models.CharField(max_length=100, null=False, blank=False, verbose_name='배송담당자 실명')
    logistic_contact = models.CharField(max_length=100, null=False, blank=False, verbose_name='배송담당자 연락처')
    logistic_email = models.CharField(max_length=100, null=False, blank=False, verbose_name='배송담당자 이메일')

    def __str__(self):
        return self.name


class SellerFkMixin(models.Model):
    class Meta:
        abstract = True

    seller = models.ForeignKey(Seller, null=False, blank=False, verbose_name='셀러', on_delete=models.PROTECT)
