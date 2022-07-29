import re, datetime
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, utc
from django.utils.translation import ugettext as _

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
    MESSAGE_DTS__lte = filters.DateTimeFilter(method='filter_MESSAGE_DTS__lte')


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
    


    def filter_MESSAGE_DTS__lte(self, queryset, name, value):
        value_str = value.astimezone(TAIPEI_TIMEZONE).strftime("%Y%m%d%H%M%S999")
        return queryset.filter(MESSAGE_DTS__lte=value_str)
    


class TURNKEY_MESSAGE_LOG_DETAILFilter(filters.FilterSet):
    PROCESS_DTS__gte = filters.DateTimeFilter(method='filter_PROCESS_DTS__gte')
    PROCESS_DTS__lte = filters.DateTimeFilter(method='filter_PROCESS_DTS__lte')
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
    


    def filter_PROCESS_DTS__lte(self, queryset, name, value):
        value_str = value.astimezone(TAIPEI_TIMEZONE).strftime("%Y%m%d%H%M%S999")
        return queryset.filter(PROCESS_DTS__lte=value_str)
    


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
            "party_id": ("icontains", ),
            "routing_id": ("icontains", ),
        }



class EITurnkeyBatchFilter(filters.FilterSet):
    class Meta:
        model = EITurnkeyBatch
        fields = {
            "slug": ("icontains", ),
            "mig": ("exact", ),
            "turnkey_version": ("exact", ),
            "status": ("exact", ),
        }



class EITurnkeyBatchEInvoiceFilter(filters.FilterSet):
    ei_turnkey_batch__slug__icontains = filters.CharFilter(method='filter_ei_turnkey_batch__slug__icontains')
    ei_turnkey_batch__mig = filters.CharFilter(method='filter_ei_turnkey_batch__mig')
    invoice_number_in_body = filters.CharFilter(method='filter_invoice_number_in_body')
    class Meta:
        model = EITurnkeyBatchEInvoice
        fields = {
            "ei_turnkey_batch": ("exact", ),
            "batch_einvoice_id": ("exact", ),
        }
    


    def filter_ei_turnkey_batch__slug__icontains(self, queryset, name, value):
        return queryset.filter(ei_turnkey_batch__slug__icontains=value)
    

    def filter_ei_turnkey_batch__mig(self, queryset, name, value):
        return queryset.filter(ei_turnkey_batch__mig=value)
    

    def filter_invoice_number_in_body(self, queryset, name, value):
        querys = [Q(**{"body__{}__Main__InvoiceNumber__icontains".format(field): value})
                  for field in ["C0401", "C0501", "C0701"]]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)