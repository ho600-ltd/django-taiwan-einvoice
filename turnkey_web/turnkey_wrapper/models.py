from django.db import models


class FROM_CONFIG(models.Model):
    TRANSPORT_ID = models.CharField(db_column='TRANSPORT_ID', max_length=10, blank=True, null=True)
    TRANSPORT_PASSWORD = models.CharField(db_column='TRANSPORT_PASSWORD', max_length=45, blank=True, null=True)
    PARTY_ID = models.CharField(db_column='PARTY_ID', primary_key=True, max_length=10)
    PARTY_DESCRIPTION = models.CharField(db_column='PARTY_DESCRIPTION', max_length=200, blank=True, null=True)
    ROUTING_ID = models.CharField(db_column='ROUTING_ID', max_length=39, blank=True, null=True)
    ROUTING_DESCRIPTION = models.CharField(db_column='ROUTING_DESCRIPTION', max_length=200, blank=True, null=True)
    SIGN_ID = models.CharField(db_column='SIGN_ID', max_length=4, blank=True, null=True)
    SUBSTITUTE_PARTY_ID = models.CharField(db_column='SUBSTITUTE_PARTY_ID', max_length=10, blank=True, null=True, db_index=True)

    class Meta:
        managed = False
        db_table = 'FROM_CONFIG'


class SCHEDULE_CONFIG(models.Model):
    TASK = models.CharField(db_column='TASK', primary_key=True, max_length=30)
    ENABLE = models.CharField(db_column='ENABLE', max_length=1, blank=True, null=True)
    SCHEDULE_TYPE = models.CharField(db_column='SCHEDULE_TYPE', max_length=10, blank=True, null=True)
    SCHEDULE_WEEK = models.CharField(db_column='SCHEDULE_WEEK', max_length=15, blank=True, null=True)
    SCHEDULE_TIME = models.CharField(db_column='SCHEDULE_TIME', max_length=50, blank=True, null=True)
    SCHEDULE_PERIOD = models.CharField(db_column='SCHEDULE_PERIOD', max_length=10, blank=True, null=True)
    SCHEDULE_RANGE = models.CharField(db_column='SCHEDULE_RANGE', max_length=15, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SCHEDULE_CONFIG'


class SIGN_CONFIG(models.Model):
    SIGN_ID = models.CharField(db_column='SIGN_ID', primary_key=True, max_length=4)
    SIGN_TYPE = models.CharField(db_column='SIGN_TYPE', max_length=10, blank=True, null=True)
    PFX_PATH = models.CharField(db_column='PFX_PATH', max_length=100, blank=True, null=True)
    SIGN_PASSWORD = models.CharField(db_column='SIGN_PASSWORD', max_length=60, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SIGN_CONFIG'


class TASK_CONFIG(models.Model):
    CATEGORY_TYPE = models.CharField(db_column='CATEGORY_TYPE', max_length=5, null=False)
    PROCESS_TYPE = models.CharField(db_column='PROCESS_TYPE', max_length=10, null=False)
    TASK = models.CharField(db_column='TASK', max_length=30, null=False)
    SRC_PATH = models.CharField(db_column='SRC_PATH', max_length=200, blank=True, null=True)
    TARGET_PATH = models.CharField(db_column='TARGET_PATH', max_length=200, blank=True, null=True)
    FILE_FORMAT = models.CharField(db_column='FILE_FORMAT', max_length=20, blank=True, null=True)
    VERSION = models.CharField(db_column='VERSION', max_length=5, blank=True, null=True)
    ENCODING = models.CharField(db_column='ENCODING', max_length=15, blank=True, null=True)
    TRANS_CHINESE_DATE = models.CharField(db_column='TRANS_CHINESE_DATE', max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TASK_CONFIG'
        unique_together = (('CATEGORY_TYPE', 'PROCESS_TYPE', 'TASK'),)


class TO_CONFIG(models.Model):
    PARTY_ID = models.CharField(db_column='PARTY_ID', max_length=10, null=False)
    PARTY_DESCRIPTION = models.CharField(db_column='PARTY_DESCRIPTION', max_length=200, blank=True, null=True)
    ROUTING_ID = models.CharField(db_column='ROUTING_ID', max_length=39, blank=True, null=True)
    ROUTING_DESCRIPTION = models.CharField(db_column='ROUTING_DESCRIPTION', max_length=200, blank=True, null=True)
    FROM_PARTY_ID = models.CharField(db_column='FROM_PARTY_ID', max_length=10)

    class Meta:
        managed = False
        db_table = 'TO_CONFIG'
        unique_together = (('FROM_PARTY_ID', 'PARTY_ID'),)


class TURNKEY_MESSAGE_LOG(models.Model):
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

    class Meta:
        managed = False
        db_table = 'TURNKEY_MESSAGE_LOG'
        unique_together = (('SEQNO', 'SUBSEQNO'),)


class TURNKEY_MESSAGE_LOG_DETAIL(models.Model):
    SEQNO = models.CharField(db_column='SEQNO', max_length=8)
    SUBSEQNO = models.CharField(db_column='SUBSEQNO', max_length=5)
    PROCESS_DTS = models.CharField(db_column='PROCESS_DTS', max_length=17, blank=True, null=True)
    TASK = models.CharField(db_column='TASK', max_length=30)
    STATUS = models.CharField(db_column='STATUS', max_length=5, blank=True, null=True)
    FILENAME = models.CharField(db_column='FILENAME', max_length=255, blank=True, null=True, db_index=True)
    UUID = models.CharField(db_column='UUID', max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TURNKEY_MESSAGE_LOG_DETAIL'
        unique_together = (('SEQNO', 'SUBSEQNO', 'TASK'),)


class TURNKEY_SEQUENCE(models.Model):
    SEQUENCE = models.CharField(db_column='SEQUENCE', primary_key=True, max_length=8)

    class Meta:
        managed = False
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

    class Meta:
        managed = False
        db_table = 'TURNKEY_SYSEVENT_LOG'
        index_together = (("SEQNO", "SUBSEQNO"),)


class TURNKEY_TRANSPORT_CONFIG(models.Model):
    TRANSPORT_ID = models.CharField(db_column='TRANSPORT_ID', primary_key=True, max_length=10)
    TRANSPORT_PASSWORD = models.CharField(db_column='TRANSPORT_PASSWORD', max_length=60)

    class Meta:
        managed = False
        db_table = 'TURNKEY_TRANSPORT_CONFIG'


class TURNKEY_USER_PROFILE(models.Model):
    USER_ID = models.CharField(db_column='USER_ID', primary_key=True, max_length=10)
    USER_PASSWORD = models.CharField(db_column='USER_PASSWORD', max_length=100, blank=True, null=True)
    USER_ROLE = models.CharField(db_column='USER_ROLE', max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'TURNKEY_USER_PROFILE'
