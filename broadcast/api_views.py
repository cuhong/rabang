from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from broadcast.models import BroadCast, Remonconfig
from broadcast.serializers import BroadCastSerializer
from product.models import Product
from product.serializers import ProductSerializer


class LiveBroadCastView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request):
        now = timezone.now()
        try:
            broadcast = BroadCast.objects.get(
                start_at__lte=now, end_at__gte=now
            )
        except BroadCast.DoesNotExist:
            response_data = {"result": False}
        else:
            ser = BroadCastSerializer(broadcast)
            response_data = {"result": True, "broadcast": ser.data}
        return Response(response_data)


class GetRemonConfigView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def get(self, request):
        remon_credential = Remonconfig.get_credential()
        return Response(remon_credential)
