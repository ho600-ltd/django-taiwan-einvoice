import re, datetime
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, utc
from django.utils.translation import ugettext as _

from taiwan_einvoice.models import TAIPEI_TIMEZONE, StaffProfile, ESCPOSWeb, Seller, LegalEntity, TurnkeyWeb, SellerInvoiceTrackNo, EInvoice, EInvoicePrintLog


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'username': ('icontains', ),
        }



class StaffProfileFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, field_name='user', queryset=User.objects.filter(staffprofile__isnull=False))



    class Meta:
        model = StaffProfile
        fields = {
            'nickname': ('icontains', ),
            'is_active': ('exact', ),
        }

class ESCPOSWebFilter(filters.FilterSet):
    class Meta:
        model = ESCPOSWeb
        fields = {
            'name': ('exact', 'iexact', 'contains', 'icontains'),
            'slug': ('exact', 'iexact', 'contains', 'icontains'),
        }



class LegalEntityFilter(filters.FilterSet):
    filter_any_words_in_those_fields = (
        'name',
        'address',
        'person_in_charge',
        'telephone_number',
        'facsimile_number',
        'email_address',
        'customer_number_char',
        'role_remark',
    )
    any_words__icontains = filters.CharFilter(method='filter_any_words__icontains')



    class Meta:
        model = LegalEntity
        fields = {
            'identifier': ('contains', 'icontains'),
        }



    def filter_any_words__icontains(self, queryset, name, value):
        querys = [Q(**{"{}__icontains".format(field): value})
                  for field in self.filter_any_words_in_those_fields]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)





class SellerFilter(filters.FilterSet):
    legal_entity = filters.RelatedFilter(LegalEntityFilter, field_name='legal_entity', queryset=LegalEntity.objects.all())



    class Meta:
        model = Seller
        fields = {
        }



class TurnkeyWebFilter(filters.FilterSet):
    filter_any_words_in_those_fields = (
        'name',
        'hash_key',
        'transport_id',
        'party_id',
        'routing_id',
        'qrcode_seed',
        'turnkey_seed',
        'download_seed',
    )
    seller = filters.RelatedFilter(SellerFilter, field_name='seller', queryset=Seller.objects.all())
    any_words__icontains = filters.CharFilter(method='filter_any_words__icontains')



    class Meta:
        model = TurnkeyWeb
        fields = {
            'on_working': ('exact', ),
        }



    def filter_any_words__icontains(self, queryset, name, value):
        querys = [Q(**{"{}__icontains".format(field): value})
                  for field in self.filter_any_words_in_those_fields]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)



class SellerInvoiceTrackNoFilter(filters.FilterSet):
    now_use = filters.BooleanFilter(method='filter_now_use')
    date_in_year_month_range = filters.CharFilter(method='filter_date_in_year_month_range')



    class Meta:
        model = SellerInvoiceTrackNo
        fields = {
            'type': ('exact', ),
            'track': ('icontains', ),
        }



    def filter_now_use(self, queryset, name, value):
        if value == 'true':
            return SellerInvoiceTrackNo.filter_now_use_sitns()
        else:
            return queryset



    def filter_date_in_year_month_range(self, queryset, name, value):
        try:
            d = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=utc)
        except ValueError:
            return queryset
        else:
            return queryset.filter(begin_time__lte=d, end_time__gte=d)



RE_ALPHABET = re.compile('([a-zA-Z]+)', flags=re.I)
RE_DIGIT = re.compile('([0-9]+)')
RE_CODE39_BARCODE = re.compile('^([0-9]{3})([0-1][0-9])([A-Z][A-Z])([0-9]{8})([0-9]{4})$')
class EInvoiceFilter(filters.FilterSet):
    filter_any_words_in_those_fields = (
        'creator__id',
        'creator__first_name',
        'npoban',
        'random_number',
        'generate_no',
        'generate_no_sha1',
        'seller_identifier',
        'seller_name',
        'buyer_identifier',
        'buyer_name',
    )
    filter_product_descriptions = (
        'details__0__Description',
        'details__1__Description',
        'details__2__Description',
        'details__3__Description',
        'details__4__Description',
        'details__5__Description',
        'details__6__Description',
        'details__7__Description',
        'details__8__Description',
        'details__9__Description',
    )
    track_no__icontains = filters.CharFilter(method='filter_track_no__icontains')
    details__description__icontains = filters.CharFilter(method='filter_details__description__icontains')
    code39__exact = filters.CharFilter(method='filter_code39__exact')
    any_words__icontains = filters.CharFilter(method='filter_any_words__icontains')



    class Meta:
        model = EInvoice
        fields = {
            'generate_time': ('gte', 'lt', ),
        }


    def filter_code39__exact(self, queryset, name, value):
        code39_barcode_re = RE_CODE39_BARCODE.search(value)
        if value and not code39_barcode_re:
            queryset = queryset.none()
        else:
            year, month, track, no, random_number = code39_barcode_re.groups()
            year = int(year) + 1911
            month = int(month)
            middle_time = datetime.datetime(year, month, 1, tzinfo=TAIPEI_TIMEZONE)
            queryset = queryset.filter(seller_invoice_track_no__begin_time__lt=middle_time,
                                       seller_invoice_track_no__end_time__gt=middle_time,
                                       track=track,
                                       no=no,
                                       random_number=random_number)
        return queryset


    def filter_track_no__icontains(self, queryset, name, value):
        if value:
            alphabet = ''
            digit = ''
            re_alphabet_re = RE_ALPHABET.search(value)
            if re_alphabet_re:
                alphabet = re_alphabet_re.groups()[0]
            re_digit_re = RE_DIGIT.search(value)
            if re_digit_re:
                digit = re_digit_re.groups()[0]

            if alphabet and digit:
                queryset = queryset.filter(track__iendswith=alphabet, no__startswith=digit)
            else:
                if digit:
                    queryset = queryset.filter(no__contains=digit)
                if alphabet:
                    queryset = queryset.filter(track__icontains=alphabet)
        return queryset


    def filter_any_words__icontains(self, queryset, name, value):
        querys = [Q(**{"{}__icontains".format(field): value})
                  for field in self.filter_any_words_in_those_fields]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)


    def filter_details__description__icontains(self, queryset, name, value):
        querys = [Q(**{"{}__icontains".format(field): value})
                  for field in self.filter_product_descriptions]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)


class EInvoicePrintLogFilter(filters.FilterSet):
    einvoice = filters.RelatedFilter(EInvoiceFilter, field_name='einvoice', queryset=EInvoice.objects.all())
    id_or_hex = filters.CharFilter(method='filter_id_or_hex')



    class Meta:
        model = EInvoicePrintLog
        fields = {
            'id': ('exact', ),
            'is_original_copy': ('exact', ),
            'print_time': ('gte', 'lt', ),
        }



    def filter_id_or_hex(self, queryset, name, value):
        try:
            id = int(value)
        except ValueError:
            try:
                objs = EInvoicePrintLog.get_objs_from_customize_hex(value)
            except EInvoicePrintLog.DoesNotExist:
                return queryset.none()
            else:
                ids = [obj.id for obj in objs]
        else:
            ids = [id]
        return queryset.filter(id__in=ids)