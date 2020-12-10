import requests
from django.contrib.auth import get_user_model
from django.db import models
from solo.models import SingletonModel

from common.models import UUIDPkMixin, DateTimeMixin

User = get_user_model()


class PaymentError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class IMPConfig(SingletonModel):
    code = models.CharField(max_length=300, null=True, blank=True, verbose_name='가맹점 식별코드')
    key = models.CharField(max_length=300, null=True, blank=True, verbose_name='키')
    secret = models.TextField(null=True, blank=True, verbose_name='시크릿')

    @classmethod
    def get_credential(cls):
        config = cls.get_solo()
        if any([config.code is None, config.key is None, config.secret is None]):
            raise PaymentError('아임포트 계정이 설정되지 않았습니다.')
        credential = {
            "code": config.code,
            "key": config.key,
            "secret": config.secret
        }
        return credential

    @classmethod
    def imp_auth(cls):
        imp_url = "https://api.iamport.kr/users/getToken"
        credential = cls.get_credential()
        headers = {"Content-Type": "application/json"}
        data = {
            "imp_key": credential['key'],
            "imp_secret": credential['secret']
        }
        response = requests.post(
            url=imp_url,
            json=data,
            headers=headers
        )
        if response.status_code != 200:
            raise PaymentError('아임포트 인증에 실패했습니다.')
        response_data = response.json()
        if response_data['code'] != 0:
            raise PaymentError('아임포트 인증에 실패했습니다.')
        return response_data['response']['access_token']


class Paymethod(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '결제수단'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    user = models.ForeignKey(User, null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT)
    status = models.IntegerField(
        choices=((0, '대기'), (1, '등록성공'), (2, '등록실패'), (3, '해제')), default=0, null=False, blank=False, verbose_name='상태'
    )
    card_name = models.CharField(max_length=300, null=True, blank=True, verbose_name='카드이름')
    card_nickname = models.CharField(max_length=300, null=True, blank=True, verbose_name='카드별칭')
    error = models.TextField(null=True, blank=True, verbose_name='에러')

    def register_key(self, card_name):
        # 빌링키 등록
        if self.status != 0:
            raise PaymentError('대기 상태가 아닙니다.')
        self.status = 1
        self.card_name = card_name
        self.save()

    def unregister(self):
        # 빌링키 해제
        if self.status != 1:
            raise PaymentError('등록 상태가 아닙니다.')
        self.status = 3
        self.save()

    def pay(self, amount, tax_free, user, uid, pay_title):
        # tax_free는 amount 중 면세 상품금액
        if self.status != 1:
            raise PaymentError(f"결제수단이 {self.get_status_display()} 상태입니다.")
        ledger = PayLedger.objects.create(
            user=user,
            paymethod=self,
            amount=amount,
            tax_free=tax_free,
            uid=uid,
            pay_title=pay_title,
        )
        token = IMPConfig.imp_auth()
        response = requests.post(
            url="https://api.iamport.kr/subscribe/payments/again",
            json={
                "customer_uid": str(self.id),
                "merchant_uid": uid,
                "amount": amount,
                "tax_free": tax_free,
                "name": pay_title
            },
            headers={"Authorization": token}
        )
        if response.status_code != 200:
            ledger.payment_error('아임포트 인증에 실패했습니다.')
            raise PaymentError('아임포트 인증에 실패했습니다.')
        response_data = response.json()
        code = response_data['code']
        message = response_data['message']
        if code == 0:
            pay_result = response_data['response']
            if pay_result['status'] == 'paid':
                ledger.payment_success(response_data)
                return ledger
            else:
                ledger.payment_fail(message, response_data)
                raise PaymentError(f"결제 실패 : {message}")
        else:
            ledger.payment_error(message, data=response_data)
            raise PaymentError(f"결제 오류 : {message}")


class PayLedger(UUIDPkMixin, DateTimeMixin, models.Model):
    class Meta:
        verbose_name = '결제기록'
        verbose_name_plural = verbose_name
        ordering = ('-registered_at',)

    user = models.ForeignKey(User, null=False, blank=False, verbose_name='사용자', on_delete=models.PROTECT, editable=False)
    paymethod = models.ForeignKey(Paymethod, null=False, blank=False, verbose_name='결제수단', on_delete=models.PROTECT, editable=False)
    amount = models.IntegerField(null=False, blank=False, verbose_name='총결제금액', editable=False)
    tax_free = models.IntegerField(null=False, blank=False, verbose_name='면세대상액', editable=False)
    uid = models.TextField(null=False, blank=False, verbose_name='결제 식별자', editable=False)
    imp_uid = models.TextField(null=True, blank=True, verbose_name='아임포트 결제 식별자', editable=False)
    pay_title = models.TextField(null=False, blank=False, verbose_name='결제 적요', editable=False)
    status = models.IntegerField(
        choices=((0, '대기'), (1, '결제성공'), (2, '결제실패'), (3, '오류')), default=0, null=False, blank=False, verbose_name='상태', editable=False
    )
    data = models.JSONField(null=True, blank=True, verbose_name='응답', editable=False)
    error = models.TextField(null=True, blank=True, verbose_name='결제 실패/오류사유', editable=False)
    memo = models.TextField(null=True, blank=True, verbose_name='운영메모')

    # def payment_refund(self, amount, tax_free, memo):

    def payment_success(self, data):
        if self.status != 0:
            raise PaymentError('요청건이 대기 상태가 아닙니다.')
        self.status = 1
        self.imp_uid = data['response']['imp_uid']
        self.data = data
        self.save()

    def payment_error(self, msg, data=None):
        if self.status != 0:
            raise PaymentError('요청건이 대기 상태가 아닙니다.')
        self.status = 3
        self.error = msg
        self.data = data
        self.save()

    def payment_fail(self, msg, data):
        if self.status != 0:
            raise PaymentError('요청건이 대기 상태가 아닙니다.')
        self.status = 2
        self.error = msg
        self.data = data
        self.save()
