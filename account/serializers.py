from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from seller.serializers import SellerSimpleSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'cellphone', 'seller']

    seller = serializers.SerializerMethodField(method_name='get_seller')

    def get_seller(self, instance):
        if instance.seller:
            return SellerSimpleSerializer(instance.seller).data
        else:
            return None
