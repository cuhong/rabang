from django.conf import settings
from django.shortcuts import render
from rest_auth.views import LoginView
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from account.serializers import UserSerializer


class LoginApiView(LoginView):

    def get_response(self):
        serializer_class = self.get_response_serializer()
        serializer = serializer_class(
            instance=self.token, context={'request': self.request}
        )
        response_data = serializer.data
        user_serializer = UserSerializer(self.user)
        for k, v in user_serializer.data.items():
            response_data[k] = v
        response_data['next'] = self.request.data.get('next', None)
        response = Response(response_data, status=status.HTTP_200_OK)
        return response


class IsAuthenticated(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        response_data = {"result": request.user.is_authenticated}
        return Response(response_data)
