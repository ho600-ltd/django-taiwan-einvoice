import os, re, logging, datetime, pathlib, shutil, glob, pytz, xmltodict, zlib
from xmlrpc.client import Boolean
from json2xml import json2xml
from django.db import models
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

from taiwan_einvoice.libs import CounterBasedOTPinRow
from taiwan_einvoice.turnkey import TurnkeyWebReturnCode


TAIPEI_TIMEZONE = pytz.timezone('Asia/Taipei')
EITurnkeyBatchEInvoice_CAN_NOT_DUPLICATES_EXIST_IN_STATUSS = ["G", "C"]
EI_WELL_STATUSS = ["P", "G", "C"]
EI_STATUSS = ["C", "G", "P", "E", "I"]
MIG_NOS = ["C0401", "C0501", "C0701", "F0401", "F0501", "F0701"]
XML_VERSION_RE = re.compile('<\?xml +version=[\'"][0-9\.]+[\'"][^>]+>', re.I)
WILL_REMOVE_DFAJDLFZX_RE = re.compile('</?will_remove_dfajdlfzx>', re.I)



class MIGConfigurationError(Exception):
    pass



class EITurnkeyConfigurationError(Exception):
    pass



class C0401JSON2MIGXMl(object):
    versions = ["3.2"]
    base_xml = """<Invoice xmlns="urn:GEINV:eInvoiceMessage:C0401:{version}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:C0401:{version} C0401.xsd">
    {xml_body}
</Invoice>"""


    def __init__(self, json_data, version="3.2"):
        if version not in self.versions:
            raise Exception("Only accept version number: {}".format(", ".join(self.versions)))
        self.version = version
        self.json_data = self.regulate_json_data(json_data)
    

    def export_xml(self):
        return self.base_xml.format(version=self.version, xml_body=self.get_xml_body())

    
    def regulate_json_data(self, json_data):
        def _append_sequence_number(index0, d):
            d["SequenceNumber"] = "{:03d}".format(index0+1)
            return d
        json_data["Details"] = [{"ProductItem": _append_sequence_number(_i, _pi)}
            for _i, _pi in enumerate(json_data["Details"])
        ]

        if "FreeTaxSalesAmount" not in json_data["Amount"]:
            json_data["Amount"]["FreeTaxSalesAmount"] = '0'
        if "ZeroTaxSalesAmount" not in json_data["Amount"]:
            json_data["Amount"]["ZeroTaxSalesAmount"] = '0'
        return json_data
    

    def get_xml_body(self):
        xml_body = ''
        for elm in ["Main", "Details", "Amount"]:
            xml = json2xml.Json2xml(self.json_data[elm], wrapper=elm, pretty=False, item_wrap=False, attr_type=False).to_xml()
            xml_body += XML_VERSION_RE.sub("", xml.decode('utf-8'))
        return xml_body



class C0501JSON2MIGXMl(C0401JSON2MIGXMl):
    base_xml = """<CancelInvoice xmlns="urn:GEINV:eInvoiceMessage:C0501:{version}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:C0501:{version} C0501.xsd">
    {xml_body}
</CancelInvoice>"""


    def __init__(self, json_data, version="3.2"):
        super().__init__(json_data, version=version)


    def export_xml(self):
        return super().export_xml()


    def regulate_json_data(self, json_data):
        return json_data


    def get_xml_body(self):
        remove_elm = "will_remove_dfajdlfzx"
        _xml_body = json2xml.Json2xml(self.json_data, wrapper=remove_elm, pretty=False, item_wrap=False, attr_type=False).to_xml()
        _xml_body = XML_VERSION_RE.sub("", _xml_body.decode('utf-8'))
        xml_body = WILL_REMOVE_DFAJDLFZX_RE.sub("", _xml_body)
        return xml_body



class C0701JSON2MIGXMl(C0501JSON2MIGXMl):
    base_xml = """<VoidInvoice xmlns="urn:GEINV:eInvoiceMessage:C0701:{version}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:C0701:{version} C0701.xsd">
    {xml_body}
</VoidInvoice>"""


class E0402JSON2MIGXMl(object):
    versions = ["4.0"]
    base_xml = """<BranchTrackBlank xmlns="urn:GEINV:eInvoiceMessage:E0402:{version}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:E0402:{version} E0402.xsd">
    {xml_body}
</BranchTrackBlank>"""


    def __init__(self, json_data, version="4.0"):
        if version not in self.versions:
            raise Exception("Only accept version number: {}".format(", ".join(self.versions)))
        self.version = version
        self.json_data = self.regulate_json_data(json_data)
    

    def export_xml(self):
        return self.base_xml.format(version=self.version, xml_body=self.get_xml_body())

    
    def regulate_json_data(self, json_data):
        data = {}
        data["Main"] = json_data["Main"]
        data["Details"] = [{"BranchTrackBlankItem": {"InvoiceBeginNo": d[0],
                                                     "InvoiceEndNo": d[1]}
                           } for d in json_data["Details"] ]
        return data
    

    def get_xml_body(self):
        xml_body = ''
        for elm in ["Main", "Details"]:
            xml = json2xml.Json2xml(self.json_data[elm], wrapper=elm, pretty=False, item_wrap=False, attr_type=False).to_xml()
            xml_body += XML_VERSION_RE.sub("", xml.decode('utf-8'))
        return xml_body





class FROM_CONFIG(models.Model):
    TRANSPORT_ID = models.CharField(db_column='TRANSPORT_ID', max_length=10, blank=True, null=True)
    TRANSPORT_PASSWORD = models.CharField(db_column='TRANSPORT_PASSWORD', max_length=45, blank=True, null=True)
    PARTY_ID = models.CharField(db_column='PARTY_ID', primary_key=True, max_length=10)
    PARTY_DESCRIPTION = models.CharField(db_column='PARTY_DESCRIPTION', max_length=200, blank=True, null=True)
    ROUTING_ID = models.CharField(db_column='ROUTING_ID', max_length=39, blank=True, null=True)
    ROUTING_DESCRIPTION = models.CharField(db_column='ROUTING_DESCRIPTION', max_length=200, blank=True, null=True)
    SIGN_ID = models.CharField(db_column='SIGN_ID', max_length=4, blank=True, null=True)
    SUBSTITUTE_PARTY_ID = models.CharField(db_column='SUBSTITUTE_PARTY_ID', max_length=10, blank=True, null=True, db_index=True)

    def __str__(self):
        return "{}-{}".format(self.PARTY_ID, self.ROUTING_ID)

    class Meta:
        managed = False
        verbose_name = 'FROM_CONFIG'
        verbose_name_plural = 'FROM_CONFIG'
        db_table = 'FROM_CONFIG_V'


class SCHEDULE_CONFIG(models.Model):
    TASK = models.CharField(db_column='TASK', primary_key=True, max_length=30)
    ENABLE = models.CharField(db_column='ENABLE', max_length=1, blank=True, null=True)
    SCHEDULE_TYPE = models.CharField(db_column='SCHEDULE_TYPE', max_length=10, blank=True, null=True)
    SCHEDULE_WEEK = models.CharField(db_column='SCHEDULE_WEEK', max_length=15, blank=True, null=True)
    SCHEDULE_TIME = models.CharField(db_column='SCHEDULE_TIME', max_length=50, blank=True, null=True)
    SCHEDULE_PERIOD = models.CharField(db_column='SCHEDULE_PERIOD', max_length=10, blank=True, null=True)
    SCHEDULE_RANGE = models.CharField(db_column='SCHEDULE_RANGE', max_length=15, blank=True, null=True)

    def __str__(self):
        return "{}-{}".format(self.TASK, self.ENABLE)


    class Meta:
        managed = False
        verbose_name = 'SCHEDULE_CONFIG'
        verbose_name_plural = 'SCHEDULE_CONFIG'
        db_table = 'SCHEDULE_CONFIG_V'


class SIGN_CONFIG(models.Model):
    SIGN_ID = models.CharField(db_column='SIGN_ID', primary_key=True, max_length=4)
    SIGN_TYPE = models.CharField(db_column='SIGN_TYPE', max_length=10, blank=True, null=True)
    PFX_PATH = models.CharField(db_column='PFX_PATH', max_length=100, blank=True, null=True)
    SIGN_PASSWORD = models.CharField(db_column='SIGN_PASSWORD', max_length=60, blank=True, null=True)


    def __str__(self):
        return "{}-{}".format(self.SIGN_ID, self.SIGN_TYPE)


    class Meta:
        managed = False
        verbose_name = 'SIGN_CONFIG'
        verbose_name_plural = 'SIGN_CONFIG'
        db_table = 'SIGN_CONFIG_V'


class TASK_CONFIG(models.Model):
    CATEGORY_TYPE_CATEGORY_TYPE_TASK = models.CharField(db_column='CATEGORY_TYPE_CATEGORY_TYPE_TASK', primary_key=True, max_length=47)
    CATEGORY_TYPE = models.CharField(db_column='CATEGORY_TYPE', max_length=5, null=False)
    PROCESS_TYPE = models.CharField(db_column='PROCESS_TYPE', max_length=10, null=False)
    TASK = models.CharField(db_column='TASK', max_length=30, null=False)
    SRC_PATH = models.CharField(db_column='SRC_PATH', max_length=200, blank=True, null=True)
    TARGET_PATH = models.CharField(db_column='TARGET_PATH', max_length=200, blank=True, null=True)
    FILE_FORMAT = models.CharField(db_column='FILE_FORMAT', max_length=20, blank=True, null=True)
    VERSION = models.CharField(db_column='VERSION', max_length=5, blank=True, null=True)
    ENCODING = models.CharField(db_column='ENCODING', max_length=15, blank=True, null=True)
    TRANS_CHINESE_DATE = models.CharField(db_column='TRANS_CHINESE_DATE', max_length=1, blank=True, null=True)


    def __str__(self):
        return self.CATEGORY_TYPE_CATEGORY_TYPE_TASK


    class Meta:
        managed = False
        verbose_name = 'TASK_CONFIG'
        verbose_name_plural = 'TASK_CONFIG'
        db_table = 'TASK_CONFIG_V'
        unique_together = (('CATEGORY_TYPE', 'PROCESS_TYPE', 'TASK'),)


class TO_CONFIG(models.Model):
    FROM_PARTY_ID_PARTY_ID = models.CharField(db_column='FROM_PARTY_ID_PARTY_ID', primary_key=True, max_length=21)
    PARTY_ID = models.CharField(db_column='PARTY_ID', max_length=10, null=False)
    PARTY_DESCRIPTION = models.CharField(db_column='PARTY_DESCRIPTION', max_length=200, blank=True, null=True)
    ROUTING_ID = models.CharField(db_column='ROUTING_ID', max_length=39, blank=True, null=True)
    ROUTING_DESCRIPTION = models.CharField(db_column='ROUTING_DESCRIPTION', max_length=200, blank=True, null=True)
    FROM_PARTY_ID = models.CharField(db_column='FROM_PARTY_ID', max_length=10)


    def __str__(self):
        return self.FROM_PARTY_ID_PARTY_ID


    class Meta:
        managed = False
        verbose_name = 'TO_CONFIG'
        verbose_name_plural = 'TO_CONFIG'
        db_table = 'TO_CONFIG_V'
        unique_together = (('FROM_PARTY_ID', 'PARTY_ID'),)


class TURNKEY_MESSAGE_LOG(models.Model):
    SEQNO_SUBSEQNO = models.CharField(db_column='SEQNO_SUBSEQNO', primary_key=True, max_length=14)
    SEQNO = models.CharField(db_column='SEQNO', max_length=8)
    SUBSEQNO = models.CharField(db_column='SUBSEQNO', max_length=5)
    UUID = models.CharField(db_column='UUID', max_length=40, blank=True, null=True, db_index=True)
    MESSAGE_TYPE = models.CharField(db_column='MESSAGE_TYPE', max_length=10, blank=True, null=True)
    CATEGORY_TYPE = models.CharField(db_column='CATEGORY_TYPE', max_length=5, blank=True, null=True)
    PROCESS_TYPE = models.CharField(db_column='PROCESS_TYPE', max_length=10, blank=True, null=True)
    FROM_PARTY_ID = models.CharField(db_column='FROM_PARTY_ID', max_length=10, blank=True, null=True)
    TO_PARTY_ID = models.CharField(db_column='TO_PARTY_ID', max_length=10, blank=True, null=True)
    MESSAGE_DTS = models.CharField(db_column='MESSAGE_DTS', max_length=17, blank=True, null=True, db_index=True)
    @property
    def MESSAGE_DTS_datetime(self):
        return TAIPEI_TIMEZONE.localize(datetime.datetime.strptime("{}000".format(self.MESSAGE_DTS), "%Y%m%d%H%M%S%f"))
    CHARACTER_COUNT = models.CharField(db_column='CHARACTER_COUNT', max_length=10, blank=True, null=True)
    STATUS = models.CharField(db_column='STATUS', max_length=5, blank=True, null=True)
    IN_OUT_BOUND = models.CharField(db_column='IN_OUT_BOUND', max_length=1, blank=True, null=True)
    FROM_ROUTING_ID = models.CharField(db_column='FROM_ROUTING_ID', max_length=39, blank=True, null=True)
    TO_ROUTING_ID = models.CharField(db_column='TO_ROUTING_ID', max_length=39, blank=True, null=True)
    INVOICE_IDENTIFIER = models.CharField(db_column='INVOICE_IDENTIFIER', max_length=30, blank=True, null=True)

    def __str__(self):
        return self.SEQNO_SUBSEQNO


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_MESSAGE_LOG'
        verbose_name_plural = 'TURNKEY_MESSAGE_LOG'
        db_table = 'TURNKEY_MESSAGE_LOG_V'
        unique_together = (('SEQNO', 'SUBSEQNO'),)


    def get_TURNKEY_SYSEVENT_LOG__MESSAGES(self):
        tsl = TURNKEY_SYSEVENT_LOG.objects.filter(EVENTDTS__gte=self.MESSAGE_DTS
                                                 ).filter(Q(UUID=self.UUID)
                                                          |Q(SEQNO=self.SEQNO, SUBSEQNO=self.SUBSEQNO)
                                                         ).order_by('EVENTDTS').first()
        if tsl:
            message = tsl.MESSAGE
            code = tsl.ERRORCODE
            code_re = re.search('(E[0-9]{4})\\b', message)
            if code_re:
                code = code_re.groups()[0]
            elif '-007' == tsl.ERRORCODE:
                code_re = re.search('\\b([579][0-9]{3}|6[0-9]{4})\\b', message)
                if code_re:
                    code = code_re.groups()[0]
        else:
            code = ''
            message = ''
        return code, message



class TURNKEY_MESSAGE_LOG_DETAIL(models.Model):
    SEQNO_SUBSEQNO_TASK = models.CharField(db_column='SEQNO_SUBSEQNO_TASK', primary_key=True, max_length=45)
    SEQNO = models.CharField(db_column='SEQNO', max_length=8)
    SUBSEQNO = models.CharField(db_column='SUBSEQNO', max_length=5)
    PROCESS_DTS = models.CharField(db_column='PROCESS_DTS', max_length=17, blank=True, null=True)
    @property
    def PROCESS_DTS_datetime(self):
        return TAIPEI_TIMEZONE.localize(datetime.datetime.strptime("{}000".format(self.PROCESS_DTS), "%Y%m%d%H%M%S%f"))
    TASK = models.CharField(db_column='TASK', max_length=30)
    STATUS = models.CharField(db_column='STATUS', max_length=5, blank=True, null=True)
    FILENAME = models.CharField(db_column='FILENAME', max_length=300, blank=True, null=True, db_index=True)
    UUID = models.CharField(db_column='UUID', max_length=40, blank=True, null=True)
    @property
    def fileformat(self):
        if self.FILENAME.endswith('.xml') or "Unpack" == self.TASK:
            return 'xml'
        else:
            return 'plain'
    def __str__(self):
        return self.SEQNO_SUBSEQNO_TASK


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_MESSAGE_LOG_DETAIL'
        verbose_name_plural = 'TURNKEY_MESSAGE_LOG_DETAIL'
        db_table = 'TURNKEY_MESSAGE_LOG_DETAIL_V'
        unique_together = (('SEQNO', 'SUBSEQNO', 'TASK'),)


class TURNKEY_SEQUENCE(models.Model):
    SEQUENCE = models.CharField(db_column='SEQUENCE', primary_key=True, max_length=8)

    def __str__(self):
        return self.SEQUENCE


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_SEQUENCE'
        verbose_name_plural = 'TURNKEY_SEQUENCE'
        db_table = 'TURNKEY_SEQUENCE_V'


class TURNKEY_SYSEVENT_LOG(models.Model):
    EVENTDTS = models.CharField(db_column='EVENTDTS', primary_key=True, max_length=17)
    PARTY_ID = models.CharField(db_column='PARTY_ID', max_length=10, blank=True, null=True)
    SEQNO = models.CharField(db_column='SEQNO', max_length=8, blank=True, null=True)
    SUBSEQNO = models.CharField(db_column='SUBSEQNO', max_length=5, blank=True, null=True)
    ERRORCODE = models.CharField(db_column='ERRORCODE', max_length=4, blank=True, null=True)
    UUID = models.CharField(db_column='UUID', max_length=40, blank=True, null=True, db_index=True)
    INFORMATION1 = models.CharField(db_column='INFORMATION1', max_length=100, blank=True, null=True)
    INFORMATION2 = models.CharField(db_column='INFORMATION2', max_length=100, blank=True, null=True)
    INFORMATION3 = models.CharField(db_column='INFORMATION3', max_length=100, blank=True, null=True)
    MESSAGE1 = models.CharField(db_column='MESSAGE1', max_length=100, blank=True, null=True)
    MESSAGE2 = models.CharField(db_column='MESSAGE2', max_length=100, blank=True, null=True)
    MESSAGE3 = models.CharField(db_column='MESSAGE3', max_length=100, blank=True, null=True)
    MESSAGE4 = models.CharField(db_column='MESSAGE4', max_length=100, blank=True, null=True)
    MESSAGE5 = models.CharField(db_column='MESSAGE5', max_length=100, blank=True, null=True)
    MESSAGE6 = models.CharField(db_column='MESSAGE6', max_length=100, blank=True, null=True)
    @property
    def MESSAGE(self):
        return "{}{}{}{}{}{}".format(
            self.MESSAGE1,
            self.MESSAGE2,
            self.MESSAGE3,
            self.MESSAGE4,
            self.MESSAGE5,
            self.MESSAGE6,
        )

    def __str__(self):
        return "{}-{}".format(self.SEQNO, self.SUBSEQNO)


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_SYSEVENT_LOG'
        verbose_name_plural = 'TURNKEY_SYSEVENT_LOG'
        db_table = 'TURNKEY_SYSEVENT_LOG_V'
        index_together = (("SEQNO", "SUBSEQNO"),)


class TURNKEY_TRANSPORT_CONFIG(models.Model):
    TRANSPORT_ID = models.CharField(db_column='TRANSPORT_ID', primary_key=True, max_length=10)
    TRANSPORT_PASSWORD = models.CharField(db_column='TRANSPORT_PASSWORD', max_length=60)

    def __str__(self):
        return self.TRANSPORT_ID


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_TRANSPORT_CONFIG'
        verbose_name_plural = 'TURNKEY_TRANSPORT_CONFIG'
        db_table = 'TURNKEY_TRANSPORT_CONFIG_V'


class TURNKEY_USER_PROFILE(models.Model):
    USER_ID = models.CharField(db_column='USER_ID', primary_key=True, max_length=10)
    USER_PASSWORD = models.CharField(db_column='USER_PASSWORD', max_length=100, blank=True, null=True)
    @property
    def mask_USER_PASSWORD(self):
        return self.USER_PASSWORD[:1] + '********************************' + self.USER_PASSWORD[-1:]
    USER_ROLE = models.CharField(db_column='USER_ROLE', max_length=2, blank=True, null=True)

    def __str__(self):
        return self.USER_ID


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_USER_PROFILE'
        verbose_name_plural = 'TURNKEY_USER_PROFILE'
        db_table = 'TURNKEY_USER_PROFILE_V'



class EITurnkey(models.Model):
    can_sync_to_ei = models.BooleanField(default=False)
    tmpdata_abspath = models.CharField(max_length=755)
    data_abspath = models.CharField(max_length=755)
    hash_key = models.CharField(max_length=40)
    transport_id = models.CharField(max_length=10)
    party_id = models.CharField(max_length=10)
    routing_id = models.CharField(max_length=39)
    tea_turnkey_service_endpoint = models.CharField(max_length=755)
    allow_ips = models.JSONField(null=True)
    endpoint = models.CharField(max_length=755, null=True)


    @classmethod
    def parse_summary_result_then_create_objects(cls):
        lg = logging.getLogger("turnkey_web")
        paths = []
        eitdsrxmls = []
        for ei_turnkey in cls.objects.all().order_by('routing_id'):
            if ei_turnkey.SummaryResultUnpackBAK not in paths:
                paths.append(ei_turnkey.SummaryResultUnpackBAK)
        _filepaths = []
        for path in paths:
            _filepaths.extend(glob.glob(os.path.join(path, "*", "*", "*")))
        lg.debug("_filepaths: {}".format(_filepaths))
        exclude_filepaths = EITurnkeyDailySummaryResultXML.objects.filter(abspath__in=_filepaths, is_parsed=True).values_list('abspath', flat=True)
        lg.debug("exclude_filepaths: {}".format(exclude_filepaths))
        filepaths = []
        for _fp in _filepaths:
            if _fp not in filepaths and _fp not in exclude_filepaths:
                filepaths.append(_fp)
        lg.debug("filepaths: {}".format(filepaths))
        if filepaths:
            for filepath in filepaths:
                if EITurnkeyDailySummaryResultXML.objects.filter(abspath=filepath, is_parsed=True).exists():
                    continue
                content = open(filepath, 'r').read()
                if 'SummaryResult xmlns' not in content:
                    _eitdsrxml = EITurnkeyDailySummaryResultXML(abspath=filepath, is_parsed=True)
                    _eitdsrxml.save()
                    continue
                lg.debug(filepath)
                try:
                    eitdsrxml = EITurnkeyDailySummaryResultXML.objects.get(abspath=filepath)
                except EITurnkeyDailySummaryResultXML.DoesNotExist:
                    eitdsrxml = EITurnkeyDailySummaryResultXML(abspath=filepath)
                eitdsrxml.content = content
                eitdsrxml.save()
                eitdsrxmls.append(eitdsrxml)
        return eitdsrxmls


    @classmethod
    def parse_E0501_then_create_objects(cls):
        lg = logging.getLogger("turnkey_web")
        paths = []
        eitE0501xmls = []
        for ei_turnkey in cls.objects.all().order_by('routing_id'):
            if ei_turnkey.E0501UnpackBAK not in paths:
                paths.append(ei_turnkey.E0501UnpackBAK)
        _filepaths = []
        for path in paths:
            _filepaths.extend(glob.glob(os.path.join(path, "*", "*", "*")))
        lg.debug("_filepaths: {}".format(_filepaths))
        exclude_filepaths = EITurnkeyE0501XML.objects.filter(abspath__in=_filepaths, is_parsed=True).values_list('abspath', flat=True)
        lg.debug("exclude_filepaths: {}".format(exclude_filepaths))
        filepaths = []
        for _fp in _filepaths:
            if _fp not in filepaths and _fp not in exclude_filepaths:
                filepaths.append(_fp)
        lg.debug("filepaths: {}".format(filepaths))
        if filepaths:
            for filepath in filepaths:
                if EITurnkeyE0501XML.objects.filter(abspath=filepath, is_parsed=True).exists():
                    continue
                content = open(filepath, 'r').read()
                if 'InvoiceEnvelope xmlns' not in content:
                    _eitE0501xml = EITurnkeyE0501XML(abspath=filepath, is_parsed=True)
                    _eitE0501xml.save()
                    continue
                lg.debug(filepath)
                try:
                    eitE0501xml = EITurnkeyE0501XML.objects.get(abspath=filepath)
                except EITurnkeyE0501XML.DoesNotExist:
                    eitE0501xml = EITurnkeyE0501XML(abspath=filepath)
                eitE0501xml.content = content
                eitE0501xml.save()
                eitE0501xmls.append(eitE0501xml)
        return eitE0501xmls


    @property
    def mask_hash_key(self):
        return self.hash_key[:4] + '********************************' + self.hash_key[-4:]
    @property
    def E0501UnpackBAK(self):
        task_config_object = self.get_task_config(category_type='B2B', process_type='EXCHANGE', task='Unpack')
        return os.path.join(task_config_object.SRC_PATH, "BAK", "E0501")
    @property
    def SummaryResultUnpackBAK(self):
        task_config_object = self.get_task_config(category_type='B2B', process_type='EXCHANGE', task='Unpack')
        return os.path.join(task_config_object.SRC_PATH, "BAK", "SummaryResult")
    @property
    def B2BExchangeUpCastSRC(self):
        task_config_object = self.get_task_config(category_type='B2B', process_type='EXCHANGE', task='UpCast')
        return os.path.join(task_config_object.SRC_PATH, "{mig}", "SRC")
    @property
    def B2BStorageUpCastSRC(self):
        task_config_object = self.get_task_config(category_type='B2B', process_type='STORAGE', task='UpCast')
        return os.path.join(task_config_object.SRC_PATH, "{mig}", "SRC")
    @property
    def B2CStorageUpCastSRC(self):
        task_config_object = self.get_task_config(category_type='B2C', process_type='STORAGE', task='UpCast')
        return os.path.join(task_config_object.SRC_PATH, "{mig}", "SRC")
    @property
    def B2PMessageUpCastSRC(self):
        task_config_object = self.get_task_config(category_type='B2P', process_type='MESSAGE', task='UpCast')
        return os.path.join(task_config_object.SRC_PATH, "{mig}", "SRC")



    class Meta:
        unique_together = (('party_id', 'routing_id', ), )



    def get_task_config(self, category_type='', process_type='', task=''):
        data_abspath = self.data_abspath
        return TASK_CONFIG.objects.get(CATEGORY_TYPE=category_type,
                                       PROCESS_TYPE=process_type,
                                       TASK=task,
                                       SRC_PATH__startswith=data_abspath)
    

    def verify_counter_based_otp_in_row(self, otps):
        n_times_in_a_row = 3
        key = '{}-{}-{}-{}'.format(self.routing_id, self.hash_key, self.transport_id, self.party_id)
        cbotpr = CounterBasedOTPinRow(SECRET=key.encode('utf-8'), N_TIMES_IN_A_ROW=n_times_in_a_row)
        return cbotpr.verify_otps(otps)
    

    def save(self, *args, **kwargs):
        if not os.access(self.data_abspath, os.W_OK):
            raise Exception("data_abspath({}) can not be writeable".format(self.data_abspath))
        elif not os.access(self.tmpdata_abspath, os.W_OK):
            raise Exception("tmpdata_abspath({}) can not be writeable".format(self.tmpdata_abspath))
        return super(EITurnkey, self).save(*args, **kwargs)
    

    def get_the_current_year_month_exist_track_nos(self):
        pass



class EITurnkeyBatch(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True, db_index=True)
    ei_turnkey = models.ForeignKey(EITurnkey, on_delete=models.DO_NOTHING)
    slug = models.CharField(max_length=14)
    mig_choices = (
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

        ('F0401', _('B2B/B2C Certificate Invoice')),
        ('F0501', _('B2B/B2C Certificate Cancel Invoice')),
        ('F0701', _('B2B/B2C Certificate Void Invoice')),
    )
    mig = models.CharField(max_length=5, choices=mig_choices, default='F0401')
    version_choices = (
        ('3.2', 'v32'),
        ('4.0', 'v40'),
    )
    turnkey_version = models.CharField(max_length=8, choices=version_choices, default='4.0') # MIG version at turnkey
    status_choices = (
        ("7", _("Just created")),
        ("8", _("Downloaded from TEA")),
        ("9", _("Exported to Data/")),
        ("F", _("Finish")),
    )
    status = models.CharField(max_length=1, default='7', choices=status_choices, db_index=True)
    @property
    def count(self):
        return self.eiturnkeybatcheinvoice_set.count()


    
    class Meta:
        unique_together = (('ei_turnkey', 'slug', ), )


    @classmethod
    def status_check(cls, statuss=[]):
        eitbs = []
        for eitb in cls.objects.exclude(status__in=['7', 'F']).filter(status__in=statuss).order_by('id'):
            while True:
                function_name = 'check_in_{}_status_then_update_to_the_next'.format(eitb.status)
                pair = [eitb, function_name, eitb.status]
                if hasattr(eitb, function_name):
                    getattr(*pair[:2])()
                    pair.append(eitb.status)
                    eitbs.append(pair)
                if 3 == len(pair) or pair[2] == pair[3]:
                    break
        return eitbs


    def save(self, *args, **kwargs):
        data_abspath = self.ei_turnkey.data_abspath
        task_config_objects = TASK_CONFIG.objects.filter(SRC_PATH__startswith=data_abspath)

        if not task_config_objects.filter(CATEGORY_TYPE="B2B", PROCESS_TYPE="EXCHANGE", TASK="ReceiveFile").exists():
            raise EITurnkeyConfigurationError(_("ReceiveFile directory does not exist!"))

        TASK_D = {
            ("B2C", "STORAGE"): ("UpCast", "SendFile", "Pack", ),
            ("B2B", "EXCHANGE"): ("UpCast", "Unpack", "SendFile", "ReceiveFile", "Pack", "DownCast", ),
            ("B2B", "STORAGE"): ("UpCast", "SendFile", "Pack", ),
            ("B2P", "MESSAGE"): ("UpCast", "SendFile", "Pack", ),
        }

        if self.mig in [
            'F0401',
            'F0501',
            'F0701',
            ]:
            category_type = "B2S"
            process_type = "STORAGE"
        elif self.mig in [
            'C0401',
            'C0501',
            'C0701',
            'D0401',
            'D0501',
            ]:
            category_type = "B2C"
            process_type = "STORAGE"
        elif self.mig in [
            'A0101',
            'A0102',
            'B0101',
            'B0102',
            'A0201',
            'A0202',
            'B0201',
            'B0202',
            'A0301',
            'A0302',
            ]:
            category_type = "B2B"
            process_type = "EXCHANGE"
        elif self.mig in [
            'A0401',
            'B0401',
            'A0501',
            'B0501',
            'A0601',
            ]:
            category_type = "B2B"
            process_type = "STORAGE"
        elif self.mig in [
            'E0401',
            'E0402',
            'E0501',
            ]:
            category_type = "B2P"
            process_type = "MESSAGE"
        else:
            raise EITurnkeyConfigurationError(_("MIG Type does not match any TASK record"))
    
        tasks = TASK_D[(category_type, process_type)]
        tasks_count = len(tasks)

        
        if tasks_count != task_config_objects.filter(CATEGORY_TYPE=category_type,
                                                     PROCESS_TYPE=process_type,
                                                     TASK__in=tasks).count():
            raise EITurnkeyConfigurationError(_("The count of directories for {} {} do not match {}!".format(
                    category_type,
                    process_type,
                    tasks_count,
                    )))

        return super().save(*args, **kwargs)


    def check_in_8_status_then_update_to_the_next(self):
        self.export_to_data_abspath()


    def check_in_9_status_then_update_to_the_next(self):
        self.check_status_of_ei_turnkey_batch_einvoices()
    

    def check_status_of_ei_turnkey_batch_einvoices(self):
        if "9" != self.status:
            return False
        else:
            NEXT_STATUS_IN_GOOD = 'F'
        
        for eitbei in self.eiturnkeybatcheinvoice_set.filter(status__in=["", "P", "G", "I", "E"]):
            eitbei.check_status_from_ei()
        
        if not self.eiturnkeybatcheinvoice_set.exclude(status__in=[".", "C"]).exists():
            self.update_to_new_status(NEXT_STATUS_IN_GOOD)


    def update_to_new_status(self, new_status):
        status_list = [_i[0] for _i in self.status_choices]
        if new_status and 1 == status_list.index(new_status) - status_list.index(self.status):
            self.status = new_status
            self.save()
        else:
            raise Exception('Wrong status flow: {}=>{}'.format(self.status, new_status))
        return self.status
    

    def update_einvoice_bodys(self, bodys):
        if "7" != self.status:
            return False
        else:
            NEXT_STATUS_IN_GOOD = '8'

        lg = logging.getLogger('turnkey_web')
        for line in bodys:
            lg.debug("line: {}".format(line))
            batch_einvoice_id, batch_einvoice_begin_time, batch_einvoice_end_time, batch_einvoice_track_no, body = line
            lg.debug("batch_einvoice_id, batch_einvoice_begin_time, batch_einvoice_end_time, batch_einvoice_track_no, body: {} {}".format(
                batch_einvoice_id, batch_einvoice_begin_time, batch_einvoice_end_time, batch_einvoice_track_no, body
                ))
            try:
                batch_einvoice_begin_time = datetime.datetime.strptime(batch_einvoice_begin_time, "%Y-%m-%d %H:%M:%S%z")
                batch_einvoice_end_time = datetime.datetime.strptime(batch_einvoice_end_time, "%Y-%m-%d %H:%M:%S%z")
            except Exception as e:
                twrc = TurnkeyWebReturnCode("003")
                result = {
                    "return_code": twrc.return_code,
                    "return_code_message": twrc.message,
                    "slug": self.slug,
                    "batch_einvoice_id": batch_einvoice_id,
                    "message_detail": str(e),
                }
                return result
            mig_no, json_body = body.popitem()
            try:
                eitbei = self.eiturnkeybatcheinvoice_set.get(batch_einvoice_id=batch_einvoice_id)
            except EITurnkeyBatchEInvoice.DoesNotExist:
                error_005 = True
                _same_eitbeis = EITurnkeyBatchEInvoice.objects.filter(status__in=EITurnkeyBatchEInvoice_CAN_NOT_DUPLICATES_EXIST_IN_STATUSS,
                                                                      batch_einvoice_begin_time=batch_einvoice_begin_time,
                                                                      batch_einvoice_end_time=batch_einvoice_end_time,
                                                                      batch_einvoice_track_no=batch_einvoice_track_no)
                same_eitbeis = _same_eitbeis.filter(**{"body__{}__isnull".format(mig_no): False})
                if not same_eitbeis.exists():
                    error_005 = False
                elif mig_no in ["F0401", "F0701"]:
                    same_eitbeis_47 = _same_eitbeis.order_by('-id')[0]
                    k, v = same_eitbeis_47.body.popitem()
                    if "F0401" == mig_no and "C" == same_eitbeis_47.status and "F0701" == k and v:
                        error_005 = False
                    elif "F0701" == mig_no and "C" == same_eitbeis_47.status and "F0401" == k and v:
                        error_005 = False
                elif mig_no in ["C0401", "C0701"]:
                    same_eitbeis_47 = _same_eitbeis.order_by('-id')[0]
                    k, v = same_eitbeis_47.body.popitem()
                    if "C0401" == mig_no and "C" == same_eitbeis_47.status and "C0701" == k and v:
                        error_005 = False
                    elif "C0701" == mig_no and "C" == same_eitbeis_47.status and "C0401" == k and v:
                        error_005 = False

                if error_005:
                    twrc = TurnkeyWebReturnCode("005")
                    result = {
                        "return_code": twrc.return_code,
                        "return_code_message": twrc.message,
                        "slug": self.slug,
                        "batch_einvoice_id": batch_einvoice_id,
                    }
                    return result
                else:
                    eitbei = EITurnkeyBatchEInvoice(
                        ei_turnkey_batch=self,
                        batch_einvoice_id=batch_einvoice_id,
                    )
            if eitbei.body not in ["", {}] or "" != eitbei.status or "" != eitbei.result_code:
                pass
            else:
                eitbei.batch_einvoice_track_no = batch_einvoice_track_no
                eitbei.batch_einvoice_begin_time = batch_einvoice_begin_time
                eitbei.batch_einvoice_end_time = batch_einvoice_end_time
                eitbei.save_body_time = now()
                eitbei.body = {mig_no: json_body}
                try:
                    eitbei.save()
                except Exception as e:
                    twrc = TurnkeyWebReturnCode("004")
                    result = {
                        "return_code": twrc.return_code,
                        "return_code_message": twrc.message,
                        "slug": self.slug,
                        "batch_einvoice_id": batch_einvoice_id,
                        "message_detail": str(e),
                    }
                    return result
        
        self.update_to_new_status(NEXT_STATUS_IN_GOOD)
        twrc = TurnkeyWebReturnCode("0")
        result = {
            "return_code": twrc.return_code,
            "return_code_message": twrc.message,
        }
        return result


    def export_to_data_abspath(self):
        if "8" != self.status:
            return False
        elif not self.ei_turnkey.can_sync_to_ei:
            return False
        else:
            NEXT_STATUS_IN_GOOD = '9'

        tmp_data_path = os.path.join(self.ei_turnkey.tmpdata_abspath, self.slug)
        pathlib.Path(tmp_data_path).mkdir(parents=True, exist_ok=True)
        for eitbei in self.eiturnkeybatcheinvoice_set.filter(result_code=''):
            tmp_file_path = os.path.join(tmp_data_path,
                "{routing_id}_{mig}_{version}_{track_no}.xml".format(routing_id=self.ei_turnkey.routing_id,
                                                                     mig=self.mig,
                                                                     version=self.get_turnkey_version_display(),
                                                                     track_no=eitbei.batch_einvoice_track_no))
            f = open(tmp_file_path, 'w')
            f.write(eitbei.mig_xml)
            f.close()
        for f in glob.glob(os.path.join(tmp_data_path, "*")):
            if self.mig.startswith("E"):
                _path = self.ei_turnkey.B2PMessageUpCastSRC.format(mig=self.mig)
            elif self.mig.startswith("C"):
                _path = self.ei_turnkey.B2CStorageUpCastSRC.format(mig=self.mig)
            else:
                _path = ''

            if _path:
                pathlib.Path(_path).mkdir(parents=True, exist_ok=True)
                shutil.move(f, _path)
        
        self.update_to_new_status(NEXT_STATUS_IN_GOOD)
        return True



    def get_batch_einvoice_id_status_result_code_set_from_ei_turnkey_batch_einvoices(self):
        statuss = []
        max_count_on_status = ''
        max_count = 0
        for d in self.eiturnkeybatcheinvoice_set.values('status').annotate(status_count=Count('status')):
            if d['status_count'] > max_count:
                max_count = d['status_count']
                max_count_on_status = d['status']
            statuss.append(d['status'])
        
        status_d = {}
        for status in statuss:
            if status != max_count_on_status:
                status_d[status] = self.eiturnkeybatcheinvoice_set.filter(status=status
                                                                         ).values_list('batch_einvoice_id',
                                                                                       named=False,
                                                                                       flat=True)
            else:
                status_d['__else__'] = max_count_on_status
        
        upload_to_ei_times = []
        max_count_on_upload_to_ei_time = ''
        max_count = 0
        for d in self.eiturnkeybatcheinvoice_set.values('upload_to_ei_time').annotate(upload_to_ei_time_count=Count('upload_to_ei_time')):
            if d['upload_to_ei_time_count'] > max_count:
                max_count = d['upload_to_ei_time_count']
                max_count_on_upload_to_ei_time = d['upload_to_ei_time']
            upload_to_ei_times.append(d['upload_to_ei_time'])
        
        upload_to_ei_time_d = {}
        for upload_to_ei_time in upload_to_ei_times:
            if upload_to_ei_time != max_count_on_upload_to_ei_time:
                upload_to_ei_time_d[str(upload_to_ei_time)] = self.eiturnkeybatcheinvoice_set.filter(upload_to_ei_time=upload_to_ei_time
                                                                                               ).values_list('batch_einvoice_id',
                                                                                                             named=False,
                                                                                                             flat=True)
            else:
                upload_to_ei_time_d['__else__'] = max_count_on_upload_to_ei_time
        
        result_code_d = {}
        for d in self.eiturnkeybatcheinvoice_set.exclude(result_code=''
                                                        ).values('result_code'
                                                                ).annotate(result_code_count=Count('result_code')):
            result_code_d[d['result_code']] = self.eiturnkeybatcheinvoice_set.filter(result_code=d['result_code']
                                                                                    ).values_list('batch_einvoice_id',
                                                                                                  named=False,
                                                                                                  flat=True)

        result_message_d = {}
        for d in self.eiturnkeybatcheinvoice_set.exclude(result_message=''
                                                        ).values('result_message'
                                                                ).annotate(result_message_count=Count('result_message')):
            result_message_d[d['result_message']] = self.eiturnkeybatcheinvoice_set.filter(result_message=d['result_message']
                                                                                          ).values_list('batch_einvoice_id',
                                                                                                        named=False,
                                                                                                        flat=True)
        return {
            "status": status_d,
            "upload_to_ei_time": upload_to_ei_time_d,
            "result_code": result_code_d,
            "result_message": result_message_d,
        }



class EITurnkeyBatchEInvoice(models.Model):
    ei_turnkey_batch = models.ForeignKey(EITurnkeyBatch, on_delete=models.DO_NOTHING)
    batch_einvoice_id = models.PositiveIntegerField(default=0)
    batch_einvoice_begin_time = models.DateTimeField()
    batch_einvoice_end_time = models.DateTimeField()
    invoice_identifier = models.CharField(max_length=23, db_index=True)
    @property
    def batch_einvoice_end_time_minus_1_second(self):
        return self.batch_einvoice_end_time - datetime.timedelta(seconds=1)
    batch_einvoice_track_no = models.CharField(max_length=10)
    status_choices = (
        ("", _("Waiting")),
        ("P", _("Preparing for EI(P)")),
        ("G", _("Uploaded to EI or Downloaded from EI(G)")),
        ("E", _("E Error for EI process(E)")),
        ("I", _("I Error for EI process(I)")),
        ("C", _("Successful EI process(C)")),
        (".", _("Failed but pass(.)")),
    )
    status = models.CharField(max_length=1, default="", choices=status_choices, db_index=True)
    save_body_time = models.DateTimeField()
    upload_to_ei_time = models.DateTimeField(null=True)
    body = models.JSONField(default="")
    result_code = models.CharField(max_length=5, default="", db_index=True)
    result_message = models.TextField(default='')


    @property
    def mig_xml(self):
        for k, v in self.body.items():
            if 'F0401' == k:
                j2mx = F0401JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'F0501' == k:
                j2mx = F0501JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'F0701' == k:
                j2mx = F0701JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'C0401' == k:
                j2mx = C0401JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'C0501' == k:
                j2mx = C0501JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'C0701' == k:
                j2mx = C0701JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'E0402' == k:
                j2mx = E0402JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            return j2mx.export_xml()


    def save(self, *args, **kwargs):
        if not self.invoice_identifier:
            mig = self.ei_turnkey_batch.mig
            if mig in ["F0401", "F0501", "F0701", "C0401", "C0501", "C0701"]:
                if mig in ["F0401", "C0401"]:
                    invoice_date = self.body[self.ei_turnkey_batch.mig]["Main"]["InvoiceDate"]
                elif mig in ["F0501", "C0501"]:
                    invoice_date = self.body[self.ei_turnkey_batch.mig]["CancelDate"]
                elif mig in ["F0701", "C0701"]:
                    invoice_date = self.body[self.ei_turnkey_batch.mig]["VoidDate"]
                self.invoice_identifier = "{mig}{batch_einvoice_track_no}{InvoiceDate}".format(
                    mig=mig,
                    batch_einvoice_track_no=self.batch_einvoice_track_no,
                    InvoiceDate=invoice_date,
                )
            elif "E0402" == mig:
                self.invoice_identifier = "{BranchBan}-{InvoiceTrack}-{InvoiceType}".format(
                    BranchBan=self.body[self.ei_turnkey_batch.mig]["Main"]["BranchBan"],
                    InvoiceTrack=self.body[self.ei_turnkey_batch.mig]["Main"]["InvoiceTrack"],
                    InvoiceType=self.body[self.ei_turnkey_batch.mig]["Main"]["InvoiceType"],
                )
            else:
                raise MIGConfigurationError(_("There is no setting for {}").format(mig))
        super().save(*args, **kwargs)


    def check_status_from_ei(self):
        lg = logging.getLogger("turnkey_web")
        SAVE_BODY_TIME_DTS = self.save_body_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y%m%d%H%M%S000')
        lg.debug("SAVE_BODY_TIME_DTS: {}".format(SAVE_BODY_TIME_DTS))
        if 'E0402' in self.body:
            query_d = {"INVOICE_IDENTIFIER__regex": "-?".join(self.invoice_identifier.split('-'))}
        else:
            query_d = {"INVOICE_IDENTIFIER": self.invoice_identifier}
        try:
            nearest_TURNKEY_MESSAGE_LOG = TURNKEY_MESSAGE_LOG.objects.filter(MESSAGE_DTS__gte=SAVE_BODY_TIME_DTS,
                                                                             **query_d
                                                                            ).order_by('MESSAGE_DTS')[0]
        except IndexError:
            return
        else:
            if "" == nearest_TURNKEY_MESSAGE_LOG.STATUS:
                return
            elif nearest_TURNKEY_MESSAGE_LOG.STATUS in EI_WELL_STATUSS:
                self.status = nearest_TURNKEY_MESSAGE_LOG.STATUS
            elif nearest_TURNKEY_MESSAGE_LOG.STATUS.startswith('E'):
                self.status = 'E'
            else:
                self.status = 'I'
            if self.status in ['E', 'I']:
                self.result_code, self.result_message = nearest_TURNKEY_MESSAGE_LOG.get_TURNKEY_SYSEVENT_LOG__MESSAGES()
            self.upload_to_ei_time = nearest_TURNKEY_MESSAGE_LOG.MESSAGE_DTS_datetime
            self.save()
            return self.status



class EITurnkeyDailySummaryResultXML(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    abspath = models.CharField(max_length=255, unique=True)
    ei_turnkey = models.ForeignKey(EITurnkey, null=True, on_delete=models.DO_NOTHING)
    result_date = models.DateField(null=True)
    is_parsed = models.BooleanField(default=False)
    total_count = models.SmallIntegerField(default=0)
    good_count = models.SmallIntegerField(default=0)
    failed_count = models.SmallIntegerField(default=0)
    total_batch_einvoice_ids = models.JSONField(default=[])
    good_batch_einvoice_ids = models.JSONField(default=[])
    failed_batch_einvoice_ids = models.JSONField(default=[])
    binary_content = models.BinaryField()
    error_note = models.TextField(default='')
    @property
    def content(self):
        content = zlib.decompress(self.binary_content)
        return content
    @content.setter
    def content(self, value=''):
        if bytes != type(value):
            value = value.encode('utf-8')
        self.binary_content = zlib.compress(value)

    
    def parse(self):
        lg = logging.getLogger('turnkey_web')
        ignore_very_old_TURNKEY_MESSAGE_LOG = False
        error_message = ''
        X = xmltodict.parse(self.content)
        party_id = X['SummaryResult']['RoutingInfo']['From']['PartyId']
        routing_id = X['SummaryResult']['RoutingInfo']['FromVAC']['RoutingId']
        self.ei_turnkey = EITurnkey.objects.get(party_id=party_id, routing_id=routing_id)
        counts = {
            "Total": 0,
            "Good": 0,
            "Failed": 0,
        }
        batch_einvoice_idss = {
            "Total": [],
            "Good": [],
            "Failed": [],
        }

        if list == type(X['SummaryResult']['DetailList']['Message']):
            messages = X['SummaryResult']['DetailList']['Message']
        else:
            messages = [X['SummaryResult']['DetailList']['Message']]
        for message in messages:
            ids = message['Info']['Id'].split('-')
            mig_no, report_date, report_time = ids[1:4]
            uuid = "-".join(ids[4:])
            self.result_date = datetime.datetime.strptime(report_date, "%Y%m%d").date()
            mig_no = message['Info']['MessageType']
            for key in counts.keys():
                if mig_no in ('E0402', ):
                    continue
                elif '0' == message['ResultType'][key]['ResultDetailType']['Count']:
                    continue
                if list == type(message['ResultType'][key]['ResultDetailType']['Invoices']['Invoice']):
                    invoices = message['ResultType'][key]['ResultDetailType']['Invoices']['Invoice']
                else:
                    invoices = [message['ResultType'][key]['ResultDetailType']['Invoices']['Invoice']]
                for invoice in invoices:
                    if mig_no in ["F0501", "C0501"]:
                        invoice_identifier = "{}{}{}".format(mig_no, invoice['ReferenceNumber'], report_date)
                    else:
                        invoice_identifier = "{}{}{}".format(mig_no, invoice['ReferenceNumber'], invoice['InvoiceDate'])
                    try:
                        tml = TURNKEY_MESSAGE_LOG.objects.get(UUID=uuid, INVOICE_IDENTIFIER=invoice_identifier)
                    except TURNKEY_MESSAGE_LOG.DoesNotExist:
                        if not ignore_very_old_TURNKEY_MESSAGE_LOG:
                            report_datetime = TAIPEI_TIMEZONE.localize(datetime.datetime.strptime(report_date+report_time+"000", "%Y%m%d%H%M%S%f"))
                            first_eitbei = EITurnkeyBatchEInvoice.objects.all().order_by('upload_to_ei_time').first()
                            if first_eitbei and report_datetime < first_eitbei.upload_to_ei_time:
                                self.is_parsed = True
                                return None
                    eitbei = EITurnkeyBatchEInvoice.objects.get(invoice_identifier=invoice_identifier, upload_to_ei_time=tml.MESSAGE_DTS_datetime)
                    if eitbei.batch_einvoice_id not in batch_einvoice_idss[key]:
                        counts[key] += 1
                        batch_einvoice_idss[key].append(eitbei.batch_einvoice_id)
        if counts['Total'] != counts['Good'] + counts['Failed']:
            error_message = "{filepath} Total({total_count}) != Good({good_count}) + Failed({failed_count})".format(
                filepath=self.abspath,
                total_count=counts['Total'],
                good_count=counts['Good'],
                failed_count=counts['Failed'])
            lg.error(error_message)

        self.total_count = counts['Total']
        self.good_count = counts['Good']
        self.failed_count = counts['Failed']
        self.total_batch_einvoice_ids = batch_einvoice_idss['Total']
        self.good_batch_einvoice_ids = batch_einvoice_idss['Good']
        self.failed_batch_einvoice_ids = batch_einvoice_idss['Failed']

        self.error_note = error_message
        self.is_parsed = True
        summary_result, new_creation = EITurnkeyDailySummaryResult.objects.get_or_create(
            ei_turnkey=self.ei_turnkey,
            result_date=self.result_date
        )
        return summary_result


    def save(self, *args, **kwargs):
        lg = logging.getLogger('turnkey_web')
        summary_result = None
        if self.binary_content and not self.is_parsed:
            try:
                summary_result = self.parse()
            except Exception as e:
                lg.error("{abspath}: {type} {e}".format(abspath=self.abspath, type=type(e), e=e))
                self.error_note = "{}: {}".format(type(e), str(e))
        super().save(*args, **kwargs)
        if summary_result:
            summary_result.xml_files.add(self)



class EITurnkeyDailySummaryResult(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ei_turnkey = models.ForeignKey(EITurnkey, on_delete=models.DO_NOTHING)
    result_date = models.DateField()
    xml_files = models.ManyToManyField(EITurnkeyDailySummaryResultXML)
    @property
    def total_count(self):
        return sum(self.xml_files.all().values_list('total_count', flat=True))
    @property
    def good_count(self):
        return sum(self.xml_files.all().values_list('good_count', flat=True))
    @property
    def failed_count(self):
        return sum(self.xml_files.all().values_list('failed_count', flat=True))
    total_batch_einvoice_ids = models.JSONField(default=[])
    @property
    def total_batch_einvoice_ids(self):
        return [x for y in self.xml_files.all().values_list('total_batch_einvoice_ids', flat=True) for x in y]
    good_batch_einvoice_ids = models.JSONField(default=[])
    @property
    def good_batch_einvoice_ids(self):
        return [x for y in self.xml_files.all().values_list('good_batch_einvoice_ids', flat=True) for x in y]
    failed_batch_einvoice_ids = models.JSONField(default=[])
    @property
    def failed_batch_einvoice_ids(self):
        return [x for y in self.xml_files.all().values_list('failed_batch_einvoice_ids', flat=True) for x in y]



    class Meta:
        unique_together = (("ei_turnkey", "result_date", ), )



class EITurnkeyE0501XML(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    abspath = models.CharField(max_length=255, unique=True)
    ei_turnkey = models.ForeignKey(EITurnkey, null=True, on_delete=models.DO_NOTHING)
    is_parsed = models.BooleanField(default=False)
    invoice_assign_nos = models.JSONField(default=[])
    binary_content = models.BinaryField()
    error_note = models.TextField(default='')
    @property
    def content(self):
        content = zlib.decompress(self.binary_content)
        return content
    @content.setter
    def content(self, value=''):
        if bytes != type(value):
            value = value.encode('utf-8')
        self.binary_content = zlib.compress(value)

    
    def parse(self):
        lg = logging.getLogger('turnkey_web')
        error_message = ''
        X = xmltodict.parse(self.content)
        party_id = X['InvoiceEnvelope']['From']['PartyId']
        routing_id = X['InvoiceEnvelope']['FromVAC']['RoutingId']
        if routing_id:
            self.ei_turnkey = EITurnkey.objects.get(party_id=party_id, routing_id=routing_id)
        else:
            self.ei_turnkey = EITurnkey.objects.filter(party_id=party_id).order_by('id')[0]
        invoice_assign_nos = []
        if list == type(X['InvoiceEnvelope']['InvoicePack']['InvoiceAssignNo']):
            ians = X['InvoiceEnvelope']['InvoicePack']['InvoiceAssignNo']
        else:
            ians = [X['InvoiceEnvelope']['InvoicePack']['InvoiceAssignNo']]
        for ian in ians:
            if party_id != ian['Ban']:
                error_message += "party_id: {} != Ban: {}\n".format(party_id, ian['Ban'])
                continue
            d = {
                'InvoiceType': ian['InvoiceType'],
                'YearMonth': ian['YearMonth'],
                'InvoiceTrack': ian['InvoiceTrack'],
                'InvoiceBeginNo': ian['InvoiceBeginNo'],
                'InvoiceEndNo': ian['InvoiceEndNo'],
                'InvoiceBooklet': int(ian['InvoiceBooklet']),
            }
            invoice_assign_nos.append(d)

        self.invoice_assign_nos = invoice_assign_nos
        self.error_note = error_message
        self.is_parsed = True
        eitians = []
        for d in invoice_assign_nos:
            eitian, new_creation = EITurnkeyE0501InvoiceAssignNo.objects.get_or_create(
                ei_turnkey=self.ei_turnkey,
                invoice_type=d['InvoiceType'],
                year_month=d['YearMonth'],
                invoice_track=d['InvoiceTrack'].upper(),
                invoice_begin_no=d['InvoiceBeginNo'],
                invoice_end_no=d['InvoiceEndNo'],
                invoice_booklet=d['InvoiceBooklet'],
            )
            eitians.append(eitian)
        return eitians


    def save(self, *args, **kwargs):
        lg = logging.getLogger('turnkey_web')
        invoice_assign_nos = None
        if self.binary_content and not self.is_parsed:
            try:
                invoice_assign_nos = self.parse()
            except Exception as e:
                lg.error("{abspath}: {type} {e}".format(abspath=self.abspath, type=type(e), e=e))
                self.error_note = "{}: {}".format(type(e), str(e))
        super().save(*args, **kwargs)
        if invoice_assign_nos:
            for ian in invoice_assign_nos:
                ian.xml_files.add(self)



class EITurnkeyE0501InvoiceAssignNo(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    ei_turnkey = models.ForeignKey(EITurnkey, on_delete=models.DO_NOTHING)
    type_choices = (
        ('07', _('General')),
        ('08', _('Special')),
    )
    invoice_type = models.CharField(max_length=2,
                                    default='07',
                                    choices=type_choices,
                                    db_index=True)
    year_month = models.CharField(max_length=5, db_index=True)
    invoice_track = models.CharField(max_length=2, db_index=True)
    invoice_begin_no = models.CharField(max_length=8, db_index=True)
    invoice_end_no = models.CharField(max_length=8, db_index=True)
    invoice_booklet = models.SmallIntegerField(default=0)
    xml_files = models.ManyToManyField(EITurnkeyE0501XML)


    class Meta:
        unique_together = (("ei_turnkey", "invoice_type", "year_month", "invoice_track",
                            "invoice_begin_no", "invoice_end_no", "invoice_booklet"), )



class F0401JSON2MIGXMl(object):
    versions = ["4.0"]
    base_xml = """<Invoice xmlns="urn:GEINV:eInvoiceMessage:F0401:{version}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:F0401:{version} F0401.xsd">
    {xml_body}
</Invoice>"""


    def __init__(self, json_data, version="4.0"):
        if version not in self.versions:
            raise Exception("Only accept version number: {}".format(", ".join(self.versions)))
        self.version = version
        self.json_data = self.regulate_json_data(json_data)
    

    def export_xml(self):
        return self.base_xml.format(version=self.version, xml_body=self.get_xml_body())

    
    def regulate_json_data(self, json_data):
        def _append_sequence_number(index0, d):
            d["SequenceNumber"] = "{:03d}".format(index0+1)
            return d
        json_data["Details"] = [{"ProductItem": _append_sequence_number(_i, _pi)}
            for _i, _pi in enumerate(json_data["Details"])
        ]

        if "FreeTaxSalesAmount" not in json_data["Amount"]:
            json_data["Amount"]["FreeTaxSalesAmount"] = '0'
        if "ZeroTaxSalesAmount" not in json_data["Amount"]:
            json_data["Amount"]["ZeroTaxSalesAmount"] = '0'
        return json_data
    

    def get_xml_body(self):
        xml_body = ''
        for elm in ["Main", "Details", "Amount"]:
            xml = json2xml.Json2xml(self.json_data[elm], wrapper=elm, pretty=False, item_wrap=False, attr_type=False).to_xml()
            xml_body += XML_VERSION_RE.sub("", xml.decode('utf-8'))
        return xml_body



class F0501JSON2MIGXMl(F0401JSON2MIGXMl):
    base_xml = """<CancelInvoice xmlns="urn:GEINV:eInvoiceMessage:F0501:{version}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:F0501:{version} F0501.xsd">
    {xml_body}
</CancelInvoice>"""


    def __init__(self, json_data, version="4.0"):
        super().__init__(json_data, version=version)


    def export_xml(self):
        return super().export_xml()


    def regulate_json_data(self, json_data):
        return json_data


    def get_xml_body(self):
        remove_elm = "will_remove_dfajdlfzx"
        _xml_body = json2xml.Json2xml(self.json_data, wrapper=remove_elm, pretty=False, item_wrap=False, attr_type=False).to_xml()
        _xml_body = XML_VERSION_RE.sub("", _xml_body.decode('utf-8'))
        xml_body = WILL_REMOVE_DFAJDLFZX_RE.sub("", _xml_body)
        return xml_body



class F0701JSON2MIGXMl(F0501JSON2MIGXMl):
    base_xml = """<VoidInvoice xmlns="urn:GEINV:eInvoiceMessage:F0701:{version}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:F0701:{version} F0701.xsd">
    {xml_body}
</VoidInvoice>"""

