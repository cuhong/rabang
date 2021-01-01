from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Paymethod, IMPConfig


class PaymethodSerializers(serializers.ModelSerializer):
    class Meta:
        model = Paymethod
        fields = ['id', 'card_name', 'card_nickname']
        read_only_fields = ['id']


class PaymentTestView(View):
    def get(self, request):
        from rest_framework.authtoken.models import Token
        paymethod_list = Paymethod.objects.values('id', 'card_nickname').filter(
            user=request.user,
            status=1,
        )
        context = {
            "token": Token.objects.get(user=request.user).key,
            "paymethod_list": paymethod_list
        }
        return render(request, 'payment/register.html', context)


class PaymethodView(APIView):
    def get(self, request):
        paymethod_list = Paymethod.objects.filter(
            user=request.user,
            status=1,
        )
        response = Response(
            PaymethodSerializers(paymethod_list, many=True).data
        )
        return response

    @csrf_exempt
    def post(self, request):
        data = request.data
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
        return Response(return_data, status=status.HTTP_200_OK)
