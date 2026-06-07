import re, datetime
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
utc = datetime.timezone.utc
from django.utils.timezone import now
from django.utils.translation import gettext as _


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

