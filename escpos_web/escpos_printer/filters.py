import re, datetime
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, utc
from django.utils.translation import ugettext as _


from escpos_printer.models import Printer, TEAWeb



class PrinterFilter(filters.FilterSet):
    class Meta:
        model = Printer
        fields = {
            'serial_number': ('icontains', ),
            'nickname': ('icontains', ),
            'profile': ('exact', ),
            'receipt_type': ('exact', ),
            'default_encoding': ('exact', ),
        }


class TEAWebFilter(filters.FilterSet):
    class Meta:
        model = TEAWeb
        fields = {
            'name': ('icontains', ),
            'slug': ('icontains', ),
        }

