from django.urls import re_path

from chat import consumers


# urls.py 와 동일한 기능
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.AynsChatConsumer.as_asgi()),
]
