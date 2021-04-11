from rest_framework import serializers

from mall.models import Cart
from product.serializers import ProductSimpleSerializer


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'option', 'quantity']
        read_only_fields = ['user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['product'] = ProductSimpleSerializer(instance.product).data
        data['quantity'] = instance.quantity
        return data
