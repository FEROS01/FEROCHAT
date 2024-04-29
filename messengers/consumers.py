import json

from asgiref.sync import async_to_sync
from django.template.loader import get_template
from channels.generic.websocket import WebsocketConsumer

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
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": "chat.message", 
                "request": data['request'],
                "sender" : data['sender'],
                "msg_id" : data['msg_id']
                })
        

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def chat_message(self, event):
        data_obj = {
            "request": event["request"],
            "sender": event["sender"],
            "msg_id" : event['msg_id']
        }
        self.send(text_data=json.dumps(data_obj))
