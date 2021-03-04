import json
from urllib.parse import parse_qs

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer

# views라고 생각하면 됨


# channel : 메시지를 보낼 수 있는 메일함. 한 접속건(사용자)엔 하나의 channel이 부여된다
# group : channel 들의 집합
from django.db import models
from django.db.models import Case, When, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from broadcast.models import BroadCast


class BroadcastConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def get_broadcast(self):
        now = timezone.now()
        try:
            broadcast = BroadCast.objects.get(id=self.broadcast_id, start_at__lte=now, end_at__gte=now)
        except:
            return None
        else:
            return broadcast

    @database_sync_to_async
    def viewer_enter(self):
        self.broadcast.viewer_enter(self.user)

    @database_sync_to_async
    def viewer_leave(self):
        self.broadcast.viewer_leave(self.user)

    @database_sync_to_async
    def get_viewer_count(self):
        return self.broadcast.broadcastviewer_set.aggregate(viewer_count=Coalesce(Sum('action'), 0))['viewer_count']

    # def get_query_params(self):

    async def connect(self):
        print("방송입장")
        self.broadcast_id = self.scope['url_route']['kwargs']['broadcast_id']
        self.broadcast_group = f'broadcast_{str(self.broadcast_id)}'
        self.user = self.scope['user']
        self.is_auth = self.scope['is_auth']
        self.broadcast = await self.get_broadcast()
        self.query_params = {k: v[0] for k, v in parse_qs(self.scope.get('query_string', b'').decode()).items()}
        self.on_broadcast = int(self.query_params.get('onBroadcast', 1))
        if self.is_auth and self.on_broadcast:
            # 로그인 및 방송 페이지 내 접속 입장처리
            await self.viewer_enter()
        viewer_count = await self.get_viewer_count()
        await self.channel_layer.group_add(
            self.broadcast_group,
            self.channel_name
        )
        await self.accept()
        data = {
            "type": "viewer_count",
            "count": viewer_count
        }
        await self.channel_layer.group_send(
            self.broadcast_group,
            data
        )

    async def disconnect(self, code):
        print("방송퇴장")
        await self.channel_layer.group_discard(
            self.broadcast_group,
            self.channel_name
        )
        if self.is_auth and self.on_broadcast:
            await self.viewer_leave()
        viewer_count = await self.get_viewer_count()
        data = {
            "type": "viewer_count",
            "count": viewer_count
        }
        await self.channel_layer.group_send(
            self.broadcast_group,
            data
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        _type = data.get('type', 'echo')
        message = data['message']
        # if self.is_auth is False:
        #     return True
        if _type == "chat_message":
            data = {
                "type": "chat_message",
                "message": message
            }
        else:  # echo
            data = {
                "type": "echo",
                "message": message
            }
        await self.channel_layer.group_send(
            self.broadcast_group,
            data
        )

    async def viewer_count(self, event):
        print("Viewer Count")
        response = {
            "type": "viewer_count",
            "data": {
                "count": int(event['count'])
            }
        }
        await self.send(
            text_data=json.dumps(response)
        )

    # chat_message 함수는 receive의 type:chat_message에서 왔음
    async def chat_message(self, event):
        print("CHAT MESSAGE")
        response = {
            "type": "chat_message",
            "data": {
                "username": self.user.name if self.is_auth else None,
                "message": event['message']
            }
        }
        await self.send(
            text_data=json.dumps(response)
        )

    async def echo(self, event):
        print("ECHO")
        response = {
            "type": "echo",
            "message": event['message']
        }
        await self.send(
            text_data=json.dumps(response)
        )


# ws://127.0.0.1:8000/ws/broadcast/27259b90-60c8-4dcf-83dd-cd30e49f1b97/
class AynscChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONNECT")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        print(self.channel_name)  # channel_name은 세션별로 유일하다
        print(self.scope.keys())
        # user = self.scope['user']
        # print(user)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        print("DISCONNET")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']
        print("RECEIVE")
        data = {
            "type": "chat_message",
            "message": message
        }
        print(data)
        await self.channel_layer.group_send(
            self.room_group_name,
            data
        )

    # chat_message 함수는 receive의 type:chat_message에서 왔음
    async def chat_message(self, event):
        print("CHAT MESSAGE")
        message = event['message']
        await self.send(
            text_data=json.dumps({"message": message})
        )
