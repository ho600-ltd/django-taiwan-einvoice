# taiwan_einvoice/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ESCPOSWebConsumer(WebsocketConsumer):
    def connect(self):
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        self.escpos_web_group_name = 'escpos_web_%s' % self.escpos_web_id
        async_to_sync(self.channel_layer.group_add)(
            self.escpos_web_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.escpos_web_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'taiwan_einvoice_message',
                'message': message
            }
        )

    
    def taiwan_einvoice_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))