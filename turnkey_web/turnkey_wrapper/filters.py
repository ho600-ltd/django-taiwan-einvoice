import re, datetime
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, utc
from django.utils.translation import ugettext as _

from turnkey_wrapper.models import (
    FROM_CONFIG,
    TASK_CONFIG,
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
        }



class SIGN_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = SIGN_CONFIG
        fields = {
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
        }



class TURNKEY_MESSAGE_LOGFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_MESSAGE_LOG
        fields = {
        }



class TURNKEY_MESSAGE_LOG_DETAILFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_MESSAGE_LOG_DETAIL
        fields = {
        }



class TURNKEY_SEQUENCEFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_SEQUENCE
        fields = {
        }



class TURNKEY_SYSEVENT_LOGFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_SYSEVENT_LOG
        fields = {
        }



class TURNKEY_TRANSPORT_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_TRANSPORT_CONFIG
        fields = {
        }



class TURNKEY_USER_PROFILEFilter(filters.FilterSet):
    class Meta:
        model = TURNKEY_USER_PROFILE
        fields = {
        }
