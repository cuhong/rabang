from django.db import models
from django.db.models import Case, When, Count, Q, Sum, Exists, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from broadcast.models import BroadCast, Remonconfig
from broadcast.serializers import BroadCastSerializer, RemonCredentialSerializer
from product.models import Product
from product.serializers import ProductSerializer


class BroadCastPagination(PageNumberPagination):
    page_size = 10


class LiveBroadCastView(ListAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = BroadCastSerializer
    pagination_class = BroadCastPagination

    def get_queryset(self):
        now = timezone.now()
        broadcast_list = BroadCast.objects.prefetch_related('broadcastwait_set', 'broadcastviewer_set').filter(end_at__gte=now).annotate(
            is_on=Case(When(start_at__lte=now, then=True), default=False, output_field=models.BooleanField()),
            viewer_count=Case(
                When(is_on=True, then=Coalesce(Sum('broadcastviewer'), 0)),
                default=0, output_field=models.IntegerField()
            ),
            im_wait=Count(
                'broadcastwait', filter=Q(broadcastwait__user=self.request.user), output_field=models.IntegerField()
            ) if self.request.user.id else Value(
                0, output_field=models.IntegerField()
            )
        )
        return broadcast_list


class GetRemonConfigView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = RemonCredentialSerializer

    def get_object(self):
        return Remonconfig.get_solo()
