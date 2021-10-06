import rest_framework_filters as filters

from django.utils.timezone import now
from django.utils.translation import ugettext as _

from taiwan_einvoice.models import TurnkeyWeb, SellerInvoiceTrackNo


class TurnkeyWebFilter(filters.FilterSet):
    class Meta:
        model = TurnkeyWeb
        fields = {
            'on_working': ('exact', ),
        }



class SellerInvoiceTrackNoFilter(filters.FilterSet):
    now_use = filters.BooleanFilter(method='filter_now_use')



    class Meta:
        model = SellerInvoiceTrackNo
        fields = {
            'type': ('exact', ),
        }



    def filter_now_use(self, queryset, name, value):
        if value == 'true':
            return SellerInvoiceTrackNo.filter_now_use_sitns()
        else:
            return queryset