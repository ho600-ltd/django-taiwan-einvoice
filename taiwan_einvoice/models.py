import pytz, datetime, hmac, requests, urllib3
from hashlib import sha256
from base64 import b64encode, b64decode
from binascii import unhexlify 
from Crypto.Cipher import AES
from hashlib import sha1
from random import random, randint
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Max
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from simple_history.models import HistoricalRecords

from ho600_ltd_libraries.utils.formats import customize_hex_from_integer, integer_from_customize_hex


def _pad(byte_array):
    BLOCK_SIZE = 16
    pad_len = BLOCK_SIZE - len(byte_array) % BLOCK_SIZE
    return byte_array + (bytes([pad_len]) * pad_len)

def _unpad(byte_array):
    last_byte = byte_array[-1]
    return byte_array[0:-last_byte]

def qrcode_aes_encrypt(key, plain_text):
    iv = b64decode('Dt8lyToo17X/XkXaQvihuA==')
    key = unhexlify(key)
    cipher = AES.new(key, mode=AES.MODE_CBC, IV=iv)
    pad_string = _pad(plain_text.encode('utf-8'))
    return b64encode(cipher.encrypt(pad_string)).decode('utf-8')

KEY_CODE_SET = [
    'C', 'W', 'B', 'E', 'R', 'T', 'Y','6', '7', '8',
    'U', 'P', 'K', 'X', 'A', 'S', 'D', 'V', 'F', 'H',
    '3', '5',
]
def get_codes(verify_id, seed=0):
    if seed <= 0:
        seed = randint(234256, 702768)
    seed = seed % 234256
    code1_n = (seed // 10648)
    code1 = KEY_CODE_SET[code1_n]
    code2_n = (seed % 10648) // 484
    code2 = KEY_CODE_SET[code2_n]
    code3_n = (seed % 10648) % 484 // 22
    code3 = KEY_CODE_SET[code3_n]
    code4_n = (seed % 10648) % 484 % 22
    code4 = KEY_CODE_SET[code4_n]
    code5 = KEY_CODE_SET[((code1_n + code2_n + code3_n + code4_n) ** 3 + verify_id) % 22]
    return ''.join((code1, code2, code3, code4, code5))


TAIPEI_TIMEZONE = pytz.timezone('Asia/Taipei')



class EInvoiceSellerAPI(models.Model):
    url = 'https://www-vc.einvoice.nat.gov.tw/BIZAPIVAN/biz'



    AppId = models.CharField(max_length=18, unique=True)
    APIKey = models.CharField(max_length=24, null=False)
    proxy = models.CharField(max_length=64, null=True)


    def __str__(self):
        return "{} with {}".format(self.AppId, self.proxy)



    def get_hmacsha256_sign(self, plain_text=None, **kwargs):
        key = bytes(self.APIKey, 'utf-8')
        if bytes == type(plain_text):
            b_text = plain_text
        else:
            b_text = plain_text.encode('utf-8')
        signed_hmac_sha256 = hmac.new(key, b_text, sha256)
        return b64encode(signed_hmac_sha256.digest())


    def post_data(self, data):
        data["timeStamp"] = int(datetime.datetime.now().timestamp()+180)
        s = []
        for key in sorted(data):
            s.append("{}={}".format(key, data[key]))
        _s = "&".join(s)
        data['signature'] = self.get_hmacsha256_sign(_s)

        requests.packages.urllib3.disable_warnings()
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        try:
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
        except AttributeError:
            pass
        for _proxy in self.proxy.split(';'):
            client_kw = {}
            if _proxy:
                proxies = {'http': _proxy, 'https': _proxy}
                client_kw['proxies'] = proxies
            try:
                result = requests.post(self.url,
                                       data=data,
                                       headers={'Content-Type':
                                                'application/x-www-form-urlencoded'},
                                       **client_kw)
            except:
                pass
            else:
                return result.json()
        return {"code": "?"}


    def set_api_result(self, type, key):
        create_new = False
        try:
            eiar = EInvoiceAPIResult.objects.get(type=type, key=key)
        except EInvoiceAPIResult.DoesNotExist:
            create_new = True
        else:
            if False == eiar.success:
                eiar.delete()
                create_new = True
        if create_new:
            eiar = EInvoiceAPIResult(type=type, key=key)
            eiar.save()
        return eiar


    def inquery_mobile_barcode(self, type, key, api_result):
        data = {
            "version": "1.0",
            "action": "bcv",
            "barCode": key,
            "TxID": api_result.id,
            "appId": self.AppId,
        }
        result = self.post_data(data)
        if 'Y' == result.get('isExist', 'N') and '200' == str(result.get('code', '')):
            api_result.success = True
        else:
            api_result.value = result
        api_result.save()
        return api_result.success


    def inquery_donate_mark(self, type, key, api_result):
        data = {
            "version": "1.0",
            "action": "preserveCodeCheck",
            "pCode": key,
            "TxID": api_result.id,
            "appId": self.AppId,
        }
        result = self.post_data(data)
        if 'Y' == result.get('isExist', 'N') and '200' == str(result.get('code', '')):
            api_result.success = True
        else:
            api_result.value = result
        api_result.save()
        return api_result.success


    def inquery_seller_identifier(self, type, key, api_result):
        data = {
            "version": "1.0",
            "action": "qryBanUnitTp",
            "ban": key,
            "serial": api_result.id,
            "appId": self.AppId,
        }
        result = self.post_data(data)
        print(result)
        if 'Y' == result.get('banUnitTpStatus', 'N') and '200' == str(result.get('code', '')):
            api_result.success = True
        else:
            api_result.value = result
        api_result.save()
        return api_result.success


    def inquery_seller_enable_einvoice(self, type, key, api_result):
        data = {
            "version": "1.0",
            "action": "qryRecvRout",
            "ban": key,
            "serial": api_result.id,
            "TxID": api_result.id,
            "appId": self.AppId,
        }
        result = self.post_data(data)
        if 'Y' == result.get('recvRoutStatus', 'N') and '200' == str(result.get('code', '')):
            api_result.success = True
        else:
            api_result.value = result
        api_result.save()
        return api_result.success


    def inquery(self, type_str, key):
        type = EInvoiceAPIResult.type_choices_reverse_dict[type_str]
        api_result = self.set_api_result(type, key)
        if 'mobile-barcode' == type_str:
            if api_result.success:
                return api_result.success
            else:
                return self.inquery_mobile_barcode(type, key, api_result)
        elif 'donate-mark' == type_str:
            if api_result.success:
                return api_result.success
            else:
                return self.inquery_donate_mark(type, key, api_result)
        elif 'seller-identifier' == type_str:
            if api_result.success:
                return api_result.success
            else:
                return self.inquery_seller_identifier(type, key, api_result)
        elif 'seller-enable-einvoice' == type_str:
            if api_result.success:
                return api_result.success
            else:
                return self.inquery_seller_enable_einvoice(type, key, api_result)



class EInvoiceFieldError(Exception):
    pass



class MobileBarcodeDoesNotExist(Exception):
    pass



class NPOBnDoesNotExist(Exception):
    pass



class SellerDoesNotEnableEInvoice(Exception):
    pass



class IdentifierDoesNotExist(Exception):
    pass



class EInvoiceAPIResult(models.Model):
    type_choices = (
        ('1', 'mobile-barcode'),
        ('2', 'donate-mark'),
        ('3', 'seller-enable-einvoice'),
        ('4', 'seller-identifier'),
    )
    type_choices_dict = dict(type_choices)
    type_choices_reverse_dict = {v: k for k, v in type_choices_dict.items()}
    type = models.CharField(max_length=1, choices=type_choices)
    key = models.CharField(max_length=40)
    success = models.BooleanField(default=False)
    value = models.TextField()



    class Meta:
        unique_together = (('type', 'key'), )



class ESCPOSWeb(models.Model):
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=5, default='')
    hash_key = models.CharField(max_length=40, default='')



    @property
    def mask_hash_key(self):
        return self.hash_key[:4] + '********************************' + self.hash_key[-4:]


    def verify_token_auth(self, seed, verify_value):
        if self.escposwebconnectionlog_set.filter(seed=seed).exists():
            return False
        elif verify_value == sha1("{}-{}".format(self.slug, seed).encode('utf-8')).hexdigest():
            escpos_web_cl = ESCPOSWebConnectionLog(escpos_web=self, seed=seed)
            escpos_web_cl.save()
            return True
        return False


    def save(self, *args, **kwargs):
        if not self.slug:
            if self.pk:
                _fake_pk = self.pk
            else:
                _fake_pk = ESCPOSWeb.objects.count() + 1
            while True:
                slug = get_codes(_fake_pk)
                if not ESCPOSWeb.objects.filter(slug=slug).exists():
                    self.slug = slug
                    break
        if not self.hash_key:
            self.hash_key = sha1(str(random()).encode('utf-8')).hexdigest()
        super(ESCPOSWeb, self).save(*args, **kwargs)



class ESCPOSWebConnectionLog(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    escpos_web = models.ForeignKey(ESCPOSWeb, on_delete=models.DO_NOTHING)
    seed = models.CharField(max_length=15)


    class Meta:
        unique_together = (('escpos_web', 'seed', ), )



class UserConnectESCPOSWebLog(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    escpos_web = models.ForeignKey(ESCPOSWeb, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    channel_name = models.CharField(max_length=255, default='')
    is_connected = models.BooleanField(default=True)



class Printer(models.Model):
    RECEIPT_TYPES = (
        ('5', _('58mm Receipt')),
        ('6', _('58mm E-Invoice')),
        ('8', _('80mm Receipt')),
    )
    escpos_web = models.ForeignKey(ESCPOSWeb, on_delete=models.DO_NOTHING)
    serial_number = models.CharField(max_length=128, unique=True)
    nickname = models.CharField(max_length=64, unique=True)
    receipt_type = models.CharField(max_length=1, choices=RECEIPT_TYPES)
    


class IdentifierRule(object):
    """ Official rules from https://www.fia.gov.tw/singlehtml/6?cntId=aaa97a9dcf2649d5bdd317f554e24f75
    Now, the rules use pass_rule_has_7_times_10, pass_rule_has_no_7_times_10.
    After 2023-Apr-01, the rules use pass_rule_has_7_times_5, pass_rule_has_no_7_times_5.
    """ 
    def pass_rule_has_7_times_10(no):
        pass
    def pass_rule_has_no_7_times_10(no):
        pass
    def pass_rule_has_7_times_5(no):
        pass
    def pass_rule_has_no_7_times_5(no):
        pass
    def verify_identifier(self, identifier):
        if (self.pass_rule_has_7_times_10(identifier)
            or self.pass_rule_has_no_7_times_10(identifier)
            or self.pass_rule_has_7_times_5(identifier)
            or self.pass_rule_has_no_7_times_5(identifier)):
            return True
        return False



class LegalEntity(models.Model, IdentifierRule):
    GENERAL_CONSUMER_IDENTIFIER = '0000000000'
    identifier = models.CharField(max_length=10, null=False, blank=False, db_index=True)
    name = models.CharField(max_length=60, default='', db_index=True)
    address = models.CharField(max_length=100, default='', db_index=True)
    person_in_charge = models.CharField(max_length=30, default='', db_index=True)
    telephone_number = models.CharField(max_length=26, default='', db_index=True)
    facsimile_number = models.CharField(max_length=26, default='', db_index=True)
    email_address = models.CharField(max_length=80, default='', db_index=True)
    customer_number_char = models.CharField(max_length=20, default='', db_index=True)
    @property
    def customer_number(self):
        if not self.customer_number_char:
            return str(self.pk)
        else:
            return self.customer_number_char
    @customer_number.setter
    def customer_number(self, char):
        self.customer_number_char = char
        self.save()
    role_remark = models.CharField(max_length=40, default='', db_index=True)


    class Meta:
        unique_together = (('identifier', 'customer_number_char'), )
    

    def __str__(self):
        return "{}({}/{})".format(self.identifier, self.name, self.customer_number)



class Seller(models.Model):
    legal_entity = models.ForeignKey(LegalEntity, unique=True, on_delete=models.DO_NOTHING)
    print_with_seller_optional_fields = models.BooleanField(default=False)
    print_with_buyer_optional_fields = models.BooleanField(default=False)
    

    def __str__(self):
        return "{}: {}, {}".format(self.legal_entity,
                                   self.print_with_seller_optional_fields,
                                   self.print_with_buyer_optional_fields)



class TurnkeyWeb(models.Model):
    on_working = models.BooleanField(default=True)
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=32)
    hash_key = models.CharField(max_length=40)
    transport_id = models.CharField(max_length=10)
    party_id = models.CharField(max_length=10)
    routing_id = models.CharField(max_length=39)
    qrcode_seed = models.CharField(max_length=40)
    turnkey_seed = models.CharField(max_length=40)
    download_seed = models.CharField(max_length=40)
    epl_base_set = models.CharField(max_length=64, default='')
    history = HistoricalRecords()
    @property
    def count_now_use_07_sellerinvoicetrackno_blank_no(self):
        count = 0
        for sitn in SellerInvoiceTrackNo.filter_now_use_sitns(turnkey_web=self).filter(type='07'):
            count += sitn.count_blank_no
        return count
    @property
    def count_now_use_08_sellerinvoicetrackno_blank_no(self):
        count = 0
        for sitn in SellerInvoiceTrackNo.filter_now_use_sitns(turnkey_web=self).filter(type='08'):
            count += sitn.count_blank_no
        return count
    @property
    def mask_hash_key(self):
        return self.hash_key[:4] + '********************************' + self.hash_key[-4:]
    @property
    def mask_qrcode_seed(self):
        return self.qrcode_seed[:4] + '************************' + self.qrcode_seed[-4:]
    @property
    def mask_turnkey_seed(self):
        return self.turnkey_seed[:4] + '************************' + self.turnkey_seed[-4:]
    @property
    def mask_download_seed(self):
        return self.download_seed[:4] + '************************' + self.download_seed[-4:]
    @property
    def mask_epl_base_set(self):
        return self.epl_base_set[:4] + '*'*(len(self.epl_base_set)-8) + self.epl_base_set[-4:]


    note = models.TextField()


    def __str__(self):
        return "{}({}:{}:{})".format(self.name,
                                     self.transport_id,
                                     self.party_id,
                                     self.routing_id)
    

    def save(self, *args, **kwargs):
        if not self.hash_key:
            self.hash_key = sha1(str(random()).encode('utf-8')).hexdigest()
            
        super(TurnkeyWeb, self).save(*args, **kwargs)



    class Meta:
        unique_together = (('seller', 'name'), )
        permissions = (
            ("add_te_sellerinvoicetrackno", "Add Seller Invoice Track No"),
            ("view_te_einvoice", "View E-Invoice"),
            ("print_te_einvoice", "Print E-Invoice"),
        )
    


class SellerInvoiceTrackNo(models.Model):
    turnkey_web = models.ForeignKey(TurnkeyWeb, on_delete=models.DO_NOTHING)
    type_choices = (
        ('07', _('General')),
        ('08', _('Special')),
    )
    type = models.CharField(max_length=2, default='07', choices=type_choices)
    @property
    def type__display(self):
        return self.get_type_display()
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    @property
    def year_month_range(self):
        chmk_year = self.begin_time.astimezone(TAIPEI_TIMEZONE).year - 1911
        begin_month = self.begin_time.astimezone(TAIPEI_TIMEZONE).month
        end_month = begin_month + 1
        return "{}年{}-{}月".format(chmk_year, begin_month, end_month)
    track = models.CharField(max_length=2)
    begin_no = models.IntegerField()
    end_no = models.IntegerField()



    class Meta:
        unique_together = (("type", "begin_time", "end_time", "track", "begin_no", "end_no"), )



    def __str__(self):
        return "{}{}({}~{}: {}{}-{})".format(self.turnkey_web,
                                             self.type,
                                             self.begin_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d'),
                                             (self.end_time-datetime.timedelta(seconds=1)).astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d'),
                                             self.track,
                                             self.begin_no,
                                             self.end_no)


    @classmethod
    def filter_now_use_sitns(cls, *args, **kwargs):
        if 'ignore_count_blank_no' in kwargs:
            ignore_count_blank_no = kwargs['ignore_count_blank_no']
            del kwargs['ignore_count_blank_no']
        else:
            ignore_count_blank_no = False
        queryset = cls.objects.filter(**kwargs)
        _now = now()
        ids = []
        for sitn in queryset.filter(begin_time__lte=_now,
                                    end_time__gt=_now).order_by('track', 'begin_no'):
            if ignore_count_blank_no:
                ids.append(sitn.id)
            elif sitn.count_blank_no > 0:
                ids.append(sitn.id)
        queryset = queryset.filter(id__in=ids)
        return queryset


    @property
    def count_blank_no(self):
        return self.end_no - self.begin_no + 1 - self.einvoice_set.count()


    @property
    def next_blank_no(self):
        return ''
    

    def create_einvoice(self, data):
        data['seller_invoice_track_no'] = self
        data['type'] = self.type
        data['track'] = self.track
        max_no = self.einvoice_set.filter(no__gte=self.begin_no, no__lte=self.end_no).aggregate(Max('no'))['no__max']
        if not max_no:
            data['no'] = self.begin_no
        elif max_no >= self.end_no:
            raise Exception('Not enough numbers')
        else:
            data['no'] = max_no + 1
        ei = EInvoice(**data)
        ei.save()
        return ei



class EInvoice(models.Model):
    only_fields_can_update = ['print_mark']
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    seller_invoice_track_no = models.ForeignKey(SellerInvoiceTrackNo, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=2, default='07', choices=SellerInvoiceTrackNo.type_choices)
    track = models.CharField(max_length=2, db_index=True)
    no = models.IntegerField(db_index=True)
    @property
    def track_no(self):
        return "{}{}".format(self.track, self.no)
    @property
    def track_no_(self):
        return "{}-{}".format(self.track, self.no)
    carrier_type_choices = (
        ('3J0002', _('Mobile barcode')),
    )
    carrier_type = models.CharField(max_length=6, default='', choices=carrier_type_choices, db_index=True)
    @property
    def carrier_type__display(self):
        return self.get_carrier_type_display()

    carrier_id1 = models.CharField(max_length=64, default='', db_index=True)
    carrier_id2 = models.CharField(max_length=64, default='', db_index=True)
    npoban = models.CharField(max_length=7, default='', db_index=True)
    @property
    def donate_mark(self):
        if self.npoban:
            return '1'
        else:
            return '0'
    print_mark = models.BooleanField(default=False)
    random_number = models.CharField(max_length=4, null=False, blank=False, db_index=True)
    generate_time = models.DateTimeField(auto_now_add=True, db_index=True)
    generate_batch_no = models.CharField(max_length=40, default='')
    generate_batch_no_sha1 = models.CharField(max_length=10, default='')

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')

    seller_identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    seller_name = models.CharField(max_length=60, default='', db_index=True)
    seller_address = models.CharField(max_length=100, default='', db_index=True)
    seller_person_in_charge = models.CharField(max_length=30, default='', db_index=True)
    seller_telephone_number = models.CharField(max_length=26, default='', db_index=True)
    seller_facsimile_number = models.CharField(max_length=26, default='', db_index=True)
    seller_email_address = models.CharField(max_length=80, default='', db_index=True)
    seller_customer_number = models.CharField(max_length=20, default='', db_index=True)
    seller_role_remark = models.CharField(max_length=40, default='', db_index=True)
    buyer = models.ForeignKey(LegalEntity, on_delete=models.DO_NOTHING)
    buyer_identifier = models.CharField(max_length=10, null=False, blank=False, db_index=True)
    buyer_name = models.CharField(max_length=60, default='', db_index=True)
    buyer_address = models.CharField(max_length=100, default='', db_index=True)
    buyer_person_in_charge = models.CharField(max_length=30, default='', db_index=True)
    buyer_telephone_number = models.CharField(max_length=26, default='', db_index=True)
    buyer_facsimile_number = models.CharField(max_length=26, default='', db_index=True)
    buyer_email_address = models.CharField(max_length=80, default='', db_index=True)
    buyer_customer_number = models.CharField(max_length=20, default='', db_index=True)
    buyer_role_remark = models.CharField(max_length=40, default='', db_index=True)
    details = models.JSONField(null=False)
    amounts = models.JSONField(null=False)



    class Meta:
        unique_together = (('seller_invoice_track_no', 'track', 'no'), )
    

    @property
    def one_dimension_barcode_str(self):
        chmk_year = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).year - 1911
        begin_month = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).month
        end_month = begin_month + 1
        barcode_str = "{}{}{}{}".format(
            chmk_year,
            end_month,
            self.track_no,
            self.random_number,
        )
        return barcode_str


    @classmethod
    def escpos_einvoice_scripts(cls, id=0):
        _sha1 = sha1(str(id).encode('utf-8')).hexdigest()
        return "*{}*".format(_sha1)


    @property
    def _escpos_einvoice_scripts(self):
        def _hex_amount(amount):
            a = hex(int(amount))[2:]
            return '0' * (8 - len(a)) + a
        if '' != self.carrier_type:
            carrier_id1 = self.carrier_id1
            if carrier_id1 == self.carrier_id2:
                carrier_id2 = ''
            message = _("Carrier Type: {carrier_type} {carrier_id1} {carrier_id2}").format(
                carrier_type=self.get_carrier_type_display(),
                carrier_id1=carrier_id1, carrier_id2=carrier_id2,
            )
            return [
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "列  印  說  明"},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "barcode", "align_ct": True, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": self.one_dimension_barcode_str},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": message},
            ]
        elif '' != self.npoban:
            message = _("Donate to NPO( {npoban} )").format(
                npoban=self.npoban,
            )
            return [
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "列  印  說  明"},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "barcode", "align_ct": True, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": self.one_dimension_barcode_str},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": message},
            ]
        else:
            details = self.details
            amounts = self.amounts
            chmk_year = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).year - 1911
            begin_month = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).month
            end_month = begin_month + 1
            generate_time = self.generate_time.astimezone(TAIPEI_TIMEZONE)
            sales_amount_str = _hex_amount(amounts['SalesAmount'])
            total_amount_str = _hex_amount(amounts['TotalAmount'])
            return [
                    {"type": "text", "custom_size": True, "width": 1, "height": 2, "align": "center", "text": "電 子 發 票 證 明 聯"},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                    {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": " {}".format(generate_time.strftime('%Y-%m-%d %H:%M:%S'))},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": " 隨機碼 {} 總計 {}".format(self.random_number, amounts['TotalAmount'])},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left",
                        "text": " 賣方 {} {}".format(self.seller_identifier,
                                                        "" if '0000000000' == self.buyer_identifier else "買方 "+self.buyer_identifier)},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "barcode", "align_ct": True, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": self.one_dimension_barcode_str},
                    {"type": "qrcode_pair", "center": False,
                        "qr1_str": "{track_no}{year_m_d}{random_number}{sales_amount}{total_amount}{buyer_identifier}{seller_identifier}{qrcode_aes_encrypt_str}:{generate_batch_no_sha1}:{product_in_einvoice_count}:{product_in_order_count}:{codepage}:".format(
                            track_no=self.track_no,
                            year_m_d="{}{}".format(chmk_year, generate_time.strftime('%m%d')),
                            random_number=self.random_number,
                            sales_amount=sales_amount_str,
                            total_amount=total_amount_str,
                            buyer_identifier="00000000" if '0000000000' == self.buyer_identifier else self.buyer_identifier,
                            seller_identifier=self.seller_identifier,
                            generate_batch_no_sha1=self.generate_batch_no_sha1,
                            qrcode_aes_encrypt_str=qrcode_aes_encrypt(self.seller_invoice_track_no.turnkey_web.qrcode_seed, "{}{}".format(self.track_no, self.random_number)),
                            product_in_einvoice_count=len(details[:5]),
                            product_in_order_count=len(details),
                            codepage='1' if 'utf-8' else '0',
                        ),
                        "qr2_str": "**" + ":".join(
                            ["{}:{}:{}".format(_p['Description'].replace(":", "-"), _p['Quantity'], _p['UnitPrice'])
                                for _p in details[:5]]),
                    },
                ]


    @property
    def details_content(self):
        if hasattr(self.content_object, 'escpos_print_scripts_of_details'):
            details_content = self.content_object.escpos_print_scripts_of_details()
        else:
            details_content = [
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": _("No details")},
            ]
        return details_content


    @property
    def escpos_print_scripts(self):
        _d = {
            "meet_to_tw_einvoice_standard": True,
            "print_mark": self.print_mark,
            "id": self.id,
            "track_no": self.track_no,
            "generate_time": self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S%z'),
            "width": "58mm",
            "content": EInvoice.escpos_einvoice_scripts(self.id),
        }
        _d["details_content"] = self.details_content
        return _d


    def set_print_mark_true(self):
        if '' != self.carrier_type or '' != self.npoban:
            pass
        elif False == self.print_mark and 'print_mark' in self.only_fields_can_update:
            EInvoice.objects.filter(id=self.id).update(print_mark=True)
    

    def delete(self, *args, **kwargs):
        raise Exception('Can not delete')


    def save(self, *args, **kwargs):
        if kwargs.get('force_save', False):
            del kwargs['force_save']
            super().save(*args, **kwargs)
        elif not self.pk:
            turnkey_web = self.seller_invoice_track_no.turnkey_web
            while True:
                random_number = '{:04d}'.format(randint(0, 10000))
                objs = self._meta.model.objects.filter(seller_invoice_track_no__turnkey_web=turnkey_web).order_by('-id')[:1000]
                if not objs.exists():
                    break
                else:
                    obj = objs[len(objs)-1]
                    if not self._meta.model.objects.filter(id__gte=obj.id,
                                                           seller_invoice_track_no__turnkey_web=turnkey_web,
                                                           random_number=random_number).exists():
                        break
            self.random_number = random_number
            self.generate_batch_no_sha1 = sha1(self.generate_batch_no.encode('utf-8')).hexdigest()[:10]
            super().save(*args, **kwargs)
        


class EInvoicePrintLog(models.Model):
    user = models.ForeignKey(User, default=102, on_delete=models.DO_NOTHING)
    printer = models.ForeignKey(Printer, on_delete=models.DO_NOTHING)
    einvoice = models.ForeignKey(EInvoice, on_delete=models.DO_NOTHING)
    is_original_copy = models.BooleanField(default=True)
    done_status = models.BooleanField(default=False)
    print_time = models.DateTimeField(null=True)
    reason = models.TextField(default='')


    base_set = 'GHIJKLMNOPQRSTUVWXYZ'
    @property
    def customize_hex_from_id(self):
        base_set = self.einvoice.seller_invoice_track_no.turnkey_web.epl_base_set
        if not base_set:
            base_set = self.base_set
        return customize_hex_from_integer(self.id, base=base_set)


    @classmethod
    def get_objs_from_customize_hex(cls, hex, base_set=''):
        ids = []
        if base_set:
            try:
                id = integer_from_customize_hex(hex, base=base_set)
            except:
                pass
            else:
                ids.append(id)
        else:
            for tw in TurnkeyWeb.objects.all():
                try:
                    id = integer_from_customize_hex(hex, base=tw.epl_base_set)
                except:
                    pass
                else:
                    ids.append(id)
        return EInvoicePrintLog.objects.filter(id__in=ids)


    def __str__(self):
        return "{}:{} print einvoice id({}) with printer({}) at {}".format(
            self.user.first_name, self.user.id,
            self.einvoice.id,
            self.printer.nickname,
            self.print_time
        )



class CancelEInvoice(models.Model):
    einvoice = models.ForeignKey(EInvoice, on_delete=models.DO_NOTHING)
    invoice_date = models.DateField()
    seller_identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    buyer_identifier = models.CharField(max_length=10, null=False, blank=False, db_index=True)
    cancel_date = models.DateField()
    cancel_time = models.DateTimeField()
    readon = models.CharField(max_length=20)
    return_tax_document_number = models.CharField(max_length=60)
    remark = models.CharField(max_length=200)


