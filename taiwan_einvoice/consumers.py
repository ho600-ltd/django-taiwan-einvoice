# taiwan_einvoice/consumers.py
import json, logging
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async



def save_print_einvoice_log(escpos_web_id, user, data):
    print("save_print_einvoice_log user: {}".format(user))



class ESCPOSWebConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_superuser:
            from taiwan_einvoice.models import ESCPOSWeb
            slug, seed, verify_value = self.scope['url_route']['kwargs']['token_auth'].split('-')
            try:
                escpos_web = ESCPOSWeb.objects.get(slug=slug)
            except ESCPOSWeb.DoesNotExist:
                return False
            if not escpos_web.verify_token_auth(seed, verify_value):
                return False
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        self.escpos_web_group_name = 'escpos_web_%s' % self.escpos_web_id
        async_to_sync(self.channel_layer.group_add)(
            self.escpos_web_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        lg = logging.getLogger('django')
        lg.info("close_code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            self.escpos_web_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        if not self.user.is_authenticated:
            return 
        text_data_json = json.loads(text_data)
        serial_number = text_data_json['serial_number']
        batch_no = text_data_json['batch_no']
        invoice_json = text_data_json['invoice_json']

        data = save_print_einvoice_log(self.escpos_web_id, self.user, text_data_json)

        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'taiwan_einvoice_message',
                'serial_number': serial_number,
                'batch_no': batch_no,
                'invoice_json': invoice_json,
            }
        )

    
    def taiwan_einvoice_message(self, event):
        serial_number = event['serial_number']
        batch_no = event['batch_no']
        invoice_json = event['invoice_json']

        self.send(text_data=json.dumps({
            'serial_number': serial_number,
            'batch_no': batch_no,
            'invoice_json': invoice_json,
        }))



class ESCPOSWebPrintResultConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_superuser:
            from taiwan_einvoice.models import ESCPOSWeb
            slug, seed, verify_value = self.scope['url_route']['kwargs']['token_auth'].split('-')
            try:
                escpos_web = ESCPOSWeb.objects.get(slug=slug)
            except ESCPOSWeb.DoesNotExist:
                return False
            if not escpos_web.verify_token_auth(seed, verify_value):
                return False
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        if self.user.is_authenticated and self.user.has_perm('taiwan_einvoice.print_einvoice'):
            from taiwan_einvoice.models import ESCPOSWeb, UserConnectESCPOSWebLog
            escpos_web = ESCPOSWeb.objects.get(id=self.escpos_web_id)
            ucel = UserConnectESCPOSWebLog.objects.get_or_create(escpos_web=escpos_web,
                                                                 user=self.user,
                                                                 channel_name=self.channel_name,
                                                                 is_connected=True,
            )
        self.escpos_web_group_name = 'escpos_web_print_result_%s' % self.escpos_web_id
        async_to_sync(self.channel_layer.group_add)(
            self.escpos_web_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        lg = logging.getLogger('django')
        lg.info("close_code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            self.escpos_web_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        lg = logging.getLogger('django')
        meet_to_tw_einvoice_standard = text_data_json['meet_to_tw_einvoice_standard']
        track_no = text_data_json['track_no']
        batch_no = text_data_json['batch_no']
        status = text_data_json['status']
        status_message = text_data_json.get('status_message', '')

        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'taiwan_einvoice_print_result_message',
                'meet_to_tw_einvoice_standard': meet_to_tw_einvoice_standard,
                'track_no': track_no,
                'batch_no': batch_no,
                'status': status,
                'status_message': status_message,
            }
        )

    
    def taiwan_einvoice_print_result_message(self, event):
        meet_to_tw_einvoice_standard = event['meet_to_tw_einvoice_standard']
        track_no = event['track_no']
        batch_no = event['batch_no']
        status = event['status']
        status_message = event.get('status_message', '')

        self.send(text_data=json.dumps({
            'meet_to_tw_einvoice_standard': meet_to_tw_einvoice_standard,
            'track_no': track_no,
            'batch_no': batch_no,
            'status': status,
            'status_message': status_message,
        }))



def save_printer_status(escpos_web_id, data):
    from taiwan_einvoice.models import ESCPOSWeb, Printer
    escpos_web = ESCPOSWeb.objects.get(id=escpos_web_id)
    d = {}
    for k, v in data.items():
        if 'interval_seconds' == k:
            continue
        need_save = False
        try:
            p = Printer.objects.get(escpos_web=escpos_web, serial_number=k)
        except Printer.DoesNotExist:
            p = Printer(escpos_web=escpos_web, serial_number=k)
        if v['nickname'] != p.nickname:
            p.nickname = v['nickname']
            need_save = True
        if v['receipt_type'] != p.receipt_type:
            p.receipt_type = v['receipt_type']
            need_save = True
        if need_save:
            p.save()
        data[k]['receipt_type_display'] = p.get_receipt_type_display()
    return data



class ESCPOSWebStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_superuser:
            from taiwan_einvoice.models import ESCPOSWeb
            slug, seed, verify_value = self.scope['url_route']['kwargs']['token_auth'].split('-')
            try:
                escpos_web = ESCPOSWeb.objects.get(slug=slug)
            except ESCPOSWeb.DoesNotExist:
                return False
            if not escpos_web.verify_token_auth(seed, verify_value):
                return False
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        if self.user.is_authenticated and self.user.has_perm('taiwan_einvoice.print_einvoice'):
            from taiwan_einvoice.models import ESCPOSWeb, UserConnectESCPOSWebLog
            escpos_web = ESCPOSWeb.objects.get(id=self.escpos_web_id)
            ucel = UserConnectESCPOSWebLog.objects.get_or_create(escpos_web=escpos_web,
                                                                 user=self.user,
                                                                 channel_name=self.channel_name,
                                                                 is_connected=True,
            )
        self.escpos_web_group_name = 'escpos_web_status_%s' % self.escpos_web_id
        async_to_sync(self.channel_layer.group_add)(
            self.escpos_web_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        lg = logging.getLogger('django')
        lg.info("close_code: {}".format(close_code))
        async_to_sync(self.channel_layer.group_discard)(
            self.escpos_web_group_name,
            self.channel_name
        )


    def receive(self, text_data):
        data= json.loads(text_data)

        data = save_printer_status(self.escpos_web_id, data)

        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'printers_message',
                'printers': data
            }
        )

    
    def printers_message(self, event):
        printers = event['printers']

        self.send(text_data=json.dumps(printers))


    def show_error_message(self, event):
        #INFO: show_error_message trigger in taiwan_einvoice.signals.on_user_logout
        error_message = event['error_message']

        self.send(text_data=json.dumps(error_message))