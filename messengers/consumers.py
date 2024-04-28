import json

from asgiref.sync import async_to_sync
from django.template.loader import get_template
from channels.generic.websocket import WebsocketConsumer

from .form import NewMessage

class MessagesConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
    
        self.accept()

    
    def receive(self, text_data):
        data = json.loads(text_data)
        # file = self.scope['files']
        print('received')
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": "chat.message", 
                "request": data['request'],
                "sender" : data['sender'],
                "msg_id" : data['msg_id']
                })
        # print(self.scope)
        # new_message = NewMessage(data,file)
        # if new_message.is_valid():
        #     async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, {
        #         "type": "chat.message", "message": 'valid'
        #     }
        # )
        # else:
        #     async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, {
        #         "type": "chat.message", "message": f'invalid {new_message.errors}'
        #     }
        # )
        # message = text_data_json["message"]

        # self.send(text_data=json.dumps({"message": data}))
        

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def chat_message(self, event):
        # Send message to WebSocket
        # self.send(text_data=get_template('chat/base.html').render({'message':message}))
        data_obj = {
            "request": event["request"],
            "sender": event["sender"],
            "msg_id" : event['msg_id']
        }
        self.send(text_data=json.dumps(data_obj))
