import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from payment.models import IMPConfig, Paymethod


class PaymethodRegisterView(View):
    def get(self, request):
        paymethod_list = Paymethod.objects.values(
            'id', 'card_name', 'card_nickname'
        ).filter(
            user=request.user,
            status=1,
        )
        return render(request, 'payment/register.html', context={'paymethod_list': paymethod_list})

    def post(self, request):
        data = request.POST
        action = data['action']
        try:
            if action == "getUID":
                paymethod = Paymethod.objects.create(user=request.user, card_nickname=data['payNickname'])
                imp_config = IMPConfig.get_credential()
                return_data = {"result": True, "uid": str(paymethod.id), "imp_code": imp_config['code']}
            elif action == "registerPaymethod":
                paymethod = Paymethod.objects.get(user=request.user, id=data['uid'])
                paymethod.register_key(data['card_name'])
                return_data = {"result": True}
            elif action == "unregister":
                paymethod = Paymethod.objects.get(user=request.user, id=data['uid'])
                paymethod.unregister()
                return_data = {"result": True}
            else:
                raise Exception('잘못된 요청')
        except Exception as e:
            return_data = {"result": False, "msg": str(e)}
        return HttpResponse(json.dumps(return_data), content_type='application/json')
