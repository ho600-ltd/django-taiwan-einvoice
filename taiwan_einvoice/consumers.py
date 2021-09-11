# taiwan_einvoice/consumers.py
import json, logging
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
        lg = logging.getLogger('django')
        lg.info("close_code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            self.escpos_web_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        serial_number = text_data_json['serial_number']
        invoice_json = text_data_json['invoice_json']
        status = text_data_json.get('status', '')

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'taiwan_einvoice_message',
                'serial_number': serial_number,
                'invoice_json': invoice_json,
                'status': status
            }
        )

    
    def taiwan_einvoice_message(self, event):
        serial_number = event['serial_number']
        invoice_json = event['invoice_json']
        status = event.get('status', '')

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'serial_number': serial_number,
            'invoice_json': invoice_json,
            'status': status
        }))



class ESCPOSWebStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        self.escpos_web_group_name = 'escpos_web_status_%s' % self.escpos_web_id
        async_to_sync(self.channel_layer.group_add)(
            self.escpos_web_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        lg = logging.getLogger('django')
        lg.info("close_code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            self.escpos_web_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        data= json.loads(text_data)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'printers_message',
                'printers': data
            }
        )

    
    def printers_message(self, event):
        printers = event['printers']

        # Send message to WebSocket
        self.send(text_data=json.dumps(printers))