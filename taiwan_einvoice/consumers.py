# taiwan_einvoice/consumers.py
import hashlib
import json, logging, datetime
from asgiref.sync import async_to_sync
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async



def set_name_with_system_hash_key(name):
    sk = settings.SECRET_KEY
    if bytes != type(sk):
        sk = sk.encode('utf-8')
    h = hashlib.md5(b'django-taiwan-einvoice-'+sk).hexdigest()
    return "{}_{}".format(name, h)



def save_print_einvoice_log(escpos_web_id, user, data, invoice_data):
    if not invoice_data['meet_to_tw_einvoice_standard']:
        return
    from taiwan_einvoice.models import LegalEntity, Printer, User, EInvoice, EInvoicePrintLog
    try:
        einvoice = EInvoice.objects.get(id=invoice_data['id'])
    except EInvoice.DoesNotExist:
        return
    try:
        printer = Printer.objects.get(escpos_web__id=escpos_web_id,
                                      serial_number=data['serial_number'])
    except Printer.DoesNotExist:
        return
    if (("3J0002" == einvoice.carrier_type and LegalEntity.GENERAL_CONSUMER_IDENTIFIER != einvoice.buyer_identifier)
        or ("" == einvoice.carrier_type and "" == einvoice.npoban)
       ):
        is_original_copy = not einvoice.einvoiceprintlog_set.exists()
    else:
        is_original_copy = False
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
    return epl


def update_print_einvoice_log(data):
    meet_to_tw_einvoice_standard = data['meet_to_tw_einvoice_standard']
    if not meet_to_tw_einvoice_standard:
        return
    track = data['track_no'][:2]
    no = data['track_no'][2:]
    unixtimestamp = data['unixtimestamp']
    status = data['status']
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
            epl.einvoice.set_print_mark_true(einvoice_print_log=epl)



class ESCPOSWebConsumer(WebsocketConsumer):
    def connect(self):
        lg = logging.getLogger('django')
        self.user = self.scope["user"]
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        if self.user.is_superuser:
            pass
        else:
            if self.user.has_perm('taiwan_einvoice.edit_te_escposweboperator'):
                pass
            else:
                from guardian.shortcuts import get_perms
                from taiwan_einvoice.models import ESCPOSWeb
                try:
                    escpos_web = ESCPOSWeb.objects.get(id=self.escpos_web_id)
                except ESCPOSWeb.DoesNotExist:
                    lg.info("ESCPOSWeb.DoesNotExist: {}".format(self.escpos_web_id))
                    return False
                if 'operate_te_escposweb' in get_perms(self.user, escpos_web):
                    pass
                else:
                    slug, seed, verify_value = self.scope['url_route']['kwargs']['token_auth'].split('-')
                    try:
                        escpos_web = ESCPOSWeb.objects.get(slug=slug)
                    except ESCPOSWeb.DoesNotExist:
                        lg.info("ESCPOSWeb.DoesNotExist: {}".format(slug))
                        return False
                    if not escpos_web.verify_token_auth(seed, verify_value):
                        lg.info("Wrong verify_token_auth: {} {} {}".format(slug, seed, verify_value))
                        return False
        self.escpos_web_group_name = set_name_with_system_hash_key('escpos_web_{}'.format(self.escpos_web_id))
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
        lg = logging.getLogger('django')
        if not self.user.is_authenticated:
            lg.warning("is not authenticated: {}".format(self.user))
            return 
        lg.debug("is authenticated: {}".format(self.user))
        data = json.loads(text_data)
        einvoice_id = int(data.get('einvoice_id', 0))
        pass_key = data.get('pass_key', '')
        serial_number = data['serial_number']
        unixtimestamp = data['unixtimestamp']
        invoice_json = data['invoice_json']
        invoice_data = json.loads(invoice_json)
        invoice_data['details_with_einvoice_in_the_same_paper'] = data.get('details_with_einvoice_in_the_same_paper', False)
        if invoice_data['details_with_einvoice_in_the_same_paper']:
            invoice_data['details_content'].insert(0, {
                "type": "text",
                "custom_size": True,
                "width": 1,
                "height": 3,
                "align": "left",
                "text": '--------  --------  --------',
            })

        einvoice = ''
        if einvoice_id > 0:
            from taiwan_einvoice.models import EInvoice
            if EInvoice.escpos_einvoice_scripts(einvoice_id) in invoice_json:
                if invoice_data['meet_to_tw_einvoice_standard']:
                    einvoice = EInvoice.objects.get(id=einvoice_id)
                    content = einvoice._escpos_einvoice_scripts
                    invoice_data['content'] = content
                    invoice_json = json.dumps(invoice_data)

        if invoice_data['meet_to_tw_einvoice_standard'] and einvoice:
            epl = save_print_einvoice_log(self.escpos_web_id, self.user, data, invoice_data)
            for _i in range(1, 1+len(invoice_data['content'])):
                index = -1 * _i
                line = invoice_data['content'][index]
                ori_word = ":{}:".format(einvoice.generate_no_sha1)
                if 'qrcode_pair' == line['type'] and ori_word in line['qr1_str']:
                    customize_hex_from_id = epl.customize_hex_from_id
                    customize_hex_from_id_len = len(customize_hex_from_id)
                    new_word = ":{}{}:".format(einvoice.generate_no_sha1[:-1*customize_hex_from_id_len], customize_hex_from_id)
                    invoice_data['content'][index]['qr1_str'] = invoice_data['content'][index]['qr1_str'].replace(ori_word, new_word)
                    break
            invoice_data['content'].append({
                "type": "text",
                "custom_size": True,
                "width": 1,
                "height": 1,
                "align": "left",
                "text": _("Print Serial No.:{}").format(epl.id),
            })
            invoice_json = json.dumps(invoice_data)

        lg.debug(invoice_json)
        async_to_sync(self.channel_layer.group_send)(
            self.escpos_web_group_name,
            {
                'pass_key': pass_key,
                'type': 'taiwan_einvoice_message',
                'serial_number': serial_number,
                'unixtimestamp': unixtimestamp,
                'invoice_json': invoice_json,
            }
        )

    
    def taiwan_einvoice_message(self, event):
        pass_key = event['pass_key']
        serial_number = event['serial_number']
        unixtimestamp = event['unixtimestamp']
        invoice_json = event['invoice_json']

        self.send(text_data=json.dumps({
            'pass_key': pass_key,
            'serial_number': serial_number,
            'unixtimestamp': unixtimestamp,
            'invoice_json': invoice_json,
        }))



class ESCPOSWebPrintResultConsumer(WebsocketConsumer):
    def connect(self):
        lg = logging.getLogger('django')
        self.user = self.scope["user"]
        escpos_web = None
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        if self.user.is_superuser:
            pass
        else:
            if self.user.has_perm('taiwan_einvoice.edit_te_escposweboperator'):
                pass
            else:
                from guardian.shortcuts import get_perms
                from taiwan_einvoice.models import ESCPOSWeb
                try:
                    escpos_web = ESCPOSWeb.objects.get(id=self.escpos_web_id)
                except ESCPOSWeb.DoesNotExist:
                    lg.info("ESCPOSWeb.DoesNotExist: {}".format(self.escpos_web_id))
                    return False
                if 'operate_te_escposweb' in get_perms(self.user, escpos_web):
                    pass
                else:
                    slug, seed, verify_value = self.scope['url_route']['kwargs']['token_auth'].split('-')
                    try:
                        escpos_web = ESCPOSWeb.objects.get(slug=slug)
                    except ESCPOSWeb.DoesNotExist:
                        lg.info("ESCPOSWeb.DoesNotExist: {}".format(slug))
                        return False
                    if not escpos_web.verify_token_auth(seed, verify_value):
                        lg.info("Wrong verify_token_auth: {} {} {}".format(slug, seed, verify_value))
                        return False
        if self.user.is_authenticated:
            from taiwan_einvoice.models import ESCPOSWeb, UserConnectESCPOSWebLog
            if not escpos_web:
                try:
                    escpos_web = ESCPOSWeb.objects.get(id=self.escpos_web_id)
                except ESCPOSWeb.DoesNotExist:
                    lg.info("ESCPOSWeb.DoesNotExist: {}".format(self.escpos_web_id))
                    return False
            ucel = UserConnectESCPOSWebLog.objects.get_or_create(escpos_web=escpos_web,
                                                                 user=self.user,
                                                                 channel_name=self.channel_name,
                                                                 is_connected=True,
            )
        self.escpos_web_group_name = set_name_with_system_hash_key('escpos_web_print_result_{}'.format(self.escpos_web_id))
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
        lg = logging.getLogger('django')
        self.user = self.scope["user"]
        escpos_web = None
        self.escpos_web_id = self.scope['url_route']['kwargs']['escpos_web_id']
        if self.user.is_superuser:
            pass
        else:
            if self.user.has_perm('taiwan_einvoice.edit_te_escposweboperator'):
                pass
            else:
                from guardian.shortcuts import get_perms
                from taiwan_einvoice.models import ESCPOSWeb
                try:
                    escpos_web = ESCPOSWeb.objects.get(id=self.escpos_web_id)
                except ESCPOSWeb.DoesNotExist:
                    lg.info("ESCPOSWeb.DoesNotExist: {}".format(self.escpos_web_id))
                    return False
                if 'operate_te_escposweb' in get_perms(self.user, escpos_web):
                    pass
                else:
                    slug, seed, verify_value = self.scope['url_route']['kwargs']['token_auth'].split('-')
                    try:
                        escpos_web = ESCPOSWeb.objects.get(slug=slug)
                    except ESCPOSWeb.DoesNotExist:
                        lg.info("ESCPOSWeb.DoesNotExist: {}".format(slug))
                        return False
                    if not escpos_web.verify_token_auth(seed, verify_value):
                        lg.info("Wrong verify_token_auth: {} {} {}".format(slug, seed, verify_value))
                        return False
        if self.user.is_authenticated:
            from taiwan_einvoice.models import ESCPOSWeb, UserConnectESCPOSWebLog
            if not escpos_web:
                try:
                    escpos_web = ESCPOSWeb.objects.get(id=self.escpos_web_id)
                except ESCPOSWeb.DoesNotExist:
                    lg.info("ESCPOSWeb.DoesNotExist: {}".format(self.escpos_web_id))
                    return False
            ucel = UserConnectESCPOSWebLog.objects.get_or_create(escpos_web=escpos_web,
                                                                 user=self.user,
                                                                 channel_name=self.channel_name,
                                                                 is_connected=True,
            )
        self.escpos_web_group_name = set_name_with_system_hash_key('escpos_web_status_{}'.format(self.escpos_web_id))
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