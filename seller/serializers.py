from rest_framework import serializers

from seller.models import Seller


class SellerSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['user', 'name']
