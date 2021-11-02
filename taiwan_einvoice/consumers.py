# taiwan_einvoice/consumers.py
import json, logging, datetime
from asgiref.sync import async_to_sync
from django.utils.translation import ugettext_lazy as _
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async



def save_print_einvoice_log(escpos_web_id, user, data, invoice_data):
    if not invoice_data['meet_to_tw_einvoice_standard']:
        return
    from taiwan_einvoice.models import Printer, User, EInvoice, EInvoicePrintLog
    try:
        einvoice = EInvoice.objects.get(id=invoice_data['id'])
    except EInvoice.DoesNotExist:
        return
    try:
        printer = Printer.objects.get(escpos_web__id=escpos_web_id,
                                      serial_number=data['serial_number'])
    except Printer.DoesNotExist:
        return
    is_original_copy = not einvoice.einvoiceprintlog_set.exists()
    epl = EInvoicePrintLog(user=user,
        printer=printer,
        einvoice=einvoice,
        done_status=False,
        is_original_copy=
            True if invoice_data.get('re_print_original_copy', False)
            else is_original_copy,
        print_time=datetime.datetime.utcfromtimestamp(data['unixtimestamp']),
        reason=data.get('reason', ''),
    )
    epl.save()
    return epl.id


def update_print_einvoice_log(data):
    meet_to_tw_einvoice_standard = data['meet_to_tw_einvoice_standard']
    track = data['track_no'][:2]
    no = int(data['track_no'][2:])
    unixtimestamp = data['unixtimestamp']
    status = data['status']
    if not meet_to_tw_einvoice_standard:
        return
    from taiwan_einvoice.models import EInvoicePrintLog
    try:
        epl = EInvoicePrintLog.objects.get(einvoice__track=track,
            einvoice__no=no,
            print_time=datetime.datetime.utcfromtimestamp(unixtimestamp))
    except EInvoicePrintLog.DoesNotExist:
        return
    else:
        epl.done_status = status
        epl.save()
        if status:
            epl.einvoice.set_print_mark_true()



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
        data = json.loads(text_data)
        einvoice_id = int(data.get('einvoice_id', 0))
        serial_number = data['serial_number']
        unixtimestamp = data['unixtimestamp']
        invoice_json = data['invoice_json']
        invoice_data = json.loads(invoice_json)
        if einvoice_id > 0:
            from taiwan_einvoice.models import EInvoice
            if EInvoice.escpos_einvoice_scripts(einvoice_id) in invoice_json:
                if invoice_data['meet_to_tw_einvoice_standard']:
                    ei = EInvoice.objects.get(id=einvoice_id)
                    content = ei._escpos_einvoice_scripts
                    invoice_data['content'] = content
                    invoice_json = json.dumps(invoice_data)

        if invoice_data['meet_to_tw_einvoice_standard']:
            epl_id = save_print_einvoice_log(self.escpos_web_id, self.user, data, invoice_data)
            invoice_data['content'].append({
                "type": "text",
                "custom_size": True,
                "width": 1,
                "height": 1,
                "align": "left",
                "text": _("Print Serial No.:{}").format(epl_id),
            })
            invoice_json = json.dumps(invoice_data)

        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'taiwan_einvoice_message',
                'serial_number': serial_number,
                'unixtimestamp': unixtimestamp,
                'invoice_json': invoice_json,
            }
        )

    
    def taiwan_einvoice_message(self, event):
        serial_number = event['serial_number']
        unixtimestamp = event['unixtimestamp']
        invoice_json = event['invoice_json']

        self.send(text_data=json.dumps({
            'serial_number': serial_number,
            'unixtimestamp': unixtimestamp,
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
        unixtimestamp = text_data_json['unixtimestamp']
        status = text_data_json['status']
        status_message = text_data_json.get('status_message', '')

        update_print_einvoice_log(text_data_json)

        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'type': 'taiwan_einvoice_print_result_message',
                'meet_to_tw_einvoice_standard': meet_to_tw_einvoice_standard,
                'track_no': track_no,
                'unixtimestamp': unixtimestamp,
                'status': status,
                'status_message': status_message,
            }
        )

    
    def taiwan_einvoice_print_result_message(self, event):
        meet_to_tw_einvoice_standard = event['meet_to_tw_einvoice_standard']
        track_no = event['track_no']
        unixtimestamp = event['unixtimestamp']
        status = event['status']
        status_message = event.get('status_message', '')

        self.send(text_data=json.dumps({
            'meet_to_tw_einvoice_standard': meet_to_tw_einvoice_standard,
            'track_no': track_no,
            'unixtimestamp': unixtimestamp,
            'status': status,
            'status_message': status_message,
        }))



def save_printer_status_and_parse_receipt_type(escpos_web_id, data):
    from taiwan_einvoice.models import ESCPOSWeb, Printer
    escpos_web = ESCPOSWeb.objects.get(id=escpos_web_id)
    d = {}
    for k, v in data.items():
        if 'interval_seconds' == k:
            continue
        need_save = False
        try:
            p = Printer.objects.get(serial_number=k)
        except Printer.DoesNotExist:
            p = Printer(escpos_web=escpos_web, serial_number=k)
            need_save = True
        if p.escpos_web != escpos_web:
            p.escpos_web = escpos_web
            need_save = True
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

        data = save_printer_status_and_parse_receipt_type(self.escpos_web_id, data)

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