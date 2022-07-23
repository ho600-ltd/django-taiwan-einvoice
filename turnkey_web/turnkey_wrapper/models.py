import os, re, logging, datetime, pathlib, shutil, glob, pytz
from json2xml import json2xml
from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from taiwan_einvoice.libs import CounterBasedOTPinRow
from taiwan_einvoice.turnkey import TurnkeyWebReturnCode


TAIPEI_TIMEZONE = pytz.timezone('Asia/Taipei')



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
        db_table = 'FROM_CONFIG'


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
        db_table = 'SCHEDULE_CONFIG'


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
        db_table = 'SIGN_CONFIG'


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


class TURNKEY_MESSAGE_LOG_DETAIL(models.Model):
    SEQNO_SUBSEQNO_TASK = models.CharField(db_column='SEQNO_SUBSEQNO_TASK', primary_key=True, max_length=45)
    SEQNO = models.CharField(db_column='SEQNO', max_length=8)
    SUBSEQNO = models.CharField(db_column='SUBSEQNO', max_length=5)
    PROCESS_DTS = models.CharField(db_column='PROCESS_DTS', max_length=17, blank=True, null=True)
    TASK = models.CharField(db_column='TASK', max_length=30)
    STATUS = models.CharField(db_column='STATUS', max_length=5, blank=True, null=True)
    FILENAME = models.CharField(db_column='FILENAME', max_length=255, blank=True, null=True, db_index=True)
    UUID = models.CharField(db_column='UUID', max_length=40, blank=True, null=True)

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
        db_table = 'TURNKEY_SEQUENCE'


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

    def __str__(self):
        return "{}-{}".format(self.SEQNO, self.SUBSEQNO)


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_SYSEVENT_LOG'
        verbose_name_plural = 'TURNKEY_SYSEVENT_LOG'
        db_table = 'TURNKEY_SYSEVENT_LOG'
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
        db_table = 'TURNKEY_TRANSPORT_CONFIG'


class TURNKEY_USER_PROFILE(models.Model):
    USER_ID = models.CharField(db_column='USER_ID', primary_key=True, max_length=10)
    USER_PASSWORD = models.CharField(db_column='USER_PASSWORD', max_length=100, blank=True, null=True)
    USER_ROLE = models.CharField(db_column='USER_ROLE', max_length=2, blank=True, null=True)

    def __str__(self):
        return self.USER_ID


    class Meta:
        managed = False
        verbose_name = 'TURNKEY_USER_PROFILE'
        verbose_name_plural = 'TURNKEY_USER_PROFILE'
        db_table = 'TURNKEY_USER_PROFILE'



class EITurnkey(models.Model):
    tmpdata_abspath = models.CharField(max_length=755)
    data_abspath = models.CharField(max_length=755)
    hash_key = models.CharField(max_length=40)
    transport_id = models.CharField(max_length=10)
    party_id = models.CharField(max_length=10)
    routing_id = models.CharField(max_length=39)
    tea_turnkey_service_endpoint = models.CharField(max_length=755)
    allow_ips = models.JSONField(null=True)
    endpoint = models.CharField(max_length=755, null=True)


    @property
    def mask_hash_key(self):
        return self.hash_key[:4] + '********************************' + self.hash_key[-4:]
    

    @property
    def B2BExchangeUpCastSRC(self):
        return os.path.join(self.data_abspath, "UpCast", "B2BEXCHANGE", "{mig}", "SRC")

    
    @property
    def B2BStorageUpCastSRC(self):
        return os.path.join(self.data_abspath, "UpCast", "B2BSTORAGE", "{mig}", "SRC")

    
    @property
    def B2CStorageUpCastSRC(self):
        return os.path.join(self.data_abspath, "UpCast", "B2CSTORAGE", "{mig}", "SRC")


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
    )
    mig = models.CharField(max_length=5, choices=mig_choices, default='C0401')
    version_choices = (
        ('3.2', 'v32'),
    )
    turnkey_version = models.CharField(max_length=8, choices=version_choices, default='3.2')
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


    def check_in_8_status_then_update_to_the_next(self):
        self.export_to_data_abspath()


    def check_in_9_status_then_update_to_the_next(self):
        self.check_status_of_ei_turnkey_batch_einvoices()
    

    def check_status_of_ei_turnkey_batch_einvoices(self):
        if "9" != self.status:
            return False
        else:
            NEXT_STATUS_IN_GOOD = 'F'
        
        for eitbei in self.eiturnkeybatcheinvoice_set.filter(status__in=["", "P", "G"]):
            eitbei.check_status_from_ei()
        
        if not self.eiturnkeybatcheinvoice_set.exclude(status__in=["I", "E", "C"]).exists():
            seld.update_to_new_status(NEXT_STATUS_IN_GOOD)


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
            try:
                eitbei = self.eiturnkeybatcheinvoice_set.get(batch_einvoice_id=batch_einvoice_id)
            except EITurnkeyBatchEInvoice.DoesNotExist:
                if EITurnkeyBatchEInvoice.objects.filter(status__in=["G", "C"],
                                                         batch_einvoice_begin_time=batch_einvoice_begin_time,
                                                         batch_einvoice_end_time=batch_einvoice_end_time,
                                                         batch_einvoice_track_no=batch_einvoice_track_no,
                                                        ).exists():
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
            if "" != eitbei.body or "" != eitbei.status or "" != eitbei.result_code:
                pass
            else:
                eitbei.batch_einvoice_track_no = batch_einvoice_track_no
                eitbei.batch_einvoice_begin_time = batch_einvoice_begin_time
                eitbei.batch_einvoice_end_time = batch_einvoice_end_time
                eitbei.save_body_time = now()
                eitbei.body = body
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
        else:
            NEXT_STATUS_IN_GOOD = '9'

        tmp_data_path = os.path.join(self.ei_turnkey.tmpdata_abspath, self.slug)
        pathlib.Path(tmp_data_path).mkdir(parents=True, exist_ok=True)
        for eitbei in self.eiturnkeybatcheinvoice_set.filter(result_code='', pass_if_error=False):
            tmp_file_path = os.path.join(tmp_data_path,
                "{routing_id}_{mig}_{version}_{track_no}.xml".format(routing_id=self.ei_turnkey.routing_id,
                                                                     mig=self.mig,
                                                                     version=self.get_turnkey_version_display(),
                                                                     track_no=eitbei.batch_einvoice_track_no))
            f = open(tmp_file_path, 'w')
            f.write(eitbei.mig_xml)
            f.close()
        for f in glob.glob(os.path.join(tmp_data_path, "*")):
            shutil.move(f, self.ei_turnkey.B2CStorageUpCastSRC.format(mig=self.mig))
        
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
        
        result_code_d = {}
        for d in self.eiturnkeybatcheinvoice_set.exclude(result_code=''
                                                        ).values('result_code'
                                                                ).annotate(result_code_count=Count('result_code')):
            result_code_d[d['result_code']] = self.eiturnkeybatcheinvoice_set.filter(result_code=d['result_code']
                                                                                    ).values_list('batch_einvoice_id',
                                                                                                  named=False,
                                                                                                  flat=True)

        return {
            "status": status_d,
            "result_code": result_code_d,
        }



class EITurnkeyBatchEInvoice(models.Model):
    ei_turnkey_batch = models.ForeignKey(EITurnkeyBatch, on_delete=models.DO_NOTHING)
    batch_einvoice_id = models.PositiveIntegerField(default=0)
    batch_einvoice_begin_time = models.DateTimeField()
    batch_einvoice_end_time = models.DateTimeField()
    batch_einvoice_track_no = models.CharField(max_length=10)
    status_choices = (
        ("", _("Waiting")),
        ("P", _("Preparing for EI(P)")),
        ("G", _("Uploaded to EI or Downloaded from EI(G)")),
        ("E", _("E Error for EI process(E)")),
        ("I", _("I Error for EI process(I)")),
        ("C", _("Successful EI process(C)")),
    )
    status = models.CharField(max_length=1, default="", choices=status_choices, db_index=True)
    save_body_time = models.DateTimeField()
    body = models.JSONField(default="")
    result_code = models.CharField(max_length=5, default="", db_index=True)


    @property
    def mig_xml(self):
        for k, v in self.body.items():
            if 'C0401' == k:
                j2mx = C0401JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'C0501' == k:
                j2mx = C0501JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            elif 'C0701' == k:
                j2mx = C0701JSON2MIGXMl(v, version=self.ei_turnkey_batch.turnkey_version)
            return j2mx.export_xml()


    def check_status_from_ei(self):
        invoice_identifier = "{mig}{batch_einvoice_track_no}{InvoiceDate}".format(
            mig=self.ei_turnkey_batch.mig,
            batch_einvoice_track_no=self.batch_einvoice_track_no,
            InvoiceDate=self.body[self.ei_turnkey_batch.mig]["Main"]["InvoiceDate"],
        )
        SAVE_BODY_TIME_DTS = self.save_body_time.astimezone(TAIPEI_TIMEZONE).strftime('%Y%m%d%H%M%S000')
        try:
            nearest_TURNKEY_MESSAGE_LOG = TURNKEY_MESSAGE_LOG.objects.filter(INVOICE_IDENTIFIER=invoice_identifier,
                                                                             MESSAGE_DTS__gte=SAVE_BODY_TIME_DTS
                                                                            ).order_by('MESSAGE_DTS')[0]
        except IndexError:
            return
        else:
            if "" == nearest_TURNKEY_MESSAGE_LOG.STATUS:
                return
            elif nearest_TURNKEY_MESSAGE_LOG.STATUS in ["P", "G", "C"]:
                self.status = nearest_TURNKEY_MESSAGE_LOG.STATUS
            elif nearest_TURNKEY_MESSAGE_LOG.STATUS.startswith('E'):
                self.status = 'E'
                self.result_code = nearest_TURNKEY_MESSAGE_LOG.STATUS
            else:
                self.status = 'I'
                self.result_code = nearest_TURNKEY_MESSAGE_LOG.STATUS
            self.save()
            return self.status



XML_VERSION_RE = re.compile('<\?xml +version=[\'"][0-9\.]+[\'"][^>]+>', re.I)
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
    

    def export_xml(self):
        return self.base_xml.format(version=self.version, xml_body=self.get_xml_body())

    
    def get_xml_body(self):
        xml_body = ''
        for elm in ["Main", "Details", "Amount"]:
            xml = json2xml.Json2xml(self.json_data[elm], wrapper=elm, pretty=False, item_wrap=False, attr_type=False).to_xml()
            xml_body += XML_VERSION_RE.sub("", xml.decode('utf-8'))
        return xml_body


class C0501JSON2MIGXMl(object):
    """<CancelInvoice xmlns="urn:GEINV:eInvoiceMessage:C0501:3.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:C0501:3.1 C0501.xsd">
</CancelInvoice>"""
    def __init__(self, json_data):
        pass



class C0701JSON2MIGXMl(object):
    """<VoidInvoice xmlns="urn:GEINV:eInvoiceMessage:C0701:3.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:GEINV:eInvoiceMessage:C0701:3.1 C0701.xsd">
</VoidInvoice>"""
    def __init__(self, json_data):
        pass