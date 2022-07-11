import re, datetime
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, utc
from django.utils.translation import ugettext as _

from turnkey_wrapper.models import (
    FROM_CONFIG,
)


class FROM_CONFIGFilter(filters.FilterSet):
    class Meta:
        model = FROM_CONFIG
        fields = {
            'PARTY_ID': ('icontains', ),
        }
