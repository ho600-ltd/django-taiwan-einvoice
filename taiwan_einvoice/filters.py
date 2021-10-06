import rest_framework_filters as filters

from django.utils.timezone import now
from django.utils.translation import ugettext as _

from taiwan_einvoice.models import SellerInvoiceTrackNo


class SellerInvoiceTrackNoFilter(filters.FilterSet):
    now_use = filters.BooleanFilter(method='filter_now_use')



    class Meta:
        model = SellerInvoiceTrackNo
        fields = {
            'type': ('exact', ),
        }



    def filter_now_use(self, queryset, name, value):
        if value == 'true':
            _now = now()
            ids = []
            for sitn in queryset.filter(begin_time__lte=_now, end_time__gt=_now):
                if sitn.count_blank_no > 0:
                    ids.append(sitn.id)
            queryset = queryset.filter(id__in=ids)
        return queryset