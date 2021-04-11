import os

from channels.auth import AuthMiddlewareStack
# from channels.http import AsgiHandler
from channels.db import database_sync_to_async
from channels.routing import ProtocolTypeRouter, URLRouter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.asgi import get_asgi_application
from rest_framework.authtoken.models import Token


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rabang.settings')



class TokenAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    @database_sync_to_async
    def get_user(self, scope):
        headers = dict(scope['headers'])
        scope['is_auth'] = False
        if b'authorization' in headers:
            try:
                token_name, token = headers[b'authorization'].decode().split()
                token = Token.objects.select_related('user').get(key=token)
            except Token.DoesNotExist:
                scope['user'] = AnonymousUser()
            except:
                scope['user'] = AnonymousUser()
            else:
                scope['user'] = token.user if token.user.is_active else AnonymousUser()
                scope['is_auth'] = token.user.is_active
        else:
            scope['user'] = AnonymousUser()
        return scope

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        scope = await self.get_user(scope)
        return await self.app(scope, receive, send)


application = ProtocolTypeRouter({
    "http": get_asgi_application()
})
