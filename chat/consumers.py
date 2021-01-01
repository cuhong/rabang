import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.layers import get_channel_layer

# views라고 생각하면 됨


# channel : 메시지를 보낼 수 있는 메일함. 한 접속건(사용자)엔 하나의 channel이 부여된다
# group : channel 들의 집합
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # print(self.scope)
        # print(self.scope['url_route'])
        # print(self.scope['url_route']['kwargs'])
        # print(self.scope['url_route']['kwargs']['room_name'])
        print("CONNECT")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        print("DISCONNET")
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        print("RECEIVE")
        data = {
            "type": "chat_message",
            "message": message
        }
        print(data)
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            data
        )

    # chat_message 함수는 receive의 type:chat_message에서 왔음
    def chat_message(self, event):
        print("CHAT MESSAGE")
        message = event['message']
        self.send(
            text_data=json.dumps({"message": message})
        )


class AynsChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("CONNECT")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        print(self.room_name)
        self.room_group_name = 'chat_%s' % self.room_name
        print(self.channel_name)  # channel_name은 세션별로 유일하다
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

