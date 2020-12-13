from rest_framework import serializers

from product.models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'url']
        read_only_fields = ['id']

    url = serializers.SerializerMethodField(method_name='get_url', read_only=True)

    def get_url(self, obj):
        return obj.file.url


class ProductSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'serial', 'name', 'thumbnail', 'simple_description', 'registered_at', 'updated_at']

    thumbnail = ProductImageSerializer(many=False)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'serial', 'name', 'thumbnail', 'simple_description', 'description', 'registered_at', 'updated_at']

    thumbnail = ProductImageSerializer(many=False)
