from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from product.models import Product
from product.serializers import ProductSerializer


class ProductDetailView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            response_data = {
                "result": False,
                "code": 404,
                "msg": "존재하지 않는 상품 ID"
            }
        else:
            response_data = {
                "result": False,
                "code": 200,
                "data": ProductSerializer(product, many=False).data
            }
        response = Response(response_data, status=status.HTTP_200_OK)
        return response

