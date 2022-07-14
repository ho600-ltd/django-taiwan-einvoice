from django.db import models
from django.utils.translation import ugettext_lazy as _


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
    execute_abspath = models.CharField(max_length=755)
    data_abspath = models.CharField(max_length=755)
    hash_key = models.CharField(max_length=40)
    transport_id = models.CharField(max_length=10)
    party_id = models.CharField(max_length=10)
    routing_id = models.CharField(max_length=39)
    tea_turnkey_service_endpoint = models.CharField(max_length=755)
    allow_ips = models.JSONField(null=True)
    endpoint = models.CharField(max_length=755, null=True)



class EITurnkeyBatch(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True, db_index=True)
    ei_turnkey = models.ForeignKey(EITurnkey, on_delete=models.DO_NOTHING)
    slug = models.CharField(max_length=14, unique=True)
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
        ('3.2.1', _('3.2.1')),
    )
    turnkey_version = models.CharField(max_length=8, choices=version_choices, default='3.2.1')
    status_choices = (
        ("7", _("Just created")),
        ("8", _("Download from TEA")),
        ("9", _("Export to Data/")),
        ("P", _("Preparing for EI(P)")),
        ("G", _("Uploaded to EI or Downloaded from EI(G)")),
        ("E", _("E Error for EI process(E)")),
        ("I", _("I Error for EI process(I)")),
        ("C", _("Successful EI process(C)")),
        ("M", _("Swith to Successful EI process manually(S-C)")),
    )
    status = models.CharField(max_length=1, default='7', choices=status_choices, db_index=True)



class EITurnkeyBatchEInvoice(models.Model):
    batch = models.ForeignKey(EITurnkeyBatch, on_delete=models.DO_NOTHING)
    body = models.JSONField()
    result_code = models.CharField(max_length=5, default='', db_index=True)
    pass_if_error = models.BooleanField(default=False)

