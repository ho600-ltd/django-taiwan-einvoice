import pytz, datetime, hmac, requests, logging, zlib, json, re, decimal, time, math
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
from django.utils.timezone import now, utc
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext, pgettext
from simple_history.models import HistoricalRecords
from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms

from ho600_ltd_libraries.utils.formats import customize_hex_from_integer, integer_from_customize_hex
from taiwan_einvoice.libs import CounterBasedOTPinRow


def _year_to_chmk_year(year):
    return year - 1911


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
COULD_PRINT_TIME_MARGIN = datetime.timedelta(minutes=15)
NO_NEED_TO_PRINT_TIME_MARGIN = datetime.timedelta(minutes=10)
MARGIN_TIME_BETWEEN_END_TIME_AND_NOW = datetime.timedelta(minutes=31)
SELLER_INVOICE_TRACK_NO_ALLOW_CANCEL_MIARGIN = datetime.timedelta(days=15)



class IdentifierError(Exception):
    pass



class IdentifierDuplicateError(Exception):
    pass



class SellerInvoiceTrackNoDisableError(Exception):
    pass



class ExcutedE0402UploadBatchError(Exception):
    pass



class ExistedE0402UploadBatchError(Exception):
    pass



class NotCurrentSellerInvoiceTrackNoError(Exception):
    pass



class CancelEInvoiceMIGError(Exception):
    pass



class VoidEInvoiceMIGError(Exception):
    pass



class BatchEInvoiceIDsError(Exception):
    pass



class BatchEInvoiceContentTypeError(Exception):
    pass



class TEAStaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    nickname = models.CharField(max_length=255, default='')
    is_active = models.BooleanField(default=True)
    @property
    def printer_admin_group(self):
        if self.in_printer_admin_group:
            return Group.objects.get(name="TaiwanEInvoicePrinterAdminGroup")
    @property
    def in_printer_admin_group(self):
        return self.user.is_superuser or self.user.groups.filter(name="TaiwanEInvoicePrinterAdminGroup").exists()
    @property
    def manager_group(self):
        if self.in_manager_group:
            return Group.objects.get(name="TaiwanEInvoiceManagerGroup")
    @property
    def in_manager_group(self):
        return self.user.is_superuser or self.user.groups.filter(name="TaiwanEInvoiceManagerGroup").exists()
    @property
    def groups(self):
        ct_id = ContentType.objects.get_for_model(TurnkeyService).id
        groups = {}
        for g in Group.objects.filter(name__startswith="ct{ct_id}:".format(ct_id=ct_id)).order_by('name'):
            turnkey_service_id = g.name.split(':')[1]
            turnkey_service = TurnkeyService.objects.get(id=turnkey_service_id)
            g.display_name = ''.join(g.name.split(':')[2:])
            is_member = self.user.groups.filter(id=g.id).exists()
            groups.setdefault(turnkey_service.name, []).append({"id": g.id,
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


TAIWAN_EI_TAX_TYPES = {
    "1": "應稅",
    "2": "零稅率",
    "3": "免稅",
    "4": "應稅(特種稅率)",
    "9": "混合應稅與免稅或零稅率",
}


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
            return TEAStaffProfile.objects.none()
        else:
            return TEAStaffProfile.objects.filter(user__in=g.user_set.all()).order_by('nickname')


    @property
    def operators(self):
        try:
            g = Group.objects.get(name='TaiwanEInvoicePrinterAdminGroup')
        except Group.DoesNotExist:
            admin_users = []
        else:
            admin_users = g.user_set.all()
        users = get_users_with_perms(self, only_with_perms_in=['operate_te_escposweb'])
        return TEAStaffProfile.objects.filter(user__is_superuser=False,
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
        ('7', _('58mm E-Invoice in 80mm Machine')),
        ('8', _('80mm Receipt')),
    )
    escpos_web = models.ForeignKey(ESCPOSWeb, on_delete=models.DO_NOTHING)
    serial_number = models.CharField(max_length=128, unique=True)
    nickname = models.CharField(max_length=64, unique=True)
    receipt_type = models.CharField(max_length=1, choices=RECEIPT_TYPES)
    


class IdentifierRule(object):
    """ Official rules from https://www.fia.gov.tw/singlehtml/6?cntId=aaa97a9dcf2649d5bdd317f554e24f75
    Now, the rules use pass_rule_has_7_times_10, pass_rule_has_no_7_times_10.
    After 2023-Apr-01, the rules also apply pass_rule_has_7_times_5, pass_rule_has_no_7_times_5.
    """ 
    def __init__(self, NOW=None):
        if NOW:
            self.now = NOW
        else:
            self.now = now()
    def times_for_no_7(self, no):
        default = [1, 2, 1, 2, 1, 2, 4, 1]
        nos = [int(i) for i in list(no)]
        _sum = 0
        for _ in range(8):
            _s = default[_] * nos[_]
            if _s < 10:
                _sum += _s
            else:
                _sum += sum([int(i) for i in list(str(_s))])
        return _sum
    def times_for_7(self, no):
        default = [1, 2, 1, 2, 1, 2, 4, 1]
        nos = [int(i) for i in list(no)]
        _sum = []
        for _ in range(8):
            _s = default[_] * nos[_]
            if _s < 10:
                _sum.append(_s)
            else:
                _sum.append(sum([int(i) for i in list(str(_s))]))
        _sum[6] = 0
        s0 = sum(_sum)
        _sum[6] = 1
        s1 = sum(_sum)
        return s0, s1
    def pass_rule_has_no_7_times_10(self, no):
        if '7' == no[6]:
            return False
        sum = self.times_for_no_7(no)
        if 0 == sum % 10:
            return True
        return False
    def pass_rule_has_7_times_10(self, no):
        if '7' != no[6]:
            return False
        s0, s1 = self.times_for_7(no)
        if 0 == s0 % 10 or 0 == s1 % 10:
            return True
        return False
    def pass_rule_has_no_7_times_5(self, no):
        if '7' == no[6] or self.now < datetime.datetime(2023, 4, 1, 0, 0, 0, tzinfo=pytz.timezone('Asia/Taipei')):
            return False
        sum = self.times_for_no_7(no)
        if 0 == sum % 5:
            return True
        return False
    def pass_rule_has_7_times_5(self, no):
        if '7' != no[6] or self.now < datetime.datetime(2023, 4, 1, 0, 0, 0, tzinfo=pytz.timezone('Asia/Taipei')):
            return False
        s0, s1 = self.times_for_7(no)
        if 0 == s0 % 5 or 0 == s1 % 5:
            return True
        return False
    def verify_identifier(self, identifier):
        if (re.match('^[0-9]{8}$', identifier)
            and (self.pass_rule_has_no_7_times_10(identifier)
                    or self.pass_rule_has_7_times_10(identifier)
                    or self.pass_rule_has_no_7_times_5(identifier)
                    or self.pass_rule_has_7_times_5(identifier)
                )
           ):
            return True
        return False
    def test(self):
        tz = pytz.timezone('Asia/Taipei')
        data = [
            ['04595257', True, now()],
            ['10458575', True, now()],
            ['12458576', False, now()],
            ['04595257', True, datetime.datetime(2020, 1, 1, tzinfo=tz)],
            ['04595252', False, datetime.datetime(2020, 1, 1, tzinfo=tz)],
            ['04595252', True, datetime.datetime(2024, 1, 1, tzinfo=tz)],
            ['12458576', True, datetime.datetime(2024, 1, 1, tzinfo=tz)],
        ] + [[i, False, now()] for i in ['12168316', '16545004', '90000067', '90091679', '90149727', '90167282', '90170888', '90175400', '90176163', '90189946', '90194167', '90196306', '90205770', '90212940', '90234091', '90234348', '90252631', '90253564', '90262020', '90264561', '90265816', '90271431', '90287623', '90288196', '90288850', '90290623', '90298042', '90298359', '90298873', '90299158', '90299456', '90299621', '90300254', '90300706', '90300843', '90305749', '90306000', '90311186', '90313827', '90315248', '90316047', '90318256', '90350235', '90350632', '90472225', '90476449', '90483734', '04080790', '04316216', '04475706', '04494701', '12313638', '12510147', '12721929', '13129413', '16477612', '20590056', '21311263', '22576190', '22717647', '22752231', '22815949', '22822485', '22891804', '23324463', '24038562', '28467994', '70454685', '70778243', '70849969', '80509808', '86275723', '86378629', '86518088', '89389431', '89415770', '12430308', '00000001', '00000243', '00000334', '00000369', '00000881', '00000927', '00002310', '00003021', '00003125', '00004282', '00005254', '00005941', '00006422', '00006701', '00010609', '00011794', '00012403', '00014374', '00015832', '00016634', '00019404', '00024092', '00024905', '00025010', '00028968', '00031118', '00032537', '00034111', '00036354', '00036355', '00036409', '00040035', '00051568', '00053601', '00054062', '00055115', '00055478', '00056057', '00056105', '00056935', '00057529', '00057995', '00060475', '00061664', '00061797', '00062839', '00065142', '00065577', '00067836', '00068092', '00071667', '00071838', '00072371', '00073680', '00074105', '00077320', '00077856', '00078925', '00079036', '00079100', '00083603', '00085690', '00301593', '00433500', '01840868', '02080513', '02617989', '02944260', '05459412', '05675379', '06282757', '06292978', '07996647', '08039532', '08042671', '09501012', '10000000', '10142789', '10382224', '11111111', '12182123', '12562776', '12682993', '13486970', '13886644', '14000000', '14598784', '16074990', '16221297', '17188079', '17583835', '17640004', '17779260', '20192018', '20326241', '20425735', '21307709', '21883419', '26378574', '27190197', '29828436', '33097039', '33283074', '33812816', '33852609', '33870068', '33878778', '33881385', '33916021', '33951828', '34197422', '34297459', '34616344', '35000194', '35000524', '35000576', '35000586', '36001241', '36001392', '36002097', '36002131', '36002151', '36002340', '36002558', '36002561', '36002638', '36002689', '36003212', '36003302', '36003457', '36003890', '36204623', '37004631', '37004861', '37106149', '37693956', '37723887', '38005008', '38005022', '38005117', '38005184', '38005466', '38005468', '38005821', '38005838', '38024958', '38466120', '38921194', '39006681', '39006937', '39006953', '39007352', '39007524', '39007525', '39008346', '39008566', '39008611', '39008862', '39009552', '39009684', '39009960', '39010003', '39010439', '39777694', '39813139', '40010598', '40010910', '40011102', '40011386', '40011693', '40011733', '40011911', '40012816', '40175100', '40186701', '40288580', '40327108', '41013202', '41013240', '41014523', '41101224', '41760021', '42766352', '43016738', '43016927', '43017197', '43017209', '43017283', '43017320', '43017740', '43018414', '43018457', '43018778', '43018822', '43076204', '43276818', '43316101', '43351338', '43355354', '43641107', '43725245', '43774338', '44019259', '44019334', '44019437', '44019496', '44019693', '44019860', '44019950', '44020212', '44020560', '44020831', '44020930', '44020973', '44021005', '44021095', '44021230', '44516246', '44699100', '45011319', '45014124', '45016245', '45021623', '45021697', '45021997', '45022426', '45022929', '45023153', '45023560', '45023613', '45023697', '45024213', '45024450', '45027542', '45039356', '45322791', '45749376', '45903359', '46024729', '46024752', '46024961', '46025161', '46025627', '46025660', '46026335', '46026484', '46026987', '46027476', '46028329', '46120849', '46264294', '47029423', '47029820', '47029947', '47030518', '47030522', '47030680', '47030816', '47031358', '47031426', '47031793', '47032568', '47311366', '47312350', '48023069', '48033392', '48033859', '48033870', '48034130', '48034453', '48034540', '48034813', '48035351', '48035425', '48035488', '48036047', '49036799', '49037473', '49037520', '49037700', '49037708', '49038029', '49038414', '49295388', '50039236', '50039307', '50039392', '50039954', '50040119', '50040146', '50040263', '50040333', '50040462', '50040650', '50041016', '50041641', '50041683', '50042347', '51042671', '51042941', '51043358', '51043462', '51044748', '51044762', '51044979', '51045013', '51234220', '52046448', '52046625', '52046664', '52046736', '52046742', '52046841', '52047290', '52047509', '52047924', '52047983', '52048433', '52349668', '52534405', '52647512', '52699282', '52921027', '53049094', '53049309', '53049348', '53049646', '53049794', '53049818', '53049833', '53049877', '53049969', '53049989', '53050184', '53050288', '53050633', '53050692', '53051524', '53051538', '53051552', '53051592', '54052136', '54052385', '54052409', '54052733', '54052737', '54052874', '54053120', '54053151', '54053288', '54053536', '54053577', '54053899', '54054177', '54054595', '54064198', '55054849', '55054889', '55055017', '55055033', '55055122', '55055213', '55055278', '55055286', '55055327', '55055804', '55056302', '55056821', '55056904', '55649920', '56057900', '56058223', '56058983', '56059795', '57060545', '57060580', '57060654', '57061070', '57061073', '57061157', '57061198', '57061819', '57062160', '57062191', '57062367', '57062382', '57063067', '58063157', '58063854', '58063963', '58064018', '58064033', '58064616', '58064843', '58064997', '58065362', '58065482', '58509809', '58995127', '59066890', '59121181', '59320754', '59439341', '59595714', '59809305', '60071631', '60071898', '60072382', '60208081', '60327680', '61073003', '61073080', '61073112', '61074224', '61074492', '61074603', '61074764', '61075514', '61076122', '62077365', '62078052', '62078168', '62078258', '62078477', '62078769', '62079193', '62080227', '63081626', '63081788', '63082863', '63083183', '63083448', '63084150', '63084402', '63084657', '63085314', '63085715', '63086518', '63720734', '63801647', '64088499', '64089438', '64089555', '64089835', '64090089', '64090867', '64091354', '64364899', '64458887', '64815710', '64826546', '64826826', '64858047', '65057626', '65093535', '65093789', '65094196', '65096349', '65097252', '65097697', '65097842', '65098519', '65298006', '65499209', '65954604', '66100066', '66100339', '66101474', '66102738', '66103432', '66104072', '66212662', '66386619', '66588701', '66615257', '67105900', '67107345', '67107746', '67110489', '67110534', '67302203', '68112803', '68113745', '68113865', '68114415', '68116049', '68116205', '68116317', '68116392', '68980907', '69116846', '69119044', '69120007', '69488008', '69910232', '70126794', '70939077', '70965539', '73701503', '73729183', '74155522', '76168841', '76777507', '76820402', '77100781', '77263460', '77327583', '77342780', '77548437', '77702742', '77703475', '77703901', '77710286', '77711261', '78123298', '78225692', '78690992', '78897377', '78918328', '80513640', '81022175', '81817618', '81999270', '82714551', '83029715', '83031566', '83033003', '85005455', '85031897', '85873579', '85971047', '86076879', '87058028', '87089107', '87214259', '87340203', '88067658', '88349705', '88821456', '89234335', '90080923', '90081317', '90081354', '90081997', '90280628', '90443306', '90711192', '90730744', '90736019', '90762332', '91082416', '91778147', '91813447', '91866460', '92122410', '92150251', '92176116', '92397412', '93011373', '93247104', '93272902', '93529157', '93609603', '93646804', '93650907', '93724786', '93748888', '94223708', '94323010', '94341999', '95996504', '96392339', '97605762', '97900589', '99900124', '99900294', '99900404', '99902501', '99903101', '99903573', '99903587', '99904892', '99906168', '99906226', '99909075', '99909282', '99909801', '99910871', '99912701', '99913702', '99913704', '99913739', '99913941', '99915036', '99915045', '99915099', '99915413', '99917088', '99917210', '99917219', '99919074', '99920396', '99925811', '99931430', '99999998']
        ]
        
        for d in data:
            self.now = d[2]
            if d[1] != self.verify_identifier(d[0]):
                raise Exception(str(d))



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
            return ("$:{}".format(self.pk))[:20]
        else:
            return self.customer_number_char[:20]
    @customer_number.setter
    def customer_number(self, char):
        self.customer_number_char = char
        self.save()
    role_remark = models.CharField(max_length=40, default='', db_index=True)


    class Meta:
        unique_together = (('identifier', 'customer_number_char'), )
    

    def __str__(self):
        return "{}({}/{})".format(self.identifier, self.name, self.customer_number)
    

    def save(self, *args, **kwargs):
        if self.GENERAL_CONSUMER_IDENTIFIER != self.identifier and False == self.verify_identifier(self.identifier):
            raise IdentifierDoesNotExist(_('Buyer identifier is not valid.'))
        super().save(*args, **kwargs)



class Seller(models.Model):
    legal_entity = models.ForeignKey(LegalEntity, unique=True, on_delete=models.DO_NOTHING)
    print_with_seller_optional_fields = models.BooleanField(default=False)
    print_with_buyer_optional_fields = models.BooleanField(default=False)
    

    def __str__(self):
        return "{}: {}, {}".format(self.legal_entity,
                                   self.print_with_seller_optional_fields,
                                   self.print_with_buyer_optional_fields)
    

    def save(self, *args, **kwargs):
        if not self.pk and Seller.objects.filter(legal_entity__identifier=self.legal_entity.identifier).exists():
            raise IdentifierDuplicateError(_("{} does exist!").format(self.legal_entity.identifier))
        super().save(*args, **kwargs)



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
    verify_tkw_ssl = models.BooleanField(default=True)
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
        for sitn in SellerInvoiceTrackNo.filter_now_use_sitns(turnkey_service=self).filter(type='07'):
            count += sitn.count_blank_no
        return count
    @property
    def count_now_use_08_sellerinvoicetrackno_blank_no(self):
        count = 0
        for sitn in SellerInvoiceTrackNo.filter_now_use_sitns(turnkey_service=self).filter(type='08'):
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
    

    def get_and_create_ei_turnkey_daily_summary_result(self, result_date=''):
        translation.activate(settings.LANGUAGE_CODE)
        audit_type = AuditType.objects.get(name="EI_SUMMARY_RESULT")
        audit_log = AuditLog(
            creator=User.objects.get(username="^taiwan_einvoice_sys_user$"),
            type=audit_type,
            turnkey_service=self,
            content_object=self,
            is_error=False,
        )
        url = self.tkw_endpoint + '{action}/'.format(action="get_ei_turnkey_summary_results")
        counter_based_otp_in_row = ','.join(self.generate_counter_based_otp_in_row())
        payload = {"format": "json"}

        if result_date:
            try:
                _dev_null = datetime.datetime.strptime(result_date, "%Y-%m-%d")
            except:
                pass
            else:
                payload["result_date"] = result_date
        else:
            last_summary_report = self.summaryreport_set.filter(report_type='E').order_by('begin_time').last()
            if last_summary_report:
                payload["result_date__gte"] = last_summary_report.begin_time.astimezone(TAIPEI_TIMEZONE).strftime("%Y-%m-%d")

        try:
            response = requests.get(url,
                                    verify=self.verify_tkw_ssl,
                                    params=payload,
                                    headers={"X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row})
        except Exception as e:
            audit_log.is_error = True
            audit_log.log = {
                "function": "TurnkeyService.get_and_create_ei_turnkey_daily_summary_result",
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
                for summary_result in result_json['results']:
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime.strptime(summary_result['result_date'], "%Y-%m-%d"))
                    end_time = begin_time + datetime.timedelta(days=1)
                    sr, new_creation = SummaryReport.objects.get_or_create(turnkey_service=self,
                                                                           report_type='E',
                                                                           begin_time=begin_time,
                                                                           end_time=end_time,
                                                                          )
                    if sr.is_resolved:
                        continue
                    sr.generate_ei_daily_summary_report(summary_result)
                audit_log.is_error = False
                audit_log.save()
                return result_json
            else:
                audit_log.is_error = True
                audit_log.save()



    def get_and_create_ei_turnkey_e0501_invoice_assign_no(self, year_month=''):
        translation.activate(settings.LANGUAGE_CODE)
        audit_type = AuditType.objects.get(name="E0501_INVOICE_ASSIGN_NO")
        audit_log = AuditLog(
            creator=User.objects.get(username="^taiwan_einvoice_sys_user$"),
            type=audit_type,
            turnkey_service=self,
            content_object=self,
            is_error=False,
        )
        url = self.tkw_endpoint + '{action}/'.format(action="get_ei_turnkey_e0501_invoice_assign_no")
        counter_based_otp_in_row = ','.join(self.generate_counter_based_otp_in_row())
        payload = {"format": "json"}

        if year_month and 5 == len(year_month):
            try:
                year, month = int(year_month[:3]), int(year_month[3:])
            except:
                pass
            else:
                payload["year_month"] = year_month
        else:
            _date = now().astimezone(TAIPEI_TIMEZONE)
            year, month = _year_to_chmk_year(_date.year), _date.month
            payload["year_month__gte"] = '{:03d}{:02d}'.format(year, month)

        try:
            response = requests.get(url,
                                    verify=self.verify_tkw_ssl,
                                    params=payload,
                                    headers={"X-COUNTER-BASED-OTP-IN-ROW": counter_based_otp_in_row})
        except Exception as e:
            audit_log.is_error = True
            audit_log.log = {
                "function": "TurnkeyService.get_and_create_ei_turnkey_e0501_invoice_assign_no",
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
                for invoice_assign_no in result_json['results']:
                    eian, new_creation = E0501InvoiceAssignNo.objects.get_or_create(identifier=invoice_assign_no['party_id'],
                                                                                    type=invoice_assign_no['invoice_type'],
                                                                                    year_month=invoice_assign_no['year_month'],
                                                                                    track=invoice_assign_no['invoice_track'].upper(),
                                                                                    begin_no=invoice_assign_no['invoice_begin_no'],
                                                                                    end_no=invoice_assign_no['invoice_end_no'],
                                                                                   )
                    eian.booklet = invoice_assign_no['invoice_booklet']
                    eian.save()
                audit_log.is_error = False
                audit_log.save()
                return result_json
            else:
                audit_log.is_error = True
                audit_log.save()



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

            ("handle_te_batcheinvoice", "Handle Batch E-Invoice of the TurnkeyService"),

            ("view_te_einvoiceprintlog", "View E-Invoice Print Log of the TurnkeyService"),
            
            ("view_te_summaryreport", "View Summary Report of the TurnkeyService"),
            ("resolve_te_summaryreport", "Resolve Summary Report of the TurnkeyService"),

            ("view_te_alarm_for_general_user", "View Alarm for the General User of the TurnkeyService"),
            ("view_te_alarm_for_programmer", "View Alarm for the Programmer of the TurnkeyService"),
        )
    


class SellerInvoiceTrackNo(models.Model):
    turnkey_service = models.ForeignKey(TurnkeyService, on_delete=models.DO_NOTHING)
    is_disabled = models.BooleanField(default=False)
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
    def pure_year_month_range(self):
        chmk_year = _year_to_chmk_year(self.begin_time.astimezone(TAIPEI_TIMEZONE).year)
        begin_month = self.begin_time.astimezone(TAIPEI_TIMEZONE).month
        end_month = (self.end_time.astimezone(TAIPEI_TIMEZONE) - datetime.timedelta(seconds=1)).month
        return chmk_year, begin_month, end_month
    @property
    def year_month(self):
        chmk_year, begin_month, end_month = self.pure_year_month_range
        return "{:03d}{:02d}".format(chmk_year, end_month)
    @property
    def year_month_range(self):
        chmk_year, begin_month, end_month = self.pure_year_month_range
        return "{}年{}-{}月".format(chmk_year, begin_month, end_month)
    track = models.CharField(max_length=2, db_index=True)
    begin_no = models.IntegerField(db_index=True)
    @property
    def begin_no_str(self):
        return "{:08d}".format(self.begin_no)
    end_no = models.IntegerField(db_index=True)
    @property
    def end_no_str(self):
        return "{:08d}".format(self.end_no)
    allow_cancel = models.BooleanField(default=True)
    @property
    def can_cancel(self):
        if self.allow_cancel and now() < self.end_time + SELLER_INVOICE_TRACK_NO_ALLOW_CANCEL_MIARGIN:
            return True
        return False
    @property
    def count_blank_no(self):
        if self.is_disabled:
            return 0
        else:
            return self.end_no - self.begin_no + 1 - self.einvoice_set.filter(reverse_void_order=0).count()
    @property
    def next_blank_no(self):
        try:
            new_no = self.get_new_no()
        except NotEnoughNumberError:
            new_no = ''
        except SellerInvoiceTrackNoDisableError:
            new_no = ''
        return new_no
    @property
    def can_be_deleted(self):
        if self.einvoice_set.exists() or now() > self.end_time:
            return False
        else:
            return True



    class Meta:
        unique_together = (("type", "begin_time", "end_time", "track", "begin_no", "end_no"), )



    def __str__(self):
        return "{}{}({}~{}: {}{}~{})".format(self.turnkey_service,
                                             self.type,
                                             self.begin_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d'),
                                             (self.end_time-datetime.timedelta(seconds=1)).astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d'),
                                             self.track,
                                             self.begin_no_str,
                                             self.end_no_str)


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
        for sitn in queryset.filter(turnkey_service__on_working=True,
                                    is_disabled=False,
                                    begin_time__lte=_now,
                                    end_time__gt=_now).order_by('track', 'begin_no'):
            if ignore_count_blank_no:
                ids.append(sitn.id)
            elif sitn.count_blank_no > 0:
                ids.append(sitn.id)
        queryset = queryset.filter(id__in=ids)
        return queryset


    @classmethod
    def create_blank_numbers_and_upload_batchs(cls, seller_invoice_track_nos, executor=None):
        if 1 != len(seller_invoice_track_nos.values('turnkey_service__seller__legal_entity__identifier'
                                                   ).annotate(a_c=Count('turnkey_service__seller__legal_entity__identifier'))):
            raise IdentifierError(_("Only use the same identifier to create the record for blank numbers!"))
        elif 1 != len(seller_invoice_track_nos.values('begin_time').annotate(a_c=Count('begin_time'))):
            raise IdentifierError(_("Only use the same begin_time to create the record for blank numbers!"))
        elif 1 != len(seller_invoice_track_nos.values('end_time').annotate(a_c=Count('end_time'))):
            raise IdentifierError(_("Only use the same end_time to create the record for blank numbers!"))

        party_ids = [d['turnkey_service__party_id'] for d in seller_invoice_track_nos.values('turnkey_service__party_id').annotate(dev_null=Count('turnkey_service__party_id'))]
        tax_types = [d['type'] for d in seller_invoice_track_nos.values('type').annotate(dev_null=Count('type'))]
        tracks = [d['track'] for d in seller_invoice_track_nos.values('track').annotate(dev_null=Count('track'))]
        upload_batchs = []
        e0402_existed_upload_batchs = []
        e0402_excuted_upload_batchs = []
        for party_id in party_ids:
            for tax_type in tax_types:
                for track in tracks:
                    sitns = seller_invoice_track_nos.filter(turnkey_service__party_id=party_id,
                                                            type=tax_type,
                                                            track=track).order_by('track', 'begin_no')
                    upload_batch = UploadBatch.append_to_the_upload_batch(sitns.first(), executor=executor)
                    if upload_batch.status == '0':
                        upload_batchs.append(upload_batch)
                    elif upload_batch.status == 'f':
                        e0402_excuted_upload_batchs.append(upload_batch)
                    else:
                        e0402_existed_upload_batchs.append(upload_batch)
        if e0402_excuted_upload_batchs:
            details_strs = []
            for _ub in e0402_excuted_upload_batchs:
                for bei in _ub.batcheinvoice_set.all():
                    for detail in bei.content_object.export_json_for_mig()["E0402"]['Details']:
                        details_strs.append("{} ~ {}".format(*detail))
            if len(details_strs) > 1:
                msg = _("{} already have executed UploadBatch, if you want to update the records, please go to EI site to update manually!").format(", ".join(details_strs))
            else:
                msg = _("{} already has executed UploadBatch, if you want to update the records, please go to EI site to update manually!").format(", ".join(details_strs))
            raise ExcutedE0402UploadBatchError(msg)
        elif e0402_existed_upload_batchs:
            details_strs = []
            for _ub in e0402_existed_upload_batchs:
                for bei in _ub.batcheinvoice_set.all():
                    for detail in bei.content_object.export_json_for_mig()["E0402"]['Details']:
                        details_strs.append("{} ~ {}".format(*detail))
            if len(details_strs) > 1:
                msg = _("{} already have executing UploadBatch, please wait for them completed!").format(", ".join(details_strs))
            else:
                msg = _("{} already has executing UploadBatch, please wait for them completed!").format(", ".join(details_strs))
            raise ExistedE0402UploadBatchError(msg)
        return upload_batchs


    def delete(self, *args, **kwargs):
        if self.einvoice_set.exists():
            ei = self.einvoice_set.order_by('id').first()
            raise UsedSellerInvoiceTrackNoError(_("It could not be deleted, because it had E-Invoice({})").format(ei.track_no_), ei.track_no_)
        return super().delete(*args, **kwargs)


    def get_new_no(self):
        if self.is_disabled:
            raise NotEnoughNumberError(_("{} is disabled").format(self))
        max_no = self.einvoice_set.filter(no__gte=self.begin_no_str, no__lte=self.end_no_str).aggregate(Max('no'))['no__max']
        if max_no:
            max_no = int(max_no)
        else:
            lg = logging.getLogger('taiwan_einvoice')
            eis = self.einvoice_set.filter(no__gte=self.begin_no_str, no__lte=self.end_no_str).order_by('-no')
            lg.info("SellerInvoiceTrackNo.get_new_no sitn({}) has eis: {}".format(self, eis))

        if not max_no:
            new_no = self.begin_no
        elif max_no >= self.end_no:
            raise NotEnoughNumberError(_('Not enough numbers'))
        else:
            new_no = max_no + 1
        new_no = '{:08d}'.format(new_no)
        return new_no


    def create_einvoice(self, data):
        if self.is_disabled:
            raise SellerInvoiceTrackNoDisableError()

        _now = now()
        if _now < self.begin_time or _now > (self.end_time - datetime.timedelta(minutes=3)):
            raise NotCurrentSellerInvoiceTrackNoError(_("{now} does not between {begin_time} and {end_time}").format(now=_now, begin_time=self.begin_time, end_time=self.end_time))

        data['seller_invoice_track_no'] = self
        data['type'] = self.type
        data['track'] = self.track
        data['no'] = self.get_new_no()
        ei = EInvoice(**data)
        try:
            ei.save()
        except IntegrityError as e:
            lg = logging.getLogger('info')
            lg.error(vars(e))
            lg.error(str(e))
            raise GenerateTimeNotFollowNoOrderError("Duplicated no: {}".format(data['no']))
        except EInvoiceDetailsError as e:
            raise e
        return ei


    def export_json_for_mig(self):
        sitns = SellerInvoiceTrackNo.objects.filter(turnkey_service__seller__legal_entity__identifier=self.turnkey_service.seller.legal_entity.identifier,
                                                    begin_time=self.begin_time,
                                                    end_time=self.end_time,
                                                    turnkey_service__party_id=self.turnkey_service.party_id,
                                                    type=self.type,
                                                    track=self.track).order_by('track', 'begin_no')
        Details = []
        for sitn in sitns:
            if sitn.next_blank_no:
                Details.append((sitn.next_blank_no, sitn.end_no_str))
        J = {"E0402": {
            "Main": {
                "HeadBan": self.turnkey_service.party_id,
                "BranchBan": self.turnkey_service.seller.legal_entity.identifier,
                "InvoiceType": self.type,
                "YearMonth": self.year_month,
                "InvoiceTrack": self.track,
            },
            "Details": Details
        }}
        return J



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
    only_fields_can_update = ['print_mark', 'ei_synced', 'ei_audited', 'generate_time']
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ei_synced = models.BooleanField(default=False, db_index=True)
    upload_to_ei_time = models.DateTimeField(null=True, db_index=True)
    ei_audited = models.BooleanField(default=False, db_index=True)
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
    @property
    def has_same_generate_no(self):
        return EInvoice.objects.filter(seller_invoice_track_no__turnkey_service__party_id=self.seller_invoice_track_no.turnkey_service.party_id,
                                       generate_no=self.generate_no).count() > 1
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
        if float(self.amounts['TotalAmount']) > self.seller_invoice_track_no.turnkey_service.warning_above_amount:
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
        elif not self.seller_invoice_track_no.can_cancel:
            return False
        else:
            return True
    @property
    def cancel_fail_reason(self):
        if self.is_canceled:
            return _("E-Invoice({}) was already canceled!").format(self.track_no_)
        elif self.is_voided and self.voideinvoice_set.filter(new_einvoice__isnull=False).exists():
            return _("E-Invoice({}) was already voieded and has created the new one!").format(self.track_no_)
        elif not self.seller_invoice_track_no.can_cancel:
            return _("It can not cancel the e-invoice({}), because of the accounting issue! Please seal the 'Cancel' mark on the original copy then transmit it to the accounter").format(self.track_no_)
        else:
            return ''
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
        return BatchEInvoice.objects.filter(content_type=ContentType.objects.get_for_model(self),
                                            object_id=self.id).order_by('id').last()
    @property
    def one_dimension_barcode_str(self):
        chmk_year = _year_to_chmk_year(self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).year)
        begin_month = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).month
        end_month = begin_month + 1
        barcode_str = "{:03d}{:02d}{}{}".format(
            chmk_year,
            end_month,
            self.track_no,
            self.random_number,
        )
        return barcode_str
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
            chmk_year = _year_to_chmk_year(self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).year)
            begin_month = self.seller_invoice_track_no.begin_time.astimezone(TAIPEI_TIMEZONE).month
            end_month = begin_month + 1
            generate_time = self.generate_time.astimezone(TAIPEI_TIMEZONE)
            sales_amount_str = _hex_amount(amounts['SalesAmount'])
            total_amount_str = _hex_amount(amounts['TotalAmount'])
            if self.seller_invoice_track_no.turnkey_service.in_production:
                test_str = ''
            else:
                test_str = '測 試 '
            tax_code = "" if LegalEntity.GENERAL_CONSUMER_IDENTIFIER == self.buyer_identifier else "格式 25"
            return [
                    {"type": "text", "custom_size": True, "width": 1, "height": 2, "align": "center", "text": test_str + "電 子 發 票 證 明 聯"},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": self.seller_invoice_track_no.year_month_range},
                    {"type": "text", "custom_size": True, "width": 2, "height": 2, "align": "center", "text": "{}-{}".format(self.track, self.no)},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": ""},
                    {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": " {} {}".format(generate_time.strftime('%Y-%m-%d %H:%M:%S'), tax_code)},
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
                            qrcode_aes_encrypt_str=qrcode_aes_encrypt(self.seller_invoice_track_no.turnkey_service.qrcode_seed, "{}{}".format(self.track_no, self.random_number)),
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
            "random_number": self.random_number,
            "generate_time": self.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S%z'),
            "width": "58mm",
            "content": EInvoice.escpos_einvoice_scripts(self.id),
        }
        _d["details_content"] = self.details_content
        return _d
    @property
    def escpos_print_scripts_for_sales_return_receipt(self):
        try:
            canceleinvoice = self.canceleinvoice_set.get(new_einvoice__isnull=True)
        except CancelEInvoice.DoesNotExist:
            _d = {}
        else:
            _d = {
                "meet_to_tw_einvoice_standard": False,
                "is_canceled": True,
                "buyer_is_business_entity": self.buyer_is_business_entity,
                "print_mark": self.print_mark,
                "id": self.id,
                "track_no": self.track_no,
                "random_number": self.random_number,
                "generate_time": canceleinvoice.generate_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S%z'),
                "width": "58mm",
                "content": canceleinvoice._escpos_sales_return_receipt_scripts,
                "details_content": [],
            }
        return _d


    @property
    def print_logs(self):
        return self.einvoiceprintlog_set.all().order_by('id')
    @property
    def print_logs_count(self):
        return self.print_logs.count()


    def __str__(self):
        return "{}".format(self.track_no)


    def in_cp_np_or_wp(self):
        if '3J0002' == self.carrier_type and LegalEntity.GENERAL_CONSUMER_IDENTIFIER != self.buyer_identifier:
            kind = 'cp'
        elif "" != self.carrier_type:
            kind = 'np'
        elif "1" == self.donate_mark:
            kind = 'np'
        else:
            kind = 'wp'
        return kind


    def post_new_track_no(self):
        lg = logging.getLogger('taiwan_einvoice')
        lg.debug('EInvoice(id:{}) post_new_track_no'.format(self.id))
        message = ""
        if hasattr(self.content_object, "post_new_track_no"):
            message = self.content_object.post_new_track_no(self)
        return message


    def renew_track_no_and_sitn_obj(self):
        turnkey_service = self.seller_invoice_track_no.turnkey_service
        sitn = ''
        no = ''
        for sitn in SellerInvoiceTrackNo.filter_now_use_sitns(turnkey_service=turnkey_service):
            new_no = sitn.get_new_no()
            if new_no:
                no = new_no
                break
        if '' == no:
            raise NotEnoughNumberError(_('Not enough numbers'))
        else:
            self.random_number = ''
            random_number = self.get_or_generate_random_number()
            EInvoice.objects.filter(id=self.id).update(
                seller_invoice_track_no=sitn,
                track=sitn.track,
                no=no,
                random_number=random_number,
                generate_time=now(),
            )
            new_track_no_self = EInvoice.objects.get(id=self.id)
            new_track_no_self.post_new_track_no()
            return new_track_no_self


    class Meta:
        unique_together = (('seller_invoice_track_no', 'track', 'no', 'reverse_void_order'), )
    


    @classmethod
    def escpos_einvoice_scripts(cls, id=0):
        _sha1 = sha1(str(id).encode('utf-8')).hexdigest()
        return "*{}*".format(_sha1)


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
        elif ("N" == J[no]["Main"]["PrintMark"]
              and LegalEntity.GENERAL_CONSUMER_IDENTIFIER != J[no]["Main"]["Buyer"]["Identifier"]
              and (self.is_voided or self.is_canceled)
             ):
              J[no]["Main"]["PrintMark"] = "Y"
        return J


    def check_before_cancel_einvoice(self):
        return self.content_object.check_before_cancel_einvoice()


    def set_generate_time(self, generate_time):
        if 'generate_time' in self.only_fields_can_update:
            EInvoice.objects.filter(id=self.id).update(generate_time=generate_time)


    def set_ei_audited_true(self):
        if 'ei_audited' in self.only_fields_can_update:
            EInvoice.objects.filter(id=self.id).update(ei_audited=True)


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
    

    def get_or_generate_random_number(self):
        if self.random_number:
            return self.random_number
        turnkey_service = self.seller_invoice_track_no.turnkey_service
        same_routeing_id_objs = self._meta.model.objects.filter(seller_invoice_track_no__turnkey_service__party_id=turnkey_service.party_id,
                                                                seller_invoice_track_no__turnkey_service__transport_id=turnkey_service.transport_id,
                                                                seller_invoice_track_no__turnkey_service__routing_id=turnkey_service.routing_id,)
        same_routeing_id_objs_count = same_routeing_id_objs.count()
        if 0 < same_routeing_id_objs_count:
            ei_synced_false_objs = same_routeing_id_objs.filter(ei_synced=False)

            _ei_synced_true_objs = same_routeing_id_objs.filter(ei_synced=True).order_by('-upload_to_ei_time')[:1000]
            if _ei_synced_true_objs.exists():
                first_ei_synced_true_obj = _ei_synced_true_objs[len(_ei_synced_true_objs)-1]
                ei_synced_true_objs = same_routeing_id_objs.filter(ei_synced=True, upload_to_ei_time__gte=first_ei_synced_true_obj.upload_to_ei_time)
            else:
                ei_synced_true_objs = same_routeing_id_objs.filter(ei_synced=True)

        while True:
            random_number = '{:04d}'.format(randint(0, 10000))
            if 0 >= same_routeing_id_objs_count or not (ei_synced_false_objs.filter(random_number=random_number).exists()
                                                        or ei_synced_true_objs.filter(random_number=random_number).exists()
                                                        or same_routeing_id_objs.filter(seller_invoice_track_no__begin_time=self.seller_invoice_track_no.begin_time,
                                                                                        track=self.track,
                                                                                        no=self.no,
                                                                                        random_number=random_number,
                                                                                       ).exists()
                ):
                break
        return random_number


    def save(self, *args, **kwargs):
        if 'upload_batch_kind' in kwargs:
            upload_batch_kind = kwargs.get('upload_batch_kind', '')
            del kwargs['upload_batch_kind']
        else:
            upload_batch_kind = ''
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
            turnkey_service = self.seller_invoice_track_no.turnkey_service
            if float(self.amounts['TotalAmount']) > turnkey_service.forbidden_above_amount:
                raise ForbiddenAboveAmountError(_("{total_amount} is bigger than Forbidden Amount({forbidden_above_amount})").format(
                    total_amount=self.amounts['TotalAmount'], forbidden_above_amount=turnkey_service.forbidden_above_amount))
            elif float(self.amounts['TotalAmount']) > turnkey_service.warning_above_amount:
                #TODO: grab staff group, and send notice mail to them.
                pass

            self.random_number = self.get_or_generate_random_number()
            self.generate_no_sha1 = sha1(self.generate_no.encode('utf-8')).hexdigest()[:10]
            super().save(*args, **kwargs)
        UploadBatch.append_to_the_upload_batch(self, upload_batch_kind=upload_batch_kind)
        


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
        base_set = self.einvoice.seller_invoice_track_no.turnkey_service.epl_base_set
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
    upload_to_ei_time = models.DateTimeField(null=True, db_index=True)
    ei_audited = models.BooleanField(default=False, db_index=True)
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
        return BatchEInvoice.objects.filter(content_type=ContentType.objects.get_for_model(self),
                                            object_id=self.id).order_by('id').last()
    @property
    def _escpos_sales_return_receipt_scripts(self):
        def _untax_amount(tax_rate, amount):
            tax_rate, amount = decimal.Decimal(tax_rate), decimal.Decimal(amount)
            if 0 == tax_rate:
                return amount
            else:
                return decimal.Decimal(round(amount / (1+tax_rate)))

        einvoice = self.einvoice
        details = einvoice.details
        amounts = einvoice.amounts
        generate_time = einvoice.generate_time.astimezone(TAIPEI_TIMEZONE)
        cancel_time = self.generate_time.astimezone(TAIPEI_TIMEZONE)
        tax_rate = amounts['TaxRate']
        tax_type = amounts['TaxType']
        total_amount = amounts['TotalAmount']
        untax_amount = _untax_amount(tax_rate, total_amount)
        tax_amount = decimal.Decimal(total_amount) - untax_amount
        if einvoice.seller_invoice_track_no.turnkey_service.in_production:
            test_str = ''
        else:
            test_str = '測 試 '
        details_list = []
        for i, d in enumerate(details):
            details_list.extend([
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "{}. {} : {} {} {}".format(
                    i+1, d['Description'], d['Quantity'], d['UnitPrice'], _untax_amount(tax_rate, d['Amount']))},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                ])

        return [
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "center", "text": test_str + "營業人銷貨退回、進貨退出或折讓證明單"},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "center", "text": cancel_time.strftime("%Y-%m-%d")},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "賣方統編：{}".format(einvoice.seller_identifier)},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "賣方名稱：{}".format(einvoice.seller_name)},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "發票開立日期：{}".format(generate_time.strftime('%Y-%m-%d'))},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 2, "height": 1, "align": "left", "bold": True, "text": "{}".format(einvoice.track_no)},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text":
                    "買方統編：{}".format("" if LegalEntity.GENERAL_CONSUMER_IDENTIFIER == einvoice.buyer_identifier else einvoice.buyer_identifier)},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text":
                    "買方名稱：{}".format("" if LegalEntity.GENERAL_CONSUMER_IDENTIFIER == einvoice.buyer_identifier else einvoice.buyer_name)},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},

                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "No. 品名 : 數量 單價 金額(不含稅之進貨額)"},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                
                *details_list,

                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "課稅別：{}".format(TAIWAN_EI_TAX_TYPES[tax_type])},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "營業稅額合計：{}".format(tax_amount)},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "金額(不含稅之進貨額)：{}".format(untax_amount)},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "合計：{}".format(total_amount)},

                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
                {"type": "text", "custom_size": True, "width": 1, "height": 1, "align": "left", "text": "簽收人："},
                {"type": "text", "custom_size": True, "width": 1, "height": 6, "align": "left", "text": " "},
            ]


    def __str__(self):
        return "{}".format(self.einvoice.track_no)


    def set_ei_audited_true(self):
        CancelEInvoice.objects.filter(id=self.id).update(ei_audited=True)


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
        elif EInvoice.objects.filter(generate_no=self.einvoice.generate_no, canceleinvoice__isnull=True).exists():
            eis = []
            for ei in EInvoice.objects.filter(generate_no=self.einvoice.generate_no, canceleinvoice__isnull=True).order_by('id'):
                if hasattr(ei.content_object, 'post_cancel_einvoice'):
                    eis.append(ei)
            if eis:
                message = self.einvoice.content_object.post_cancel_einvoice(*eis)
        return message


    def save(self, *args, **kwargs):
        self.mig_type = EInvoiceMIG.objects.get(no=self.get_mig_no())

        if kwargs.get('force_save', False):
            del kwargs['force_save']
            super().save(*args, **kwargs)
        elif not self.pk:
            super().save(*args, **kwargs)
        UploadBatch.append_to_the_upload_batch(self)


    MIG_NO_SET = {
        "C0401": "C0501",
    }
    def get_mig_no(self):
        no = self.einvoice.get_mig_no()
        mig = self.MIG_NO_SET.get(no, "")
        if not mig:
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
    upload_to_ei_time = models.DateTimeField(null=True, db_index=True)
    ei_audited = models.BooleanField(default=False, db_index=True)
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
        return "{}".format(self.einvoice.track_no)


    def set_ei_audited_true(self):
        VoidEInvoice.objects.filter(id=self.id).update(ei_audited=True)


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
        self.mig_type = EInvoiceMIG.objects.get(no=self.get_mig_no())

        if kwargs.get('force_save', False):
            del kwargs['force_save']
            super().save(*args, **kwargs)
        elif not self.pk:
            super().save(*args, **kwargs)
        UploadBatch.append_to_the_upload_batch(self)
    
    
    MIG_NO_SET = {
        "C0401": "C0701",
    }
    def get_mig_no(self):
        no = self.einvoice.get_mig_no()
        mig = self.MIG_NO_SET.get(no, "")
        if not mig:
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

        ("E",  "E0401 ~ E0501"),
        ("R",  _("Re-Created by error status")),
        ("RN", _("Re-Created by error status with the new track no.")),
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
                                    verify=self.turnkey_service.verify_tkw_ssl,
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
                   upload_to_ei_time=result_json['upload_to_ei_time'],
                   result_code=result_json['result_code'],
                   result_message=result_json['result_message'],
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
                                     verify=self.turnkey_service.verify_tkw_ssl,
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
                                     verify=self.turnkey_service.verify_tkw_ssl,
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
            eis = []
            content_object = self.batcheinvoice_set.get().content_object

        if 'wp' == self.kind and not eis.filter(print_mark=False).exists():
            self.update_to_new_status(NEXT_STATUS)
        elif ('cp' == self.kind and (not eis.filter(print_mark=False).exists()
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
                kind = content_object.in_cp_np_or_wp()
                if content_object.print_mark or "np" == kind or content_object.is_voided or content_object.is_canceled:
                    self.update_to_new_status(NEXT_STATUS)
                elif "cp" == kind and content_object.generate_time <= now() - COULD_PRINT_TIME_MARGIN:
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
        elif self.kind in ['E', 'R', 'RN']:
            self.update_to_new_status(NEXT_STATUS)

        if NEXT_STATUS != self.status and eis:
            print_mark_falsse_all_has_canceled_or_voided = True
            for _ei in eis.filter(print_mark=False):
                if not _ei.is_canceled and not _ei.is_voided:
                    print_mark_falsse_all_has_canceled_or_voided = False
                    break
            if print_mark_falsse_all_has_canceled_or_voided:
                self.update_to_new_status(NEXT_STATUS)


    @classmethod
    def append_to_the_upload_batch(cls, content_object, upload_batch_kind='', executor=None):
        ct = ContentType.objects.get_for_model(content_object)
        if hasattr(content_object, "ei_synced") and content_object.ei_synced:
            return BatchEInvoice.objects.get(content_type=ct, object_id=content_object.id, status='c').batch
        elif BatchEInvoice.objects.filter(content_type=ct, object_id=content_object.id, result_code='').exists():
            return BatchEInvoice.objects.get(content_type=ct, object_id=content_object.id, result_code='').batch

        if 'einvoice' == content_object._meta.model_name:
            mig_type = EInvoiceMIG.objects.get(no='C0401')
            _now = now().astimezone(TAIPEI_TIMEZONE)
            _s = _now.strftime('%Y-%m-%d 00:00:00+08:00')
            start_time = datetime.datetime.strptime(_s, '%Y-%m-%d %H:%M:%S%z')
            end_time = start_time + datetime.timedelta(days=1)
            if '57' == upload_batch_kind or content_object.new_einvoice_on_cancel_einvoice_set.exists() or content_object.new_einvoice_on_void_einvoice_set.exists():
                kind = '57'
            else:
                kind = content_object.in_cp_np_or_wp()

            if kind in ["wp", "cp", "np"] and UploadBatch.objects.filter(turnkey_service=content_object.seller_invoice_track_no.turnkey_service,
                                                                         mig_type=mig_type,
                                                                         kind=kind,
                                                                         status="0",
                                                                         create_time__gte=start_time, create_time__lt=end_time).exists():
                _ub = UploadBatch.objects.filter(turnkey_service=content_object.seller_invoice_track_no.turnkey_service,
                                                 mig_type=mig_type,
                                                 kind=kind,
                                                 status="0",
                                                 create_time__gte=start_time,
                                                 create_time__lt=end_time).order_by('-id')[0]
                if _ub.batcheinvoice_set.count() < 1000:
                    ub = _ub
                else:
                    ub = UploadBatch(turnkey_service=content_object.seller_invoice_track_no.turnkey_service,
                                     mig_type=mig_type,
                                     kind=kind,
                                     status='0',
                                     executor=executor,
                                    )
                    ub.save()
            else:
                ub = UploadBatch(turnkey_service=content_object.seller_invoice_track_no.turnkey_service,
                                 mig_type=mig_type,
                                 kind=kind,
                                 status='0',
                                 executor=executor,
                                )
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
            ub = UploadBatch(turnkey_service=content_object.einvoice.seller_invoice_track_no.turnkey_service,
                             slug=slug,
                             mig_type=mig_type,
                             kind=kind,
                             status='0',
                             executor=executor,
                             )
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
        elif content_object._meta.model_name in ['sellerinvoicetrackno',]:
            mig_type = EInvoiceMIG.objects.get(no='E0402')
            kind = 'E'
            slug_prefix = "{year_month}{track}{type}".format(year_month=content_object.year_month,
                                                             track=content_object.track,
                                                             type=content_object.type)
            slug = slug_prefix + "{:05d}".format(UploadBatch.objects.filter(slug__startswith=slug_prefix).count() + 1)

            ub = UploadBatch(turnkey_service=content_object.turnkey_service,
                             slug=slug,
                             mig_type=mig_type,
                             kind=kind,
                             status='0',
                             executor=executor,
                             )
            ub.save()
            be = BatchEInvoice(batch=ub,
                               content_object=content_object,
                               begin_time=content_object.begin_time,
                               end_time=content_object.end_time,
                               track_no="{}{}".format(content_object.track, content_object.begin_no_str),
                               body="",
                               )
            be.save()
            return ub
        else:
            return None


    def update_batch_einvoice_status_result_code(self, status={}, upload_to_ei_time={}, result_code={}, result_message={}):
        lg = logging.getLogger("taiwan_einvoice")
        def _update_upload_to_ei_time(self, upload_to_ei_time={}):
            bei = self.batcheinvoice_set.all()[0]
            content_model = bei.content_type.model_class()
            if SellerInvoiceTrackNo == content_model:
                return
            elif content_model not in [EInvoice, CancelEInvoice, VoidEInvoice]:
                raise BatchEInvoiceContentTypeError(_("{} not in [EInvoice, CancelEInvoice, VoidEInvoice]").format(content_model))

            exclude_ids = []
            for s, ids in upload_to_ei_time.items():
                lg.debug("UploadBatch.update_batch_einvoice_status_result_code._update_upload_to_ei_time {}: {}".format(s, ids))

                if "__else__" == s:
                    continue
                elif 'None' == s:
                    continue
                else:
                    for format in ["%Y-%m-%d %H:%M:%S.%f%z", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            upload_to_ei_time_datetime = datetime.datetime.strptime(s, format).astimezone(utc)
                        except ValueError:
                            pass
                        else:
                            break
                beis = self.batcheinvoice_set.filter(id__in=ids)
                if len(ids) != beis.count():
                    raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match batch_einvoice_ids({})".format(self, ids))
                else:
                    content_ids = BatchEInvoice.objects.filter(id__in=ids,
                                                              ).values_list('object_id',
                                                                            named=False,
                                                                            flat=True)
                    lg.debug("_update_upload_to_ei_time {} content_ids: {}".format(s, content_ids))
                    content_model.objects.filter(ei_synced=True, id__in=content_ids).update(upload_to_ei_time=upload_to_ei_time_datetime)
                exclude_ids.extend(ids)
            
            if "None" != upload_to_ei_time.get('__else__', "None"):
                beis = self.batcheinvoice_set.exclude(id__in=exclude_ids)
                if beis.count() != self.batcheinvoice_set.count() - len(exclude_ids):
                    raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match excluding batch_einvoice_ids({})".format(self, ids))
                else:
                    for format in ["%Y-%m-%d %H:%M:%S.%f%z", "%Y-%m-%d %H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]:
                        try:
                            upload_to_ei_time_datetime = datetime.datetime.strptime(upload_to_ei_time['__else__'], format).astimezone(utc)
                        except ValueError:
                            pass
                        else:
                            break
                    content_ids = self.batcheinvoice_set.exclude(id__in=exclude_ids
                                                                ).values_list('object_id',
                                                                            named=False,
                                                                            flat=True)
                    lg.debug("_update_upload_to_ei_time {} content_ids: {}".format(upload_to_ei_time['__else__'], content_ids))
                    content_model.objects.filter(ei_synced=True, id__in=content_ids).update(upload_to_ei_time=upload_to_ei_time_datetime)

        for rc, ids in result_code.items():
            beis = self.batcheinvoice_set.filter(id__in=ids)
            if len(ids) != beis.count():
                raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match batch_einvoice_ids({})".format(self, ids))
            else:
                beis.update(result_code=rc)

        for rc, ids in result_message.items():
            beis = self.batcheinvoice_set.filter(id__in=ids)
            if len(ids) != beis.count():
                raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match batch_einvoice_ids({})".format(self, ids))
            else:
                beis.update(result_message=rc)
        
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
            beis = self.batcheinvoice_set.filter(id__in=ids)
            if len(ids) != beis.count():
                raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match batch_einvoice_ids({})".format(self, ids))
            else:
                beis.update(status=s)
                if 'c' == s and not ids_in_c:
                    ids_in_c = ids

            exclude_ids.extend(ids)
            if s not in finish_status:
                is_finish = False
        beis = self.batcheinvoice_set.exclude(id__in=exclude_ids)
        if beis.count() != self.batcheinvoice_set.count() - len(exclude_ids):
            raise BatchEInvoiceIDsError("BatchEInvoice objects of {} do not match excluding batch_einvoice_ids({})".format(self, ids))
        else:
            beis.update(status=status['__else__'])
            if 'c' == status['__else__']:
                ids_in_c = beis.values_list('id', named=False, flat=True)

        if ids_in_c:
            bei = self.batcheinvoice_set.get(id=ids_in_c[0])
            content_model = bei.content_type.model_class()
            if content_model in [EInvoice, CancelEInvoice, VoidEInvoice]:
                content_ids = BatchEInvoice.objects.filter(id__in=ids_in_c
                                                          ).values_list('object_id',
                                                                        named=False,
                                                                        flat=True)
                lg.debug("content_ids: {}".format(content_ids))
                content_model.objects.filter(id__in=content_ids).update(ei_synced=True)

        _update_upload_to_ei_time(self, upload_to_ei_time)

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
Result message: "{result_message}"
            """).format(status=error_bei.status, result_code=error_bei.result_code, result_message=error_bei.result_message)

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


    def generate_slug(self, be_called_in_while=0):
        if self.slug:
            return self.slug
        _now = now().astimezone(TAIPEI_TIMEZONE)
        _s = _now.strftime('%Y-%m-%d 00:00:00+08:00')
        start_time = datetime.datetime.strptime(_s, '%Y-%m-%d %H:%M:%S%z')
        end_time = start_time + datetime.timedelta(days=1)
        _no = UploadBatch.objects.filter(create_time__gte=start_time, create_time__lt=end_time).count() + 1
        no = '{:04d}'.format(_no)
        slug1 = '{}{}'.format(no, get_codes(_no, seed=int(_now.strftime('%y%m%d')+no)))
        _t = math.ceil(be_called_in_while / len(KEY_CODE_SET))
        if _t > 1:
            slug2 = ''
            for dev_null in range(_t):
                slug2 += '{}'.format(choice(KEY_CODE_SET))
        else:
            slug2 = '{}'.format(choice(KEY_CODE_SET))
        return "{}{}".format(slug1, slug2)
        

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_slug()
        _i = 0
        while True:
            try:
                super().save(*args, **kwargs)
            except IntegrityError:
                _i += 1
                self.slug = self.generate_slug(be_called_in_while=_i)
            else:
                break



class BatchEInvoice(models.Model):
    batch = models.ForeignKey(UploadBatch, on_delete=models.DO_NOTHING)
    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField(default=0)
    content_object = GenericForeignKey('content_type', 'object_id')
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    @property
    def year_month_range(self):
        chmk_year = _year_to_chmk_year(self.begin_time.astimezone(TAIPEI_TIMEZONE).year)
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
    result_message = models.TextField(default='')
    handling_note = models.CharField(max_length=200, default='')
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
        ("EI_SUMMARY_RESULT", "EI Summary Result"),
        ("E0501_INVOICE_ASSIGN_NO", "E0501(Invoice Assign No)"),
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



def _dict_value_plus_1(dictionary, key):
    if key in dictionary: dictionary[key] += 1
    else: dictionary[key] = 1



class SummaryReport(models.Model):
    LAST_BATCH_EINVOICE_DOES_NOT_EXIST_MESSAGE = _("The last Batch E-Invoice does not exist!")
    NOT_MATCH_BETWEEN_SUMMARY_RESULT_AND_BATCH_EINVOICE_MESSAGE = _("The ids in Summary Result do not match BatchEInvoice!")
    EI_SUMMARY_RESULT_RETIRN_FAILED_MESSAGE = _("EI Daily Summary Result report it as failed record!")

    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    turnkey_service = models.ForeignKey(TurnkeyService, on_delete=models.DO_NOTHING)
    begin_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    report_type_choices = (
        ("h", _("Hourly Sync")),
        ("d", _("Daily Sync")),
        ("w", _("Weekly Sync")),
        ("m", _("Monthly Sync")),
        ("o", _("Odd month ~ Even month Sync")),
        ("y", _("Yearly Sync")),
        ("a", _("Daily Audit")),
        ("E", _("Daily Summary from EI")),
    )
    report_type = models.CharField(max_length=1, choices=report_type_choices, db_index=True)
    problems = models.JSONField(default={})

    good_count = models.SmallIntegerField(default=0)
    failed_count = models.SmallIntegerField(default=0)
    resolved_count = models.SmallIntegerField(default=0)

    good_counts = models.JSONField(default={})
    failed_counts = models.JSONField(default={})
    resolved_counts = models.JSONField(default={})

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
        if "a" == report_type:
            ei_check_type = 'ei_audited'
        else:
            ei_check_type = 'ei_synced'
        model_objects = [EInvoice.objects.filter(seller_invoice_track_no__turnkey_service=turnkey_service, 
                                                 create_time__gte=begin_time,
                                                 create_time__lt=end_time).order_by('id'),
                         CancelEInvoice.objects.filter(einvoice__seller_invoice_track_no__turnkey_service=turnkey_service,
                                                       create_time__gte=begin_time,
                                                       create_time__lt=end_time).order_by('id'),
                         VoidEInvoice.objects.filter(einvoice__seller_invoice_track_no__turnkey_service=turnkey_service,
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

        vars_list_for_ei_check_type_true_false = {True: {
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
                for ture_or_false, _vars in vars_list_for_ei_check_type_true_false.items():
                    for m in mos.filter(**{ei_check_type: ture_or_false}):
                        _vars["count_var"] += 1
                        _dict_value_plus_1(_vars["counts_var"], m.get_mig_no())
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
                            problems.setdefault(problem_key, []).append(str(summary_report.LAST_BATCH_EINVOICE_DOES_NOT_EXIST_MESSAGE))
                        _vars["objects_list"].append(last_einvoices_content_type)
            good_count = vars_list_for_ei_check_type_true_false[True]["count_var"]
            failed_count = vars_list_for_ei_check_type_true_false[False]["count_var"]
            if 0 >= good_count + failed_count:
                return None
            summary_report.problems = problems
            summary_report.good_count = good_count
            summary_report.good_counts = vars_list_for_ei_check_type_true_false[True]["counts_var"]
            summary_report.resolved_count = resolved_count
            summary_report.failed_count = failed_count
            summary_report.failed_counts = vars_list_for_ei_check_type_true_false[False]["counts_var"]
            summary_report.resolved_counts = resolved_counts
            summary_report.save()
            summary_report.good_objects.add(*vars_list_for_ei_check_type_true_false[True]["objects_list"])
            if vars_list_for_ei_check_type_true_false[False]["objects_list"]:
                summary_report.failed_objects.add(*vars_list_for_ei_check_type_true_false[False]["objects_list"])
            summary_report.notice(new_creation=True)
        else:
            for eict in summary_report.failed_objects.all():
                if getattr(eict.content_object, ei_check_type):
                    resolved_count += 1
                    _dict_value_plus_1(resolved_counts, eict.content_object.get_mig_no())
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
            "d": datetime.timedelta(hours=24 + 11),
            "a": datetime.timedelta(hours=24 + 11),
            "w": datetime.timedelta(hours=24 * 7 + 11),
            "m": datetime.timedelta(hours=24 * 31 + 11),
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
                elif "a" == report_type:
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(_Y, _m, _d, 0, 0, 0)) - datetime.timedelta(hours=24)
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
            if "h" == self.report_type and last_batch_einvoice and "wp" == last_batch_einvoice.batch.kind:
                _h_msg = ''
                if True == failed_einvoice_ct.content_object.print_mark:
                    if not failed_einvoice_ct.content_object.upload_to_ei_time:
                        _h_msg = _("Please notice the E-Invoice({track_no}), it does not be synced to EI yet")
                else:
                    _h_msg = _("Please print the E-Invoice({track_no}) as soon as possible, so that the system can sync this E-Invoice to EI")
                if _h_msg:
                    target_audience_types.setdefault("g", {})[fe_key] = str(_h_msg.format(track_no=track_no))
            elif "a" == self.report_type:
                target_audience_types.setdefault("p", {})[fe_key] = str(self.EI_SUMMARY_RESULT_RETIRN_FAILED_MESSAGE)
            elif not last_batch_einvoice:
                target_audience_types.setdefault("p", {})[fe_key] = str(self.LAST_BATCH_EINVOICE_DOES_NOT_EXIST_MESSAGE)
            elif last_batch_einvoice and last_batch_einvoice.batch.kind in ["cp", "np"]:
                target_audience_types.setdefault("p", {})[fe_key] = str(_("Please check taiwan_einvoice.crontabs.polling_upload_batch for the E-Invoice({track_no})").format(track_no=track_no))
            else:
                target_audience_types.setdefault("p", {})[fe_key] = str(_("The {track_no}@{mig_no} has result_code: {status}: '{result_code}'").format(
                    track_no=track_no,
                    mig_no=mig_no,
                    status=last_batch_einvoice.status,
                    result_code=last_batch_einvoice.result_code,
                ))
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
            title = _("Failed-{ei_check_type} E-Invoice(s) in {name} summary report({report_type}@{begin_time}) for {target_audience}").format(
                ei_check_type=_("Audit") if "a" == self.report_type else _("Sync"),
                name=self.turnkey_service.name,
                report_type=self.get_report_type_display(),
                begin_time=self.begin_time.astimezone(TAIPEI_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
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


    def generate_ei_daily_summary_report(self, summary_result):
        sr = self
        problems = sr.problems
        for k in ["total_count", "good_count", "failed_count"]:
            setattr(sr, k, summary_result[k])
        field_d = {
            "good_batch_einvoice_ids": "good_objects",
            "failed_batch_einvoice_ids": "failed_objects",
        }
        for tk in ["good_batch_einvoice_ids", "failed_batch_einvoice_ids"]:
            beis = BatchEInvoice.objects.filter(id__in=summary_result[tk])
            if beis.count() != summary_result[tk]:
                if tk in problems:
                    problems[tk].append(str(sr.NOT_MATCH_BETWEEN_SUMMARY_RESULT_AND_BATCH_EINVOICE_MESSAGE))
                else:
                    problems[tk] = [str(sr.NOT_MATCH_BETWEEN_SUMMARY_RESULT_AND_BATCH_EINVOICE_MESSAGE)]
            einvoices_content_types = [_bei.last_einvoices_content_type for _bei in beis]
            remove_ects = []
            for _ect in getattr(sr, field_d[tk]).all():
                if _ect not in einvoices_content_types:
                    remove_ects.append(_ect)
            add_ects = []
            for _ect in einvoices_content_types:
                if not getattr(sr, field_d[tk]).filter(id=_ect.id).exists():
                    add_ects.append(_ect)
            if remove_ects:
                getattr(sr, field_d[tk]).remove(*remove_ects)
                for _ect in remove_ects:
                    _ect.content_object.ei_audited = False
                    _ect.content_object.save()
            if add_ects:
                getattr(sr, field_d[tk]).add(*add_ects)
                if "good_batch_einvoice_ids" == tk:
                    for _ect in add_ects:
                        _ect.content_object.set_ei_audited_true()
        sr.problems = problems
        good_counts = {}
        for good_object in sr.good_objects.all():
            _dict_value_plus_1(good_counts, good_object.content_object.get_mig_no())
        failed_counts = {}
        for failed_object in sr.failed_objects.all():
            _dict_value_plus_1(failed_counts, failed_object.content_object.get_mig_no())
        sr.good_counts = good_counts
        sr.failed_counts = failed_counts
        if not sr.problems and sr.failed_count <= 0:
            sr.is_resolved = True
        sr.save()
        sr.notice()
        


class E0501InvoiceAssignNo(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    type = models.CharField(max_length=2, default='07', choices=SellerInvoiceTrackNo.type_choices, db_index=True)
    year_month = models.CharField(max_length=5, db_index=True)
    track = models.CharField(max_length=2, db_index=True)
    begin_no = models.CharField(max_length=8, db_index=True)
    end_no = models.CharField(max_length=8, db_index=True)
    booklet = models.SmallIntegerField(default=0)


    
    class Meta:
        unique_together = (("identifier", "type", "year_month", "track", "begin_no", "end_no", ), )