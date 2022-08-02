import pytz, datetime, hmac, requests, logging, zlib, json, re
from hashlib import sha256
from base64 import b64encode, b64decode
from binascii import unhexlify 
from Crypto.Cipher import AES
from hashlib import sha1
from random import random, randint, choice
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError
from django.db.models import Max, F, Count, Q
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.fields import GenericRelation
from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext, pgettext
from simple_history.models import HistoricalRecords
from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms

from ho600_ltd_libraries.utils.formats import customize_hex_from_integer, integer_from_customize_hex
from taiwan_einvoice.libs import CounterBasedOTPinRow


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
COULD_PRINT_TIME_MARGIN = datetime.timedelta(minutes=20)
NO_NEED_TO_PRINT_TIME_MARGIN = datetime.timedelta(minutes=10)
MARGIN_TIME_BETWEEN_END_TIME_AND_NOW = datetime.timedelta(minutes=31)



class CancelEInvoiceMIGError(Exception):
    pass



class VoidEInvoiceMIGError(Exception):
    pass



class BatchEInvoiceIDsError(Exception):
    pass



class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    nickname = models.CharField(max_length=255, default='')
    is_active = models.BooleanField(default=True)
    @property
    def in_printer_admin_group(self):
        return self.user.is_superuser or self.user.groups.filter(name="TaiwanEInvoicePrinterAdminGroup").exists()
    @property
    def in_manager_group(self):
        return self.user.is_superuser or self.user.groups.filter(name="TaiwanEInvoiceManagerGroup").exists()
    @property
    def groups(self):
        ct_id = ContentType.objects.get_for_model(TurnkeyService).id
        groups = {}
        for g in Group.objects.filter(name__startswith="ct{ct_id}:".format(ct_id=ct_id)).order_by('name'):
            turnkeyservice_id = g.name.split(':')[1]
            turnkeyservice = TurnkeyService.objects.get(id=turnkeyservice_id)
            g.display_name = ''.join(g.name.split(':')[2:])
            is_member = self.user.groups.filter(id=g.id).exists()
            groups.setdefault(turnkeyservice.name, []).append({"id": g.id,
                                                           "display_name": g.display_name,
                                                           "is_member": is_member})
        return groups
    @property
    def count_within_groups(self):
        count_within_groups = {}
        for k, v in self.groups.items():
            count_within_groups[k] = 0
            for group in v:
                if group['is_member']:
                    if k in count_within_groups:
                        count_within_groups[k] += 1
        return count_within_groups


    def __str__(self):
        return "{}({} {})".format(self.nickname, self.user.username, self.is_active)

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
                                       timeout=(10, 10),
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



class NotEnoughNumberError(Exception):
    pass



class UsedSellerInvoiceTrackNoError(Exception):
    pass



class GenerateTimeNotFollowNoOrderError(Exception):
    pass



class EInvoiceDetailsError(Exception):
    pass



class EInvoiceFieldError(Exception):
    pass



class MobileBarcodeDoesNotExist(Exception):
    pass



class NPOBanDoesNotExist(Exception):
    pass



class NatualPersonBarcodeFormatError(Exception):
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



    class Meta:
        permissions = (
            ("operate_te_escposweb", "Operate ESCPOSWeb"),
            ("edit_te_escposweboperator", "Edit the operators of ESCPOSWeb"),
        )



    @property
    def admins(self):
        try:
            g = Group.objects.get(name='TaiwanEInvoicePrinterAdminGroup')
        except Group.DoesNotExist:
            return StaffProfile.objects.none()
        else:
            return StaffProfile.objects.filter(user__in=g.user_set.all()).order_by('nickname')


    @property
    def operators(self):
        try:
            g = Group.objects.get(name='TaiwanEInvoicePrinterAdminGroup')
        except Group.DoesNotExist:
            admin_users = []
        else:
            admin_users = g.user_set.all()
        users = get_users_with_perms(self, only_with_perms_in=['operate_te_escposweb'])
        return StaffProfile.objects.filter(user__is_superuser=False,
                                           user__in=users
                                          ).exclude(user__in=admin_users).order_by('nickname')


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
    GENERAL_CONSUMER_IDENTIFIER = 10 * '0'
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



class ContentObjectError(Exception):
    pass



class ForbiddenAboveAmountError(Exception):
    pass



class TurnkeyService(models.Model):
    on_working = models.BooleanField(default=True)
    in_production = models.BooleanField(default=False)
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=32, unique=True)
    hash_key = models.CharField(max_length=40)
    transport_id = models.CharField(max_length=10)
    party_id = models.CharField(max_length=10)
    routing_id = models.CharField(max_length=39)
    qrcode_seed = models.CharField(max_length=40)
    turnkey_seed = models.CharField(max_length=40)
    download_seed = models.CharField(max_length=40)
    epl_base_set = models.CharField(max_length=64, default='')
    warning_above_amount = models.IntegerField(default=10000)
    forbidden_above_amount = models.IntegerField(default=20000)
    auto_upload_c0401_einvoice = models.BooleanField(default=False)
    upload_cronjob_format_choices = (
      ("*/5 * * * *", _("once per 5 minutes")),
      ("*/10 * * * *", _("once per 10 minutes")),
      ("*/15 * * * *", _("once per 15 minutes")),
      ("*/20 * * * *", _("once per 20 minutes")),
      ("*/30 * * * *", _("once per 30 minutes")),
      ("*/60 * * * *", _("once per 60 minutes")),
    )
    upload_cronjob_format = models.CharField(max_length=128, default="*/15 * * * *", choices=upload_cronjob_format_choices, db_index=True)
    @property
    def upload_cronjob_format__display(self):
        return self.get_upload_cronjob_format_display()
    tkw_endpoint = models.TextField()
    history = HistoricalRecords()
    @property
    def groups(self):
        ct_id = ContentType.objects.get_for_model(TurnkeyService).id
        return Group.objects.filter(name__startswith="ct{ct_id}:{id}:".format(ct_id=ct_id, id=self.id)).order_by('name')
    @property
    def groups_permissions(self):
        permissions = {}
        for g in self.groups:
            permissions[g.id] = get_perms(g, self)
            for p in g.permissions.all():
                permissions[g.id].append(p.codename)
        return permissions
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
            
        super(TurnkeyService, self).save(*args, **kwargs)


    def generate_counter_based_otp_in_row(self):
        n_times_in_a_row = 3
        key = '{}-{}-{}-{}'.format(self.routing_id, self.hash_key, self.transport_id, self.party_id)
        cbotpr = CounterBasedOTPinRow(SECRET=key.encode('utf-8'), N_TIMES_IN_A_ROW=n_times_in_a_row)
        return cbotpr.generate_otps()



    class Meta:
        unique_together = (('seller', 'name'), )
        permissions = (
            ("edit_te_turnkeyservicegroup", "Edit the groups of the TurnkeyService"),

            ("view_te_sellerinvoicetrackno", "View Seller Invoice Track No of the TurnkeyService"),
            ("add_te_sellerinvoicetrackno", "Add Seller Invoice Track No of the TurnkeyService"),
            ("delete_te_sellerinvoicetrackno", "Delete Seller Invoice Track No of the TurnkeyService"),

            ("view_te_einvoice", "View E-Invoice of the TurnkeyService"),

            ("view_te_canceleinvoice", "View Cancel E-Invoice of the TurnkeyService"),
            ("add_te_canceleinvoice", "Add Cancel E-Invoice of the TurnkeyService"),

            ("view_te_voideinvoice", "View Void E-Invoice of the TurnkeyService"),
            ("add_te_voideinvoice", "Add Void E-Invoice of the TurnkeyService"),

            ("view_te_einvoiceprintlog", "View E-Invoice Print Log of the TurnkeyService"),
            
            ("view_te_summaryreport", "View Summary Report of the TurnkeyService"),
            ("resolve_te_summaryreport", "Resolve Summary Report of the TurnkeyService"),

            ("view_te_alarm_for_general_user", "View Alarm for the General User of the TurnkeyService"),
            ("view_te_alarm_for_programmer", "View Alarm for the Programmer of the TurnkeyService"),
        )
    


class SellerInvoiceTrackNo(models.Model):
    turnkey_web = models.ForeignKey(TurnkeyService, on_delete=models.DO_NOTHING)
    type_choices = (
        ('07', _('General')),
        ('08', _('Special')),
    )
    type = models.CharField(max_length=2, default='07', choices=type_choices, db_index=True)
    @property
    def type__display(self):
        return self.get_type_display()
    begin_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    @property
    def year_month_range(self):
        chmk_year = self.begin_time.astimezone(TAIPEI_TIMEZONE).year - 1911
        begin_month = self.begin_time.astimezone(TAIPEI_TIMEZONE).month
        end_month = (self.end_time.astimezone(TAIPEI_TIMEZONE) - datetime.timedelta(seconds=1)).month
        return "{}年{}-{}月".format(chmk_year, begin_month, end_month)
    track = models.CharField(max_length=2, db_index=True)
    begin_no = models.IntegerField(db_index=True)
    end_no = models.IntegerField(db_index=True)



    class Meta:
        unique_together = (("type", "begin_time", "end_time", "track", "begin_no", "end_no"), )



    def __str__(self):
        return "{}{}({}~{}: {}{:08d}-{:08d})".format(self.turnkey_web,
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
        for sitn in queryset.filter(turnkey_web__on_working=True,
                                    begin_time__lte=_now,
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
    

    @property
    def can_be_deleted(self):
        return not self.einvoice_set.exists()
    

    def delete(self, *args, **kwargs):
        if self.einvoice_set.exists():
            ei = self.einvoice_set.order_by('id').first()
            raise UsedSellerInvoiceTrackNoError(_("It could not be deleted, because it had E-Invoice({})"), ei.track_no_)
        return super().delete(*args, **kwargs)


    def get_new_no(self):
        max_no = self.einvoice_set.filter(no__gte=self.begin_no, no__lte=self.end_no).aggregate(Max('no'))['no__max']
        if max_no:
            max_no = int(max_no)

        if not max_no:
            new_no = self.begin_no
        elif max_no >= self.end_no:
            raise NotEnoughNumberError(_('Not enough numbers'))
        else:
            new_no = max_no + 1
        new_no = '{:08d}'.format(new_no)
        return new_no


    def create_einvoice(self, data):
        data['seller_invoice_track_no'] = self
        data['type'] = self.type
        data['track'] = self.track
        data['no'] = self.get_new_no()
        ei = EInvoice(**data)
        try:
            ei.save()
        except IntegrityError:
            raise GenerateTimeNotFollowNoOrderError("Duplicated no: {}".format(data['no']))
        except EInvoiceDetailsError as e:
            raise e
        return ei






class EInvoiceMIG(models.Model):
    no_choices = (
        ('A0101', _('B2B Exchange Invoice')),
        ('A0102', _('B2B Exchange Invoice Confirm')),
        ('B0101', _('B2B Exchange Allowance')),
        ('B0102', _('B2B Exchange Allowance Confirm')),
        ('A0201', _('B2B Exchange Cancel Invoice')),
        ('A0202', _('B2B Exchange Cancel Invoice Confirm')),
        ('B0201', _('B2B Exchange Cancel Allowance')),
        ('B0202', _('B2B Exchange Cancel Allowance Confirm')),
        ('A0301', _('B2B Exchange Reject Invoice')),
        ('A0302', _('B2B Exchange Reject Invoice Confirm')),

        ('A0401', _('B2B Certificate Invoice')),
        ('B0401', _('B2B Certificate Allowance')),
        ('A0501', _('B2B Certificate Cancel Invoice')),
        ('B0501', _('B2B Certificate Cancel Allowance')),
        ('A0601', _('B2B Certificate Reject Invoice')),

        ('C0401', _('B2C Certificate Invoice')),
        ('C0501', _('B2C Certificate Cancel Invoice')),
        ('C0701', _('B2C Certificate Void Invoice')),
        ('D0401', _('B2C Certificate Allowance')),
        ('D0501', _('B2C Certificate Cancel Allowance')),

        ('E0401', _('Branch Track')),
        ('E0402', _('Branch Track Blank')),
        ('E0501', _('Invoice Assign No')),
    )
    no = models.CharField(max_length=5, choices=no_choices, unique=True)


    def __str__(self):
        return self.no



class EInvoice(models.Model):
    only_fields_can_update = ['print_mark', 'ei_synced', 'generate_time']
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ei_synced = models.BooleanField(default=False, db_index=True)
    mig_type = models.ForeignKey(EInvoiceMIG, null=False, on_delete=models.DO_NOTHING)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    seller_invoice_track_no = models.ForeignKey(SellerInvoiceTrackNo, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=2, default='07', choices=SellerInvoiceTrackNo.type_choices, db_index=True)
    track = models.CharField(max_length=2, db_index=True)
    no = models.CharField(max_length=8, db_index=True)
    @property
    def track_no(self):
        return "{}{}".format(self.track, self.no)
    @property
    def track_no_(self):
        return "{}-{}".format(self.track, self.no)
    reverse_void_order = models.SmallIntegerField(default=0) #INFO: only E-Invoice with reverse_void_order=0 is the normal E-Invoice, others are the voided E-Invoice
    carrier_type_choices = (
        ('3J0002', _('Mobile barcode')),
        ('CQ0001', _('Natural person barcode')),
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
    @property
    def invoice_date(self):
        return self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y%m%d')
    @property
    def invoice_time(self):
        return self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%H:%M:%S')
    generate_no = models.CharField(max_length=40, default='', db_index=True)
    generate_no_sha1 = models.CharField(max_length=10, default='', db_index=True)
    batch_id = models.SmallIntegerField(default=0)

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
    @property
    def amount_is_warning(self):
        if float(self.amounts['TotalAmount']) > self.seller_invoice_track_no.turnkey_web.warning_above_amount:
            return True
        else:
            return False
    @property
    def buyer_is_business_entity(self):
        if not self.buyer or not self.buyer_identifier:
            raise Exception("No Buyer")
        if LegalEntity.GENERAL_CONSUMER_IDENTIFIER == self.buyer_identifier:
            return False
        else:
            return True
    @property
    def is_canceled(self):
        return self.canceleinvoice_set.exists()
    @property
    def canceled_time(self):
        if self.is_canceled:
            cei = self.canceleinvoice_set.get()
            return cei.generate_time
        else:
            return None
    @property
    def can_cancel(self):
        if self.is_canceled:
            return False
        elif self.is_voided and self.voideinvoice_set.filter(new_einvoice__isnull=False).exists():
            return False
        else:
            return True
    @property
    def is_voided(self):
        return self.voideinvoice_set.exists()
    @property
    def voided_time(self):
        if self.is_voided:
            vei = self.voideinvoice_set.get()
            return vei.generate_time
        else:
            return None
    @property
    def can_void(self):
        if self.is_voided:
            return False
        elif self.is_canceled and self.canceleinvoice_set.filter(new_einvoice__isnull=False).exists():
            return False
        elif self.is_canceled:
            #INFO: Logically, a normal flow can be C0401 > C0501 > C0701 > C0401
            #But in the general case, an E-Invoice state is from C0401 to C0501 and has no new C0401 means "Return Order"
            #So the "E-Invoice depends on the return order" does not need another C0701
            return False
        else:
            return True
    @property
    def related_einvoices(self):
        #TODO: how put "voided-einvoice" in here?
        einvoice = self
        related_einvoices = []
        while True:
            related_einvoice = einvoice.canceleinvoice_set.filter(new_einvoice__isnull=False)
            if related_einvoice:
                canceled_einvoice = related_einvoice.get()
                related_einvoices.append(canceled_einvoice.new_einvoice)
                einvoice = canceled_einvoice.new_einvoice
            else:
                break
        return related_einvoices
    @property
    def last_batch_einvoice(self):
        try:
            bei = BatchEInvoice.objects.get(content_type=ContentType.objects.get_for_model(self),
                                            object_id=self.id)
        except BatchEInvoice.DoesNotExist:
            return None
        else:
            return bei


    def __str__(self):
        return "{}@{}".format(self.track_no, self.get_mig_no())



    class Meta:
        unique_together = (('seller_invoice_track_no', 'track', 'no', 'reverse_void_order'), )
    

    @property
    def one_dimension_barcode_str(self):
        chmk_year = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).year - 1911
        begin_month = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).month
        end_month = begin_month + 1
        barcode_str = "{:03d}{:02d}{}{}".format(
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
        print_original_copy = False
        if self.is_canceled:
            cancel_einvoice = self.canceleinvoice_set.get()
            cancel_note = pgettext("canceleinvoice", "Canceled at {} {}").format(cancel_einvoice.cancel_date, cancel_einvoice.cancel_time)
            cancel_reason = pgettext("canceleinvoice", "Reason: {}").format(cancel_einvoice.reason)
            res = [
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "作  廢  說  明"},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "barcode", "align_ct": True, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": self.one_dimension_barcode_str},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": cancel_note},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": cancel_reason},
            ]
            if cancel_einvoice.return_tax_document_number:
                message1 = pgettext("canceleinvoice", "Return tax document number: {}").format(cancel_einvoice.return_tax_document_number)
                res += [
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": message1},
                ]
            if cancel_einvoice.remark:
                message2 = pgettext("canceleinvoice", "Remark: {}").format(cancel_einvoice.remark)
                res += [
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": message2},
                ]
            return res
        elif self.is_voided:
            void_einvoice = self.voideinvoice_set.get()
            void_note = pgettext("voideinvoice", "voided at {} {}").format(void_einvoice.void_date, void_einvoice.void_time)
            void_reason = pgettext("voideinvoice", "Reason: {}").format(void_einvoice.reason)
            res = [
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "註  銷  說  明"},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "barcode", "align_ct": True, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": self.one_dimension_barcode_str},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": void_note},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": void_reason},
            ]
            if void_einvoice.remark:
                message2 = pgettext("voideinvoice", "Remark: {}").format(void_einvoice.remark)
                res += [
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": message2},
                ]
            return res
        elif "3J0002" == self.carrier_type and LegalEntity.GENERAL_CONSUMER_IDENTIFIER != self.buyer_identifier:
            print_original_copy = True
        elif '' != self.carrier_type:
            carrier_id1 = self.carrier_id1
            if carrier_id1 == self.carrier_id2:
                carrier_id2 = ''
            message = _("Carrier Type: {carrier_type} {carrier_id1} {carrier_id2}").format(
                carrier_type=self.get_carrier_type_display(),
                carrier_id1=carrier_id1, carrier_id2=carrier_id2,
            )
            _result = [
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "列  印  說  明"},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "barcode", "align_ct": True, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": self.one_dimension_barcode_str},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": message},
            ]
            if '' != self.npoban:
                message = _("Donate to NPO( {npoban} )").format(npoban=self.npoban)
                _result += [{"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": message}]
            elif LegalEntity.GENERAL_CONSUMER_IDENTIFIER != self.buyer_identifier:
                _result += [{"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "買方 "+self.buyer_identifier}]
            return _result
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
            print_original_copy = True
        
        if print_original_copy:
            details = self.details
            amounts = self.amounts
            chmk_year = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).year - 1911
            begin_month = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).month
            end_month = begin_month + 1
            generate_time = self.generate_time.astimezone(TAIPEI_TIMEZONE)
            sales_amount_str = _hex_amount(amounts['SalesAmount'])
            total_amount_str = _hex_amount(amounts['TotalAmount'])
            if self.seller_invoice_track_no.turnkey_web.in_production:
                test_str = ''
            else:
                test_str = '測 試 '
            return [
                    {"type": "text", "custom_size": True, "width": 1, "height": 2, "align": "center", "text": test_str + "電 子 發 票 證 明 聯"},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                    {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": " {}".format(generate_time.strftime('%Y-%m-%d %H:%M:%S'))},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": " 隨機碼 {} 總計 {}".format(self.random_number, amounts['TotalAmount'])},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left",
                        "text": " 賣方 {} {}".format(self.seller_identifier,
                                                        "" if LegalEntity.GENERAL_CONSUMER_IDENTIFIER == self.buyer_identifier else "買方 "+self.buyer_identifier)},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "barcode", "align_ct": True, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": self.one_dimension_barcode_str},
                    {"type": "qrcode_pair", "center": False,
                        "qr1_str": "{track_no}{year_m_d}{random_number}{sales_amount}{total_amount}{buyer_identifier}{seller_identifier}{qrcode_aes_encrypt_str}:{generate_no_sha1}:{product_in_einvoice_count}:{product_in_order_count}:{codepage}:".format(
                            track_no=self.track_no,
                            year_m_d="{}{}".format(chmk_year, generate_time.strftime('%m%d')),
                            random_number=self.random_number,
                            sales_amount=sales_amount_str,
                            total_amount=total_amount_str,
                            buyer_identifier=(LegalEntity.GENERAL_CONSUMER_IDENTIFIER if LegalEntity.GENERAL_CONSUMER_IDENTIFIER == self.buyer_identifier else self.buyer_identifier)[:8],
                            seller_identifier=self.seller_identifier,
                            generate_no_sha1=self.generate_no_sha1,
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
            "is_canceled": self.is_canceled,
            "buyer_is_business_entity": self.buyer_is_business_entity,
            "print_mark": self.print_mark,
            "id": self.id,
            "track_no": self.track_no,
            "generate_time": self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S%z'),
            "width": "58mm",
            "content": EInvoice.escpos_einvoice_scripts(self.id),
        }
        _d["details_content"] = self.details_content
        return _d


    def get_mig_no(self):
        return self.mig_type.no


    def export_json_for_mig(self):
        er_field_d = {
            "identifier": "Identifier",
            "name": "Name",
            "address": "Address",
            "person_in_charge": "PersonInCharge",
            "telephone_number": "TelephoneNumber",
            "facsimile_number": "FacsimileNumber",
            "email_address": "EmailAddress",
            "customer_number": "CustomerNumber",
            "role_remark": "RoleRemark"
        }
        er_j = {"seller": {}, "buyer": {}}
        for er in ["seller", "buyer"]:
            for k, json_k in er_field_d.items():
                v = getattr(self, "{}_{}".format(er, k))
                if v:
                    er_j[er][json_k] = v
        J = {self.get_mig_no(): {
                "Main": {
                    "InvoiceNumber": self.track_no,
                    "InvoiceDate": self.invoice_date,
                    "InvoiceTime": self.invoice_time,
                    "Seller": er_j["seller"],
                    "Buyer": er_j["buyer"],
                    "InvoiceType": self.seller_invoice_track_no.type,
                    "DonateMark": self.donate_mark,
                    "PrintMark": 'Y' if self.print_mark else 'N',
                    "RandomNumber": self.random_number,
                },
                "Details": self.details,
                "Amount": self.amounts,
            }
        }
        no = self.get_mig_no()
        if '1' == J[no]["Main"]["DonateMark"]:
            J[no]["Main"]["NPOBAN"] = self.npoban
        if self.carrier_type:
            J[no]["Main"]["CarrierType"] = self.carrier_type
            J[no]["Main"]["CarrierId1"] = self.carrier_id1
            J[no]["Main"]["CarrierId2"] = self.carrier_id2
        return J


    def check_before_cancel_einvoice(self):
        return self.content_object.check_before_cancel_einvoice()


    def set_generate_time(self, generate_time):
        if 'generate_time' in self.only_fields_can_update:
            EInvoice.objects.filter(id=self.id).update(generate_time=generate_time)


    def set_ei_synced_true(self):
        if 'ei_synced' in self.only_fields_can_update:
            EInvoice.objects.filter(id=self.id).update(ei_synced=True)


    def set_print_mark_true(self, einvoice_print_log=None):
        if self.is_canceled:
            return False
        elif self.is_voided:
            return False
        elif "3J0002" == self.carrier_type and LegalEntity.GENERAL_CONSUMER_IDENTIFIER != self.buyer_identifier:
            pass
        elif '' != self.carrier_type:
            return False
        elif '' != self.npoban:
            return False

        if 'print_mark' in self.only_fields_can_update:
            if True == self.print_mark:
                #TODO: CMEC2-324
                # It is "duplicated original copy"
                # raise or just log this error?
                # Now, I prefer "log", because raise error in websocket does not help user.
                pass
            elif False == self.print_mark:
                EInvoice.objects.filter(id=self.id).update(print_mark=True)
    

    def increase_reverse_void_order(self):
        EInvoice.objects.filter(id=self.id).update(reverse_void_order=F('reverse_void_order')+1)


    def delete(self, *args, **kwargs):
        raise Exception('Can not delete')


    def save(self, *args, **kwargs):
        if not self.content_object:
            raise ContentObjectError(_("Content object is not existed"))
        elif not hasattr(self.content_object, 'check_before_cancel_einvoice'):
            raise ContentObjectError(_("Content Object: {} has no 'check_before_cancel_einvoice' method").format(self.content_object))
        elif not hasattr(self.content_object, 'post_cancel_einvoice'):
            raise ContentObjectError(_("Content Object: {} has no 'post_cancel_einvoice' method").format(self.content_object))
        elif 999 <= len(self.details):
            raise EInvoiceDetailsError(_("Max records in details is 999"))
        elif kwargs.get('force_save', False):
            del kwargs['force_save']
            super().save(*args, **kwargs)
        elif not self.pk:
            turnkey_web = self.seller_invoice_track_no.turnkey_web
            if float(self.amounts['TotalAmount']) > turnkey_web.forbidden_above_amount:
                raise ForbiddenAboveAmountError(_("{total_amount} is bigger than Forbidden Amount({forbidden_above_amount})").format(
                    total_amount=self.amounts['TotalAmount'], forbidden_above_amount=turnkey_web.forbidden_above_amount))
            elif float(self.amounts['TotalAmount']) > turnkey_web.warning_above_amount:
                #TODO: grab staff group, and send notice mail to them.
                pass

            while True:
                random_number = '{:04d}'.format(randint(0, 10000))
                objs = self._meta.model.objects.filter(seller_invoice_track_no__turnkey_web=turnkey_web).order_by('-id')[:1000]
                if not objs.exists():
                    break
                else:
                    obj = objs[len(objs)-1]
                    if not (self._meta.model.objects.filter(id__gte=obj.id,
                                                            seller_invoice_track_no__turnkey_web=turnkey_web,
                                                            random_number=random_number).exists()
                            or self._meta.model.objects.filter(reverse_void_order__gt=0,
                                                               seller_invoice_track_no__turnkey_web=turnkey_web,
                                                               track=self.track,
                                                               no=self.no,
                                                               random_number=random_number,
                                                               ).exists()):
                        break
            self.random_number = random_number
            self.generate_no_sha1 = sha1(self.generate_no.encode('utf-8')).hexdigest()[:10]
            super().save(*args, **kwargs)
        UploadBatch.append_to_the_upload_batch(self)
        


class EInvoicePrintLog(models.Model):
    user = models.ForeignKey(User, default=102, on_delete=models.DO_NOTHING)
    printer = models.ForeignKey(Printer, on_delete=models.DO_NOTHING)
    einvoice = models.ForeignKey(EInvoice, on_delete=models.DO_NOTHING)
    is_original_copy = models.BooleanField(default=True, db_index=True)
    done_status = models.BooleanField(default=False, db_index=True)
    print_time = models.DateTimeField(null=True, db_index=True)
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
            for tw in TurnkeyService.objects.all():
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
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ei_synced = models.BooleanField(default=False, db_index=True)
    mig_type = models.ForeignKey(EInvoiceMIG, null=False, on_delete=models.DO_NOTHING)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    einvoice = models.ForeignKey(EInvoice, on_delete=models.DO_NOTHING)
    @property
    def invoice_date(self):
        return self.einvoice.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y%m%d')
    @property
    def track_no(self):
        return self.einvoice.track_no
    seller_identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    buyer_identifier = models.CharField(max_length=10, null=False, blank=False, db_index=True)
    generate_time = models.DateTimeField(db_index=True)
    @property
    def cancel_date(self):
        return self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y%m%d')
    @property
    def cancel_time(self):
        return self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%H:%M:%S')
    reason = models.CharField(max_length=20, null=False, db_index=True)
    return_tax_document_number = models.CharField(max_length=60, default='', null=True, blank=True, db_index=True)
    remark = models.CharField(max_length=200, default='', null=True, blank=True)
    new_einvoice = models.ForeignKey(EInvoice,
        related_name="new_einvoice_on_cancel_einvoice_set",
        null=True,
        on_delete=models.DO_NOTHING)
    @property
    def last_batch_einvoice(self):
        try:
            bei = BatchEInvoice.objects.get(content_type=ContentType.objects.get_for_model(self),
                                            object_id=self.id)
        except BatchEInvoice.DoesNotExist:
            return None
        else:
            return bei


    def __str__(self):
        return "{}@{}".format(self.einvoice.track_no, self.get_mig_no())


    def set_ei_synced_true(self):
        CancelEInvoice.objects.filter(id=self.id).update(ei_synced=True)


    def set_new_einvoice(self, new_einvoice):
        if not self.new_einvoice:
            CancelEInvoice.objects.filter(id=self.id).update(new_einvoice=new_einvoice)
            self.new_einvoice = new_einvoice


    def post_cancel_einvoice(self):
        lg = logging.getLogger('taiwan_einvoice')
        lg.debug('CancelEInvoice(id:{}) post_cancel_einvoice'.format(self.id))
        message = ""
        if self.new_einvoice:
            message = self.einvoice.content_object.post_cancel_einvoice(self.new_einvoice)
        return message


    def save(self, *args, **kwargs):
        if not self.mig_type:
            self.mig_type = EInvoiceMIG.objects.get(no=self.get_mig_no())

        if kwargs.get('force_save', False):
            del kwargs['force_save']
            super().save(*args, **kwargs)
        elif not self.pk:
            super().save(*args, **kwargs)
        UploadBatch.append_to_the_upload_batch(self)


    def get_mig_no(self):
        no = self.einvoice.get_mig_no()
        if "C0401" == no:
            mig = "C0501"
        else:
            raise CancelEInvoiceMIGError("MIG for {} is not set".format(no))
        return mig


    def export_json_for_mig(self):
        mig = self.get_mig_no()
        J = {mig: {
            "CancelInvoiceNumber": self.einvoice.track_no,
            "InvoiceDate": self.einvoice.invoice_date,
            "BuyerId": self.buyer_identifier,
            "SellerId": self.seller_identifier,
            "CancelDate": self.cancel_date,
            "CancelTime": self.cancel_time,
            "CancelReason": self.reason,
            }}
        if self.return_tax_document_number:
            J[mig]['ReturnTaxDocumentNumber'] = self.return_tax_document_number
        if self.remark:
            J[mig]['Remark'] = self.remark
        return J



class VoidEInvoice(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ei_synced = models.BooleanField(default=False, db_index=True)
    mig_type = models.ForeignKey(EInvoiceMIG, null=False, on_delete=models.DO_NOTHING)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    einvoice = models.ForeignKey(EInvoice, on_delete=models.DO_NOTHING)
    @property
    def invoice_date(self):
        return self.einvoice.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y%m%d')
    @property
    def track_no(self):
        return self.einvoice.track_no
    seller_identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    buyer_identifier = models.CharField(max_length=10, null=False, blank=False, db_index=True)
    generate_time = models.DateTimeField(db_index=True)
    @property
    def void_date(self):
        return self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y%m%d')
    @property
    def void_time(self):
        return self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%H:%M:%S')
    reason = models.CharField(max_length=20, null=False, db_index=True)
    remark = models.CharField(max_length=200, default='', null=True, blank=True)
    new_einvoice = models.ForeignKey(EInvoice, related_name="new_einvoice_on_void_einvoice_set", null=True, on_delete=models.DO_NOTHING)
    @property
    def last_batch_einvoice(self):
        return BatchEInvoice.objects.filter(content_type=ContentType.objects.get_for_model(self),
                                            object_id=self.id).order_by('id').last()


    def __str__(self):
        return "{}@{}".format(self.einvoice.track_no, self.get_mig_no())


    def set_ei_synced_true(self):
        VoidEInvoice.objects.filter(id=self.id).update(ei_synced=True)


    def set_new_einvoice(self, new_einvoice):
        if not self.new_einvoice:
            VoidEInvoice.objects.filter(id=self.id).update(new_einvoice=new_einvoice)
            self.new_einvoice = new_einvoice


    def post_void_einvoice(self):
        lg = logging.getLogger('taiwan_einvoice')
        lg.debug('VoidEInvoice(id:{}) post_void_einvoice'.format(self.id))
        message = self.einvoice.content_object.post_void_einvoice(self.new_einvoice)
        return message


    def save(self, *args, **kwargs):
        if not self.mig_type:
            self.mig_type = EInvoiceMIG.objects.get(no=self.get_mig_no())

        if kwargs.get('force_save', False):
            del kwargs['force_save']
            super().save(*args, **kwargs)
        elif not self.pk:
            super().save(*args, **kwargs)
        UploadBatch.append_to_the_upload_batch(self)
    
    
    def get_mig_no(self):
        no = self.einvoice.get_mig_no()
        if "C0401" == no:
            mig = "C0701"
        else:
            raise VoidEInvoiceMIGError("MIG for {} is not set".format(no))
        return mig


    def export_json_for_mig(self):
        mig = self.get_mig_no()
        J = {mig: {
            "VoidInvoiceNumber": self.einvoice.track_no,
            "InvoiceDate": self.einvoice.invoice_date,
            "BuyerId": self.buyer_identifier,
            "SellerId": self.seller_identifier,
            "VoidDate": self.void_date,
            "VoidTime": self.void_time,
            "VoidReason": self.reason,
            }}
        if self.remark:
            J[mig]['Remark'] = self.remark
        return J



EITurnkeyBatchEndpoint_SUB_RE = re.compile("/EITurnkey/[0-9]+/")

class UploadBatch(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True, db_index=True)
    turnkey_service = models.ForeignKey(TurnkeyService, on_delete=models.DO_NOTHING)
    slug = models.CharField(max_length=14, unique=True)
    mig_type = models.ForeignKey(EInvoiceMIG, on_delete=models.DO_NOTHING)
    kind_choices = (
        ("wp", _("Wait for printed")),          # to EInvoice
        ("cp", _("Could print")),               # to EInvoice
        ("np", _("No need to print")),          # to EInvoice
        ("57", _("Wait for C0501 or C0701")),   # to EInvoice

        ("w4", _("Wait for C0401")),            # to CancelEInvoice or VoidEInvoice
        ("54", _("Wait for C0501 or C0401")),   # to VoidEInvoice
    )
    kind = models.CharField(max_length=2, choices=kind_choices)
    executor = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)
    status_choices = (
        ("0", _("Collecting")),
        ("1", _("Waiting for trigger(Stop Collecting)")),
        ("2", _("Noticed to TKW")),
        ("3", _("Exporting E-Invoice JSON")),
        ("4", _("Uploaded to TKW")),
        ("f", _("Finish")),
    )
    status = models.CharField(max_length=1, default='0', choices=status_choices, db_index=True)
    ei_turnkey_batch_id = models.PositiveBigIntegerField(default=0)
    @property
    def batch_einvoice_count(self):
        return self.batcheinvoice_set.count()
    history = HistoricalRecords()


    def __str__(self):
        return "{}-{}@{}".format(self.slug, self.mig_type, self.kind)


    def get_mig_no(self):
        return self.mig_type.no


    @classmethod
    def status_check(cls, statuss=[]):
        ubs = []
        for ub in cls.objects.exclude(status__in=['c', 'm']).filter(status__in=statuss).order_by('id'):
            while True:
                function_name = 'check_in_{}_status_then_update_to_the_next'.format(ub.status)
                pair = [ub, function_name, ub.status]
                if hasattr(ub, function_name):
                    getattr(*pair[:2])()
                    pair.append(ub.status)
                    ubs.append(pair)
                if 3 == len(pair) or pair[2] == pair[3]:
                    break
        return ubs


    def update_to_new_status(self, new_status):
        status_list = [_i[0] for _i in self.status_choices]
        if new_status and 1 == status_list.index(new_status) - status_list.index(self.status):
            self.status = new_status
            self.save()
        else:
            raise Exception('Wrong status flow: {}=>{}'.format(self.status, new_status))


    def check_in_4_status_then_update_to_the_next(self, NEXT_STATUS='f'):
        if '4' != self.status: return

        audit_type = AuditType.objects.get(name="EI_PROCESSING")
        audit_log = AuditLog(
            creator=User.objects.get(username="^taiwan_einvoice_sys_user$"),
            type=audit_type,
            turnkey_service=self.turnkey_service,
            content_object=self,
            is_error=False,
        )
        url = (EITurnkeyBatchEndpoint_SUB_RE.sub("/EITurnkeyBatch/{}/".format(self.ei_turnkey_batch_id),
                                                self.turnkey_service.tkw_endpoint)
                + '{action}/'.format(action="get_batch_einvoice_id_status_result_code_set_from_ei_turnkey_batch_einvoices")
        )
        counter_based_otp_in_row = ','.join(self.turnkey_service.generate_counter_based_otp_in_row())
        payload = {"format": "json"}
        try:
            response = requests.get(url,
                                    params=payload,
                                    headers={"X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row})
        except Exception as e:
            audit_log.is_error = True
            audit_log.log = {
                "function": "UploadBatch.check_in_4_status_then_update_to_the_next",
                "url": url,
                "position at": "requests.get(...)",
                "params": payload,
                "X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row,
                "exception": str(e)
            }
            audit_log.save()
        else:
            result_json = response.json()
            audit_log.log = result_json
            if 200 == response.status_code and "0" == result_json['return_code']:
                is_finish = self.update_batch_einvoice_status_result_code(
                   status=result_json['status'],
                   result_code=result_json['result_code'],
                )
                if is_finish:
                    self.update_to_new_status(NEXT_STATUS)
                    audit_type = AuditType.objects.get(name="EI_PROCESSED")
                    audit_log.type = audit_type
                audit_log.is_error = False
                audit_log.save()
            else:
                audit_log.is_error = True
                audit_log.save()


    def check_in_3_status_then_update_to_the_next(self, NEXT_STATUS='4'):
        if '3' != self.status: return

        audit_type = AuditType.objects.get(name="UPLOAD_TO_EITURNKEY")
        audit_log = AuditLog(
            creator=User.objects.get(username="^taiwan_einvoice_sys_user$"),
            type=audit_type,
            turnkey_service=self.turnkey_service,
            content_object=self,
            is_error=False,
        )

        bodys = [(bei.id,
                  bei.begin_time.strftime("%Y-%m-%d %H:%M:%S%z"),
                  bei.end_time.strftime("%Y-%m-%d %H:%M:%S%z"),
                  bei.track_no,
                  bei.body) for bei in self.batcheinvoice_set.order_by('object_id')]
        gz_bodys = zlib.compress(json.dumps(bodys).encode('utf-8'))
        url = self.turnkey_service.tkw_endpoint + '{action}/'.format(action="upload_eiturnkey_batch_einvoice_bodys")
        counter_based_otp_in_row = ','.join(self.turnkey_service.generate_counter_based_otp_in_row())
        payload = {"format": "json"}
        data = {"slug": self.slug}
        files = {"gz_bodys": gz_bodys}
        try:
            response = requests.post(url,
                                     params=payload,
                                     data=data,
                                     files=files,
                                     headers={"X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row})
        except Exception as e:
            audit_log.is_error = True
            audit_log.log = {
                "function": "UploadBatch.check_in_3_status_then_update_to_the_next",
                "url": url,
                "position at": "requests.post(...)",
                "params": payload,
                "data": data,
                "X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row,
                "exception": str(e)
            }
            audit_log.save()
        else:
            audit_type = AuditType.objects.get(name="UPLOAD_TO_EITURNKEY")
            audit_log.type = audit_type
            result_json = response.json()
            audit_log.log = result_json
            if 200 == response.status_code and "0" == result_json['return_code']:
                audit_log.is_error = False
                audit_log.save()
                self.update_to_new_status(NEXT_STATUS)
            else:
                audit_log.is_error = True
                audit_log.save()


    def check_in_2_status_then_update_to_the_next(self, NEXT_STATUS='3'):
        if '2' != self.status: return

        audit_type = AuditType.objects.get(name="TEA_CEC_PROCESSING")
        audit_log = AuditLog(
            creator=User.objects.get(username="^taiwan_einvoice_sys_user$"),
            type=audit_type,
            turnkey_service=self.turnkey_service,
            content_object=self,
            is_error=False,
        )

        bei_saved = []
        for bei in self.batcheinvoice_set.filter(body='').order_by('object_id'):
            bei.body = bei.content_object.export_json_for_mig()
            try:
                bei.save()
            except:
                audit_log.is_error = True
                audit_log.log = {
                    "function": "UploadBatch.check_in_2_status_then_update_to_the_next",
                    "position at": "bei.save()",
                    "problem bei": str(bei),
                    "exception": str(e)
                }
                audit_log.save()
                return
            else:
                bei_saved.append(str(bei))
        audit_log.log = {
            "saved_count": len(bei_saved),
            "objects": bei_saved,
        }
        audit_log.save()
        self.update_to_new_status(NEXT_STATUS)


    def check_in_1_status_then_update_to_the_next(self, NEXT_STATUS='2'):
        if '1' != self.status: return

        audit_type = AuditType.objects.get(name="TEA_CEC_PROCESSING")
        audit_log = AuditLog(
            creator=User.objects.get(username="^taiwan_einvoice_sys_user$"),
            type=audit_type,
            turnkey_service=self.turnkey_service,
            content_object=self,
            is_error=False,
        )
        url = self.turnkey_service.tkw_endpoint + '{action}/'.format(action="create_eiturnkey_batch")
        counter_based_otp_in_row = ','.join(self.turnkey_service.generate_counter_based_otp_in_row())
        payload = {"format": "json"}
        data = {
            "slug": self.slug,
            "mig": self.get_mig_no(),
        }
        try:
            response = requests.post(url,
                                     params=payload,
                                     data=data,
                                     headers={"X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row})
        except Exception as e:
            audit_log.is_error = True
            audit_log.log = {
                "function": "UploadBatch.check_in_1_status_then_update_to_the_next",
                "url": url,
                "position at": "requests.post(...)",
                "params": payload,
                "data": data,
                "X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row,
                "exception": str(e)
            }
            audit_log.save()
        else:
            audit_type = AuditType.objects.get(name="UPLOAD_TO_EITURNKEY")
            audit_log.type = audit_type
            result_json = response.json()
            audit_log.log = result_json
            if 200 == response.status_code and "0" == result_json['return_code']:
                audit_log.is_error = False
                audit_log.save()
                self.update_to_new_status(NEXT_STATUS)
            else:
                audit_log.is_error = True
                audit_log.save()

            if 'ei_turnkey_batch_id' in result_json and result_json['ei_turnkey_batch_id']:
                self.ei_turnkey_batch_id = result_json['ei_turnkey_batch_id']
                self.save()


    def check_in_0_status_then_update_to_the_next(self, NEXT_STATUS='1'):
        if '0' != self.status: return

        if self.kind in ['wp', 'cp', 'np']:
            object_ids = self.batcheinvoice_set.all().values('object_id')
            ids = [_i['object_id'] for _i in object_ids]
            eis = EInvoice.objects.filter(id__in=ids)
            if len(object_ids) != eis.count():
                raise Exception('Some E-Invoices disappear')
        else:
            content_object = self.batcheinvoice_set.get().content_object
        if 'wp' == self.kind and not eis.filter(print_mark=False).exists():
            self.update_to_new_status(NEXT_STATUS)
        elif ('cp' == self.kind
            and (not eis.filter(print_mark=False).exists()
                or not eis.filter(generate_time__gte=now() - COULD_PRINT_TIME_MARGIN).exists())
            ):
            self.update_to_new_status(NEXT_STATUS)
        elif ('np' == self.kind
            and not eis.filter(generate_time__gte=now() - NO_NEED_TO_PRINT_TIME_MARGIN).exists()):
            self.update_to_new_status(NEXT_STATUS)
        elif '57' == self.kind:
            check_C0501 = False
            check_C0701 = False
            if (not content_object.new_einvoice_on_cancel_einvoice_set.exists()
                or content_object.new_einvoice_on_cancel_einvoice_set.get().ei_synced):
                check_C0501 = True

            if (not content_object.new_einvoice_on_void_einvoice_set.exists()
                or content_object.new_einvoice_on_void_einvoice_set.get().ei_synced):
                check_C0701 = True
            
            if check_C0501 and check_C0701:
                self.update_to_new_status(NEXT_STATUS)
        elif 'w4' == self.kind and content_object.einvoice.ei_synced:
            self.update_to_new_status(NEXT_STATUS)
        elif '54' == self.kind:
            check_C0401 = False
            check_C0501 = False
            if content_object.einvoice.ei_synced:
                check_C0401 = True
            
            if (not content_object.einvoice.canceleinvoice_set.exists()
                or content_object.einvoice.canceleinvoice_set.get().ei_synced):
                check_C0501 = True
            
            if check_C0401 and check_C0501:
                self.update_to_new_status(NEXT_STATUS)


    @classmethod
    def append_to_the_upload_batch(cls, content_object):
        ct = ContentType.objects.get_for_model(content_object)
        if content_object.ei_synced:
            return BatchEInvoice.objects.get(content_type=ct, object_id=content_object.id, status='c').batch
        elif BatchEInvoice.objects.filter(content_type=ct, object_id=content_object.id, result_code='').exists():
            return BatchEInvoice.objects.get(content_type=ct, object_id=content_object.id, result_code='').batch

        if 'einvoice' == content_object._meta.model_name:
            mig_type = EInvoiceMIG.objects.get(no='C0401')
            _now = now().astimezone(TAIPEI_TIMEZONE)
            _s = _now.strftime('%Y-%m-%d 00:00:00+08:00')
            start_time = datetime.datetime.strptime(_s, '%Y-%m-%d %H:%M:%S%z')
            end_time = start_time + datetime.timedelta(days=1)
            if content_object.new_einvoice_on_cancel_einvoice_set.exists() or content_object.new_einvoice_on_void_einvoice_set.exists():
                kind = '57'
            elif '3J0002' == content_object.carrier_type and LegalEntity.GENERAL_CONSUMER_IDENTIFIER != content_object.buyer_identifier:
                kind = 'cp'
            elif "" != content_object.carrier_type:
                kind = 'np'
            elif "1" == content_object.donate_mark:
                kind = 'np'
            else:
                kind = 'wp'

            if kind in ["wp", "cp", "np"] and UploadBatch.objects.filter(turnkey_service=content_object.seller_invoice_track_no.turnkey_web,
                                                                         mig_type=mig_type,
                                                                         kind=kind,
                                                                         status="0",
                                                                         create_time__gte=start_time, create_time__lt=end_time).exists():
                _ub = UploadBatch.objects.filter(turnkey_service=content_object.seller_invoice_track_no.turnkey_web,
                                                 mig_type=mig_type,
                                                 kind=kind,
                                                 status="0",
                                                 create_time__gte=start_time,
                                                 create_time__lt=end_time).order_by('-id')[0]
                if _ub.batcheinvoice_set.count() < 1000:
                    ub = _ub
                else:
                    ub = UploadBatch(turnkey_service=content_object.seller_invoice_track_no.turnkey_web,
                                     mig_type=mig_type,
                                     kind=kind,
                                     status='0')
                    ub.save()
            else:
                ub = UploadBatch(turnkey_service=content_object.seller_invoice_track_no.turnkey_web,
                                 mig_type=mig_type,
                                 kind=kind,
                                 status='0')
                ub.save()
            be = BatchEInvoice(batch=ub,
                               content_object=content_object,
                               begin_time=content_object.seller_invoice_track_no.begin_time,
                               end_time=content_object.seller_invoice_track_no.end_time,
                               track_no=content_object.track_no,
                               body="",
                               )
            be.save()
            return ub
        elif content_object._meta.model_name in ['canceleinvoice', 'voideinvoice']:
            if 'canceleinvoice' == content_object._meta.model_name:
                mig_type = EInvoiceMIG.objects.get(no='C0501')
                kind = 'w4'
            elif 'voideinvoice' == content_object._meta.model_name:
                mig_type = EInvoiceMIG.objects.get(no='C0701')
                kind = '54'
            slug_prefix = '{}{}'.format(mig_type.no[2], content_object.einvoice.track_no)
            index = '{:03d}'.format(UploadBatch.objects.filter(slug__startswith=slug_prefix).count() + 1)
            slug = "{}{}".format(slug_prefix, index)
            ub = UploadBatch(turnkey_service=content_object.einvoice.seller_invoice_track_no.turnkey_web,
                             slug=slug,
                             mig_type=mig_type,
                             kind=kind,
                             status='0')
            ub.save()
            be = BatchEInvoice(batch=ub,
                               content_object=content_object,
                               begin_time=content_object.einvoice.seller_invoice_track_no.begin_time,
                               end_time=content_object.einvoice.seller_invoice_track_no.end_time,
                               track_no=content_object.einvoice.track_no,
                               body="",
                               )
            be.save()
            return ub
        else:
            return None


    def update_batch_einvoice_status_result_code(self, status={}, result_code={}):
        lg = logging.getLogger("taiwan_einvoice")
        for rc, ids in result_code.items():
            beteis = self.batcheinvoice_set.filter(id__in=ids)
            if len(ids) != beteis.count():
                raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match batch_einvoice_ids({})".format(self, ids))
            else:
                beteis.update(result_code=rc)
        
        ids_in_c = []
        status['__else__'] = status['__else__'].lower()
        finish_status = ['i', 'e', 'c']
        is_finish = True
        exclude_ids = []
        lg.debug("status: {}".format(status))
        for s, ids in status.items():
            lg.debug("UploadBatch.update_batch_einvoice_status_result_code {}: {}".format(s, ids))

            s = s.lower()
            if "__else__" == s:
                continue
            beteis = self.batcheinvoice_set.filter(id__in=ids)
            if len(ids) != beteis.count():
                raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match batch_einvoice_ids({})".format(self, ids))
            else:
                beteis.update(status=s)
                if 'c' == s and not ids_in_c:
                    ids_in_c = ids

            exclude_ids.extend(ids)
            if s not in finish_status:
                is_finish = False
        beteis = self.batcheinvoice_set.exclude(id__in=exclude_ids)
        if beteis.count() != self.batcheinvoice_set.count() - len(exclude_ids):
            raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match excluding batch_einvoice_ids({})".format(self, ids))
        else:
            beteis.update(status=status['__else__'])
            if 'c' == status['__else__']:
                ids_in_c = beteis.values_list('id', named=False, flat=True)

        if ids_in_c:
            bei = self.batcheinvoice_set.get(id=ids_in_c[0])
            content_model = bei.content_type.model_class()
            content_ids = BatchEInvoice.objects.filter(id__in=ids_in_c
                                                      ).values_list('object_id',
                                                                    named=False,
                                                                    flat=True)
            lg.debug("content_ids: {}".format(content_ids))
            content_model.objects.filter(id__in=content_ids).update(ei_synced=True)

        if status['__else__'] not in finish_status:
            is_finish = False
        
        for error_bei in self.batcheinvoice_set.filter(Q(status__in=("e", "i"))
                                                        |~Q(result_code="")
                                                        ):
            target_audience_type = "p"
            title = _("Error in sync the E-Invoice({content_object}) of {slug} for {target_audience}").format(
                slug=self.slug,
                content_object=str(error_bei.content_object),
                target_audience=_("General User") if "g" == target_audience_type else _("Programmer"),
            )
            body = _("""Error status: "{status}"
Result code: "{result_code}"
            """).format(status=bei.status, result_code=bei.result_code)

            te_alarm, new_creation = TEAlarm.objects.get_or_create(
                turnkey_service=self.turnkey_service,
                target_audience_type=target_audience_type,
                title=title,
                body=body,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.id,
            )
            only_with_perms_in = {"g": ("view_te_alarm_for_general_user", "view_te_alarm_for_programmer", ),
                                    "p": ("view_te_alarm_for_programmer", ),
                                    }[target_audience_type]
            notified_users = get_users_with_perms(self, only_with_perms_in=only_with_perms_in)
            if notified_users:
                te_alarm.notified_users.add(notified_users)

        return is_finish


    def generate_slug(self):
        if self.slug:
            return self.slug
        _now = now().astimezone(TAIPEI_TIMEZONE)
        _s = _now.strftime('%Y-%m-%d 00:00:00+08:00')
        start_time = datetime.datetime.strptime(_s, '%Y-%m-%d %H:%M:%S%z')
        end_time = start_time + datetime.timedelta(days=1)
        _no = UploadBatch.objects.filter(create_time__gte=start_time, create_time__lt=end_time).count() + 1
        no = '{:04d}'.format(_no)
        return '{}{}{}'.format(no, get_codes(int(_now.strftime('%y%m%d')+no), seed=365724), choice(KEY_CODE_SET))
        

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)



class BatchEInvoice(models.Model):
    batch = models.ForeignKey(UploadBatch, on_delete=models.DO_NOTHING)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    @property
    def year_month_range(self):
        chmk_year = self.begin_time.astimezone(TAIPEI_TIMEZONE).year - 1911
        begin_month = self.begin_time.astimezone(TAIPEI_TIMEZONE).month
        end_month = (self.end_time.astimezone(TAIPEI_TIMEZONE) - datetime.timedelta(seconds=1)).month
        return "{}年{}-{}月".format(chmk_year, begin_month, end_month)
    track_no = models.CharField(max_length=10)
    body = models.JSONField()
    status_choices = (
        ("", _("Waiting")),
        ("p", _("Preparing for EI(P)")),
        ("g", _("Uploaded to EI or Downloaded from EI(G)")),
        ("e", _("E Error for EI process(E)")),
        ("i", _("I Error for EI process(I)")),
        ("c", _("Successful EI process(C)")),
    )
    status = models.CharField(max_length=1, default="", choices=status_choices, db_index=True)
    result_code = models.CharField(max_length=5, default='', db_index=True)
    pass_if_error = models.BooleanField(default=False)
    history = HistoricalRecords()
    @property
    def last_einvoices_content_type(self):
        eict, new_creation = EInvoicesContentType.objects.get_or_create(
            content_type=self.content_type,
            object_id=self.object_id,
            status=self.status,
        )
        return eict


    def __str__(self):
        return "BatchEInvoice {}. {}".format(self.id, self.content_object)



class AuditType(models.Model):
    name_choices = (
        ("TEA_CEC_PROCESSING", "TEA/CEC Processing"),
        ("UPLOAD_TO_EITURNKEY", "Upload to EITurnkey"),
        ("EITURNKEY_PROCESSING", "EITurnkey Processing"),
        ("EI_PROCESSING", "EI Processing"),
        ("EI_PROCESSED", "EI Processed"),
    )
    name = models.CharField(max_length=32, choices=name_choices, unique=True)



class AuditLog(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    type = models.ForeignKey(AuditType, on_delete=models.DO_NOTHING)
    turnkey_service = models.ForeignKey(TurnkeyService, on_delete=models.DO_NOTHING)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')
    is_error = models.BooleanField(default=False)
    log = models.JSONField()



class EInvoicesContentType(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')
    status_choices = list(BatchEInvoice.status_choices) + [("-", _("BatchEInvoice does exist"))]
    status = models.CharField(max_length=1, default="", choices=status_choices, db_index=True)



class TEAlarm(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    turnkey_service = models.ForeignKey(TurnkeyService, on_delete=models.DO_NOTHING)
    target_audience_type_choices = (
        ("g", _("General User"), ),
        ("p", _("Programmer"), ),
    )
    target_audience_type = models.CharField(max_length=1, choices=target_audience_type_choices)
    notified_users = models.ManyToManyField(User)
    title = models.CharField(max_length=255)
    body = models.TextField()
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')


class SummaryReport(models.Model):
    LAST_BATCH_EINVOICE_DOES_NOT_EXIST_MESSAGE = _("The last Batch E-Invoice does not exist!")
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    turnkey_service = models.ForeignKey(TurnkeyService, on_delete=models.DO_NOTHING)
    begin_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    report_type_choices = (
        ("h", _("Hour")),
        ("d", _("Day")),
        ("w", _("Week")),
        ("m", _("Month")),
        ("o", _("Odd month ~ Even month")),
        ("y", _("Year")),
        ("E", _("Daily summary from EI")),
    )
    report_type = models.CharField(max_length=1, choices=report_type_choices, db_index=True)
    problems = models.JSONField()

    good_count = models.SmallIntegerField(default=0)
    failed_count = models.SmallIntegerField(default=0)
    resolved_count = models.SmallIntegerField(default=0)

    good_counts = models.JSONField()
    failed_counts = models.JSONField()
    resolved_counts = models.JSONField()

    good_objects = models.ManyToManyField(EInvoicesContentType, related_name="summary_report_set_as_good_object")
    failed_objects = models.ManyToManyField(EInvoicesContentType, related_name="summary_report_set_as_failed_object")
    resolved_objects = models.ManyToManyField(EInvoicesContentType, related_name="summary_report_set_as_resolved_object")

    is_resolved = models.BooleanField(default=False)
    resolved_note = models.TextField(default="")
    resolver = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)

    te_alarms = GenericRelation(TEAlarm)

    class Meta:
        unique_together = (("turnkey_service", "begin_time", "report_type", ), )


    
    @classmethod
    def generate_report_and_notice(cls, turnkey_service, report_type, begin_time, end_time):
        if now() - end_time < MARGIN_TIME_BETWEEN_END_TIME_AND_NOW:
            return None
        lg = logging.getLogger("taiwan_einvoice")
        translation.activate(settings.LANGUAGE_CODE)

        model_objects = [EInvoice.objects.filter(seller_invoice_track_no__turnkey_web=turnkey_service, 
                                                 create_time__gte=begin_time,
                                                 create_time__lt=end_time).order_by('id'),
                         CancelEInvoice.objects.filter(einvoice__seller_invoice_track_no__turnkey_web=turnkey_service,
                                                       create_time__gte=begin_time,
                                                       create_time__lt=end_time).order_by('id'),
                         VoidEInvoice.objects.filter(einvoice__seller_invoice_track_no__turnkey_web=turnkey_service,
                                                     create_time__gte=begin_time,
                                                     create_time__lt=end_time).order_by('id')]
        problems = {}
        good_count = 0
        failed_count = 0
        resolved_count = 0
        good_counts = {}
        failed_counts = {}
        resolved_counts = {}
        good_objects = []
        failed_objects = []
        resolved_objects = []
        def dict_value_plus_1(dictionary, key):
            if key in dictionary: dictionary[key] += 1
            else: dictionary[key] = 1

        try:
            summary_report = cls.objects.get(turnkey_service=turnkey_service,
                                             report_type=report_type,
                                             begin_time=begin_time,
                                             end_time=end_time)
        except cls.DoesNotExist:
            summary_report = cls(turnkey_service=turnkey_service,
                                 report_type=report_type,
                                 begin_time=begin_time,
                                 end_time=end_time)
            
            new_creation = True
        else:
            new_creation = False
        if not new_creation and (summary_report.failed_count <= 0
            or summary_report.is_resolved
            ):
            return summary_report

        vars_list_for_ei_synced_true_false = {True: {
                                                    "count_var": good_count,
                                                    "counts_var": good_counts,
                                                    "objects_list": good_objects,
                                              },
                                              False: {
                                                    "count_var": failed_count,
                                                    "counts_var": failed_counts,
                                                    "objects_list": failed_objects,
                                              }}
        if new_creation:
            for mos in model_objects:
                for ei_synced, _vars in vars_list_for_ei_synced_true_false.items():
                    for m in mos.filter(ei_synced=ei_synced):
                        _vars["count_var"] += 1
                        dict_value_plus_1(_vars["counts_var"], m.get_mig_no())
                        last_batch_einvoice = m.last_batch_einvoice
                        if last_batch_einvoice:
                            last_einvoices_content_type = last_batch_einvoice.last_einvoices_content_type
                        else:
                            last_einvoices_content_type = EInvoicesContentType(content_type=ContentType.objects.get_for_model(m),
                                                                               object_id=m.id,
                                                                               status="-",
                                                                              )
                            last_einvoices_content_type.save()
                            problem_key = "{mig_no}-{track_no}-{einvoices_content_type_id}".format(
                                mig_no=m.get_mig_no(),
                                track_no=m.track_no,
                                einvoices_content_type_id=last_einvoices_content_type.id,
                            )
                            problems.setdefault(problem_key, []).append(summary_report.LAST_BATCH_EINVOICE_DOES_NOT_EXIST_MESSAGE)
                        _vars["objects_list"].append(last_einvoices_content_type)

            good_count = vars_list_for_ei_synced_true_false[True]["count_var"]
            failed_count = vars_list_for_ei_synced_true_false[False]["count_var"]
            if 0 >= good_count + failed_count:
                return None
            summary_report.problems = problems
            summary_report.good_count = good_count
            summary_report.good_counts = vars_list_for_ei_synced_true_false[True]["counts_var"]
            summary_report.resolved_count = resolved_count
            summary_report.failed_count = failed_count
            summary_report.failed_counts = vars_list_for_ei_synced_true_false[False]["counts_var"]
            summary_report.resolved_counts = resolved_counts
            summary_report.save()
            summary_report.good_objects.add(*vars_list_for_ei_synced_true_false[True]["objects_list"])
            if vars_list_for_ei_synced_true_false[False]["objects_list"]:
                summary_report.failed_objects.add(*vars_list_for_ei_synced_true_false[False]["objects_list"])
            summary_report.notice(new_creation=True)
        else:
            for eict in summary_report.failed_objects.all():
                if eict.content_object.ei_synced:
                    resolved_count += 1
                    dict_value_plus_1(resolved_counts, eict.content_object.get_mig_no())
                    resolved_objects.append(eict.content_object.last_batch_einvoice.last_einvoices_content_type)
            summary_report.resolved_count = resolved_count
            summary_report.resolved_counts = resolved_counts
            if summary_report.resolved_count >= summary_report.failed_count:
                summary_report.is_resolved = True
            summary_report.save()
            if resolved_objects:
                summary_report.resolved_objects.add(*resolved_objects)
            summary_report.notice(new_creation=False)

        return summary_report
    

    @classmethod
    def auto_generate_report(cls, generate_at_time=None):
        if not generate_at_time:
            generate_at_time = now()
        timedelta_d = {
            "h": datetime.timedelta(minutes=91),
            "d": datetime.timedelta(hours=24 + 8),
            "w": datetime.timedelta(hours=24 * 7 + 9),
            "m": datetime.timedelta(hours=24 * 31 + 10),
            "o": datetime.timedelta(hours=24 * 61 + 11),
            "y": datetime.timedelta(hours=24 * 365 + 12),
        }
        for turnkey_service in TurnkeyService.objects.all().order_by('id'):
            for report_type, report_type_str in cls.report_type_choices:
                if not timedelta_d.get(report_type, None):
                    continue
                generate_for_time = (generate_at_time - timedelta_d[report_type]).astimezone(TAIPEI_TIMEZONE)
                _Y, _m, _d, _H, _M, _S = generate_for_time.timetuple()[:6]
                if "h" == report_type:
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, _m, _d, _H, 0, 0))
                    end_time = begin_time + datetime.timedelta(minutes=60)
                elif "d" == report_type:
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, _m, _d, 0, 0, 0))
                    end_time = begin_time + datetime.timedelta(hours=24)
                elif "w" == report_type:
                    _begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, _m, _d, 0, 0, 0))
                    begin_time = _begin_time - datetime.timedelta(days=_begin_time.weekday())
                    end_time = begin_time + datetime.timedelta(days=7)
                elif "m" == report_type:
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, _m, 1, 0, 0, 0))
                    _end_time = begin_time + datetime.timedelta(days=45)
                    end_time = TAIPEI_TIMEZONE.localize(datetime.datetime(*_end_time.timetuple()[:2], 1))
                elif "o" == report_type:
                    if 1 == _m % 2:
                        begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, _m, 1, 0, 0, 0))
                    else:
                        _begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, _m, 1, 0, 0, 0)) - datetime.timedelta(days=10)
                        begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(*_begin_time.timetuple()[:2], 1))
                    _end_time = begin_time + datetime.timedelta(days=75)
                    end_time = TAIPEI_TIMEZONE.localize(datetime.datetime(*_end_time.timetuple()[:2], 1))
                elif "y" == report_type:
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, 1, 1, 0, 0, 0))
                    _end_time = begin_time + datetime.timedelta(days=540)
                    end_time = TAIPEI_TIMEZONE.localize(datetime.datetime(*_end_time.timetuple()[:1], 1, 1))

                if now() - end_time >= MARGIN_TIME_BETWEEN_END_TIME_AND_NOW:
                    cls.generate_report_and_notice(turnkey_service, report_type, begin_time, end_time)
    

    def notice(self, new_creation=True):
        if self.failed_count <= 0 or self.resolved_count >= self.failed_count:
            return

        translation.activate(settings.LANGUAGE_CODE)
        target_audience_types = {}
        for failed_einvoice_ct in self.failed_objects.all():
            if self.resolved_objects.filter(id=failed_einvoice_ct.id):
                continue

            mig_no = failed_einvoice_ct.content_object.get_mig_no()
            track_no = failed_einvoice_ct.content_object.track_no
            fe_key = "{mig_no}-{track_no}-{einvoices_content_type_id}".format(
                mig_no=mig_no,
                track_no=track_no,
                einvoices_content_type_id=failed_einvoice_ct.id,
            )

            last_batch_einvoice = failed_einvoice_ct.content_object.last_batch_einvoice
            if last_batch_einvoice and "wp" == last_batch_einvoice.batch.kind:
                target_audience_types.setdefault("g", {})[fe_key] = _("Please print the E-Invoice({track_no}) as soon as possible, so that the system can sync this E-Invoice to EI").format(track_no=track_no)
            elif not last_batch_einvoice:
                target_audience_types.setdefault("p", {})[fe_key] = self.LAST_BATCH_EINVOICE_DOES_NOT_EXIST_MESSAGE
            elif last_batch_einvoice and last_batch_einvoice.batch.kind in ["cp", "np"]:
                target_audience_types.setdefault("p", {})[fe_key] = _("Please check taiwan_einvoice.crontabs.polling_upload_batch for the E-Invoice({track_no})").format(track_no=track_no)
            else:
                target_audience_types.setdefault("p", {})[fe_key] = _("The {track_no}@{mig_no} has result_code: {status}-{result_code}").format(
                    track_no=track_no,
                    mig_no=mig_no,
                    status=last_batch_einvoice.status,
                    result_code=last_batch_einvoice.result_code,
                )
        summary_report_problems = self.problems
        for target_audience_type, errors_d in target_audience_types.items():
            _errors_keys = list(errors_d.keys())
            _errors_keys.sort(key=lambda x: x.split('-')[1])
            _bodys = []
            for _ek in _errors_keys:
                _bodys.append(errors_d[_ek])
                if _ek in summary_report_problems:
                    if errors_d[_ek] not in summary_report_problems[_ek]:
                        summary_report_problems[_ek].append(errors_d[_ek])
                else:
                    summary_report_problems[_ek] = [errors_d[_ek]]
            body = "\n\n".join(_bodys)
            title = _("Failed-sync E-Invoice(s) in {name} summary report({report_type}@{begin_time}) for {target_audience}").format(
                name=self.turnkey_service.name,
                report_type=self.get_report_type_display(),
                begin_time=self.begin_time.strftime("%Y-%m-%d %H:%M:%S"),
                target_audience=_("General User") if "g" == target_audience_type else _("Programmer"),
            )

            te_alarm, new_creation = TEAlarm.objects.get_or_create(
                turnkey_service=self.turnkey_service,
                target_audience_type=target_audience_type,
                title=title,
                body=body,
                content_type=ContentType.objects.get_for_model(self),
                object_id=self.id,
            )
            only_with_perms_in = {"g": ("view_te_alarm_for_general_user", "view_te_alarm_for_programmer", ),
                                  "p": ("view_te_alarm_for_programmer", ),
                                 }[target_audience_type]
            notified_users = get_users_with_perms(self, only_with_perms_in=only_with_perms_in)
            if notified_users:
                te_alarm.notified_users.add(notified_users)
        self.problems = summary_report_problems
        self.save()


