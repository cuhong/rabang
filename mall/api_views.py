from django.db.models import Q
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from mall.models import Cart
from mall.serializers import CartSerializer
from payment.models import Paymethod


class CartView(APIView):
    def get(self, request):
        cart_list = Cart.objects.filter(user=request.user)
        data = CartSerializer(cart_list, many=True)
        return Response(data.data, status=status.HTTP_200_OK)

    def post(self, request):
        cart_serializer = CartSerializer(data=request.data)
        if cart_serializer.is_valid():
            cart_serializer.save(user=request.user)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(cart_serializer.errors, status=status.HTTP_200_OK)


class CartDetailView(APIView):
    def delete(self, request, cart_id):
        try:
            cart = Cart.objects.get(Q(user=request.user) & Q(id=cart_id))
        except:
            return Response({"result": False}, status=status.HTTP_200_OK)
        else:
            cart.delete()
            return Response({"result": True}, status=status.HTTP_200_OK)

    def patch(self, request, cart_id):
        quantity = int(request.data.get('quantity'))
        try:
            cart = Cart.objects.get(Q(user=request.user) & Q(id=cart_id))
        except:
            return Response({"result": False, "msg": "존재하지 않는 카트 id"}, status=status.HTTP_200_OK)
        else:
            cart.quantity = quantity
            cart.save()
            return Response({"result": True, "data": CartSerializer(cart).data}, status=status.HTTP_200_OK)
