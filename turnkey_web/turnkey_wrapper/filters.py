import re, datetime
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, utc
from django.utils.translation import gettext as _

from turnkey_wrapper.models import (
    TAIPEI_TIMEZONE,

    FROM_CONFIG,
    SCHEDULE_CONFIG,
    SIGN_CONFIG,
    TASK_CONFIG,
    TO_CONFIG,
    TURNKEY_MESSAGE_LOG,
    TURNKEY_MESSAGE_LOG_DETAIL,
    TURNKEY_SEQUENCE,
    TURNKEY_SYSEVENT_LOG,
    TURNKEY_TRANSPORT_CONFIG,
    TURNKEY_USER_PROFILE,

    EITurnkey,
    EITurnkeyBatch,
    EITurnkeyBatchEInvoice,
    EITurnkeyDailySummaryResultXML,
    EITurnkeyDailySummaryResult,
    EITurnkeyE0501XML,
    EITurnkeyE0501InvoiceAssignNo,
)


class FROM_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = FROM_CONFIG
        fields = {
            'TRANSPORT_ID': ('icontains', ),
            'PARTY_ID': ('icontains', ),
        }



class SCHEDULE_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = SCHEDULE_CONFIG
        fields = {
            "TASK": ('icontains', ),
            "ENABLE": ('icontains', ),
        }



class SIGN_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = SIGN_CONFIG
        fields = {
            "SIGN_ID": ('icontains', ),
            "SIGN_TYPE": ('icontains', ),
        }



class TASK_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = TASK_CONFIG
        fields = {
            'CATEGORY_TYPE': ('icontains', ),
            'PROCESS_TYPE': ('icontains', ),
            'TASK': ('icontains', ),
        }



class TO_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = TO_CONFIG
        fields = {
            "FROM_PARTY_ID_PARTY_ID": ("icontains", ),
            "ROUTING_ID": ("icontains", ),
        }



class TURNKEY_MESSAGE_LOGFilter(filters.FilterSet):
    MESSAGE_DTS__gte = filters.DateTimeFilter(method='filter_MESSAGE_DTS__gte')
    MESSAGE_DTS__lt = filters.DateTimeFilter(method='filter_MESSAGE_DTS__lt')


    class Meta:
        model = TURNKEY_MESSAGE_LOG
        fields = {
            "SEQNO": ("icontains", ),
            "SUBSEQNO": ("icontains", ),
            "STATUS": ("exact", ),
            "FROM_ROUTING_ID": ("exact", ),
            "INVOICE_IDENTIFIER": ("exact", "icontains", ),
        }


    def filter_MESSAGE_DTS__gte(self, queryset, name, value):
        value_str = value.astimezone(TAIPEI_TIMEZONE).strftime("%Y%m%d%H%M%S000")
        return queryset.filter(MESSAGE_DTS__gte=value_str)
    


    def filter_MESSAGE_DTS__lt(self, queryset, name, value):
        value_str = value.astimezone(TAIPEI_TIMEZONE).strftime("%Y%m%d%H%M%S999")
        return queryset.filter(MESSAGE_DTS__lt=value_str)
    


class TURNKEY_MESSAGE_LOG_DETAILFilter(filters.FilterSet):
    PROCESS_DTS__gte = filters.DateTimeFilter(method='filter_PROCESS_DTS__gte')
    PROCESS_DTS__lt = filters.DateTimeFilter(method='filter_PROCESS_DTS__lt')
    class Meta:
        model = TURNKEY_MESSAGE_LOG_DETAIL
        fields = {
            "SEQNO": ("icontains", ),
            "SUBSEQNO": ("icontains", ),
            "TASK": ("icontains", ),
            "STATUS": ("exact", ),
        }


    def filter_PROCESS_DTS__gte(self, queryset, name, value):
        value_str = value.astimezone(TAIPEI_TIMEZONE).strftime("%Y%m%d%H%M%S000")
        return queryset.filter(PROCESS_DTS__gte=value_str)
    


    def filter_PROCESS_DTS__lt(self, queryset, name, value):
        value_str = value.astimezone(TAIPEI_TIMEZONE).strftime("%Y%m%d%H%M%S999")
        return queryset.filter(PROCESS_DTS__lt=value_str)
    


class TURNKEY_SEQUENCEFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_SEQUENCE
        fields = {
            "SEQUENCE": ("icontains", ),
        }



class TURNKEY_SYSEVENT_LOGFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_SYSEVENT_LOG
        fields = {
            "SEQNO": ("icontains", ),
            "SUBSEQNO": ("icontains", ),
        }



class TURNKEY_TRANSPORT_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_TRANSPORT_CONFIG
        fields = {
            "TRANSPORT_ID": ("icontains", ),
        }



class TURNKEY_USER_PROFILEFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_USER_PROFILE
        fields = {
            "USER_ID": ("icontains", ),
        }



class EITurnkeyFilter(filters.FilterSet):
    class Meta:
        model = EITurnkey
        fields = {
            "transport_id": ("icontains", ),
            "party_id": ("exact", "icontains", ),
            "routing_id": ("icontains", ),
        }



class EITurnkeyBatchFilter(filters.FilterSet):
    ei_turnkey = filters.RelatedFilter(EITurnkeyFilter, field_name='ei_turnkey', queryset=EITurnkey.objects.all())



    class Meta:
        model = EITurnkeyBatch
        fields = {
            "slug": ("icontains", ),
            "mig": ("exact", ),
            "turnkey_version": ("exact", ),
            "status": ("exact", ),
            "create_time": ("gte", "gt", "lte", "lt", ),
            "update_time": ("gte", "gt", "lte", "lt", ),
        }



class EITurnkeyBatchEInvoiceFilter(filters.FilterSet):
    ei_turnkey_batch__ei_turnkey__party_id = filters.CharFilter(method='filter_ei_turnkey_batch__ei_turnkey__party_id')
    ei_turnkey_batch__slug__icontains = filters.CharFilter(method='filter_ei_turnkey_batch__slug__icontains')
    ei_turnkey_batch__mig = filters.CharFilter(method='filter_ei_turnkey_batch__mig')
    in_year_month_range_time = filters.DateTimeFilter(method='filter_in_year_month_range_time')
    


    class Meta:
        model = EITurnkeyBatchEInvoice
        fields = {
            "ei_turnkey_batch": ("exact", ),
            "batch_einvoice_id": ("exact", ),
            "batch_einvoice_track_no": ("exact", "icontains", ),
            "status": ("exact", ),
            "result_code": ("exact", "icontains", ),
        }
    


    def filter_ei_turnkey_batch__ei_turnkey__party_id(self, queryset, name, value):
        return queryset.filter(ei_turnkey_batch__ei_turnkey__party_id=value)
    

    def filter_ei_turnkey_batch__slug__icontains(self, queryset, name, value):
        return queryset.filter(ei_turnkey_batch__slug__icontains=value)
    

    def filter_ei_turnkey_batch__mig(self, queryset, name, value):
        return queryset.filter(ei_turnkey_batch__mig=value)
    

    def filter_in_year_month_range_time(self, queryset, name, value):
        return queryset.filter(batch_einvoice_begin_time__lte=value,
                               batch_einvoice_end_time__gt=value,
                              )



class EITurnkeyDailySummaryResultXMLFilter(filters.FilterSet):
    class Meta:
        model = EITurnkeyDailySummaryResultXML
        fields = {
            "create_time": ("gte", "gt", "lte", "lt", ),
            "ei_turnkey": ("exact", ),
            "abspath": ("exact", "icontains", ),
            "result_date": ("gte", "gt", "lte", "lt", ),
            "is_parsed": ("exact", ),
        }



class EITurnkeyDailySummaryResultFilter(filters.FilterSet):
    class Meta:
        model = EITurnkeyDailySummaryResult
        fields = {
            "ei_turnkey": ("exact", ),
            "result_date": ("gte", "gt", "lte", "lt", ),
        }



class EITurnkeyE0501XMLFilter(filters.FilterSet):
    class Meta:
        model = EITurnkeyE0501XML
        fields = {
            "create_time": ("gte", "gt", "lte", "lt", ),
            "ei_turnkey": ("exact", ),
            "abspath": ("exact", "icontains", ),
            "is_parsed": ("exact", ),
        }



class EITurnkeyE0501InvoiceAssignNoFilter(filters.FilterSet):
    class Meta:
        model = EITurnkeyE0501InvoiceAssignNo
        fields = {
            "create_time": ("gte", "gt", "lte", "lt", ),
            "invoice_type": ("exact", ),
            "year_month": ("exact", ),
            "invoice_track": ("exact", "iexact", ),
            "invoice_begin_no": ("exact", "contains"),
            "invoice_end_no": ("exact", "contains"),
        }