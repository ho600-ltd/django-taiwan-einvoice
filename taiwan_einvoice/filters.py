import re, datetime, logging
import rest_framework_filters as filters

from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.timezone import now, utc
from django.utils.translation import ugettext as _
from guardian.shortcuts import get_objects_for_user

from taiwan_einvoice.models import (
    TAIPEI_TIMEZONE,
    StaffProfile,
    ESCPOSWeb,
    Seller,
    LegalEntity,
    TurnkeyService,
    SellerInvoiceTrackNo,
    EInvoice,
    Printer,
    EInvoicePrintLog,
    CancelEInvoice,
    VoidEInvoice,
    UploadBatch,
    BatchEInvoice,
    AuditLog,
    SummaryReport,
    TEAlarm,
)


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'username': ('icontains', ),
        }



class PrinterFilter(filters.FilterSet):
    class Meta:
        model = Printer
        fields = {
            'id': ('exact', ),
        }



def can_view_users_by_some_TODO_groups(request):
    #TODO: Don't let managers can see all users
    lg = logging.getLogger('taiwan_einvoice')
    users = User.objects.filter(staffprofile__isnull=False)
    lg.debug("#TODO can_view_users_by_some_TODO_groups: {}".format(users)) 
    return users


class StaffProfileFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, field_name='user', queryset=can_view_users_by_some_TODO_groups)



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
            'identifier': ('exact', 'contains', 'icontains'),
        }



    def filter_any_words__icontains(self, queryset, name, value):
        querys = [Q(**{"{}__icontains".format(field): value})
                  for field in self.filter_any_words_in_those_fields]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)



def legal_entity_under_can_view_turnkey_services(request):
    from taiwan_einvoice.permissions import CanViewTurnkeyService
    lg = logging.getLogger('taiwan_einvoice')
    ts = get_objects_for_user(request.user,
                              CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get("list", []),
                              any_perm=True,
                             )
    legal_entitys = LegalEntity.objects.filter(id__in=ts.values_list('seller__legal_entity', flat=True))
    lg.debug("legal_entity_under_can_view_turnkey_services: {}".format(legal_entitys)) 
    return legal_entitys



class SellerFilter(filters.FilterSet):
    legal_entity = filters.RelatedFilter(LegalEntityFilter, field_name='legal_entity', queryset=legal_entity_under_can_view_turnkey_services)



    class Meta:
        model = Seller
        fields = {
            "legal_entity": ("exact", ),
        }



def sellers_under_can_view_turnkey_services(request):
    from taiwan_einvoice.permissions import CanViewTurnkeyService
    lg = logging.getLogger('taiwan_einvoice')
    ts = get_objects_for_user(request.user,
                              CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get("list", []),
                              any_perm=True,
                             )
    sellers = Seller.objects.filter(id__in=ts.values_list('seller', flat=True))
    lg.debug("sellers_under_can_view_turnkey_services: {}".format(sellers)) 
    return sellers



class TurnkeyServiceFilter(filters.FilterSet):
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
    seller = filters.RelatedFilter(SellerFilter, field_name='seller', queryset=sellers_under_can_view_turnkey_services)
    any_words__icontains = filters.CharFilter(method='filter_any_words__icontains')



    class Meta:
        model = TurnkeyService
        fields = {
            'on_working': ('exact', ),
            'seller': ('exact', ),
            'party_id': ('exact', ),
        }



    def filter_any_words__icontains(self, queryset, name, value):
        querys = [Q(**{"{}__icontains".format(field): value})
                  for field in self.filter_any_words_in_those_fields]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)



class TurnkeyServiceGroupFilter(filters.FilterSet):
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
    seller = filters.RelatedFilter(SellerFilter, field_name='seller', queryset=sellers_under_can_view_turnkey_services)
    any_words__icontains = filters.CharFilter(method='filter_any_words__icontains')



    class Meta:
        model = TurnkeyService
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



def can_view_turnkey_services(request):
    from taiwan_einvoice.permissions import CanViewTurnkeyService
    lg = logging.getLogger('taiwan_einvoice')
    ts =  get_objects_for_user(request.user,
                               CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get("list", []),
                               any_perm=True,
                              )
    lg.debug("can_view_turnkey_services: {}".format(ts)) 
    return ts



class SellerInvoiceTrackNoFilter(filters.FilterSet):
    turnkey_service = filters.RelatedFilter(TurnkeyServiceFilter, field_name='turnkey_service', queryset=can_view_turnkey_services)
    now_use = filters.BooleanFilter(method='filter_now_use')
    date_in_year_month_range = filters.CharFilter(method='filter_date_in_year_month_range')
    no_including = filters.CharFilter(method='filter_no_including')



    class Meta:
        model = SellerInvoiceTrackNo
        fields = {
            'turnkey_service': ('exact', ),
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
    

    def filter_no_including(self, queryset, name, value):
        try:
            value = "{:08d}".format(int(value))
        except ValueError:
            return queryset
        else:
            return queryset.filter(begin_no__lte=value, end_no__gte=value)



def sitns_under_can_view_turnkey_services(request):
    from taiwan_einvoice.permissions import CanViewTurnkeyService
    lg = logging.getLogger('taiwan_einvoice')
    ts =  get_objects_for_user(request.user,
                               CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get("list", []),
                               any_perm=True,
                              )
    sitns = SellerInvoiceTrackNo.objects.filter(turnkey_service__in=ts)
    lg.debug("sitns_under_can_view_turnkey_services: {}".format(sitns)) 
    return sitns



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
    seller_invoice_track_no = filters.RelatedFilter(SellerInvoiceTrackNoFilter, field_name='seller_invoice_track_no', queryset=sitns_under_can_view_turnkey_services)
    track_no__icontains = filters.CharFilter(method='filter_track_no__icontains')
    details__description__icontains = filters.CharFilter(method='filter_details__description__icontains')
    code39__exact = filters.CharFilter(method='filter_code39__exact')
    any_words__icontains = filters.CharFilter(method='filter_any_words__icontains')
    cancel_einvoice_type = filters.CharFilter(method='filter_cancel_einvoice_type')



    class Meta:
        model = EInvoice
        fields = {
            'generate_time': ('gte', 'lt', ),
            'print_mark': ('exact', ),
            'carrier_type': ('exact', 'regex'),
            'npoban': ('regex', ),
            'reverse_void_order': ('exact', 'gte', 'gt', 'lte', 'lt'),
            'ei_synced': ('exact', ),
            'buyer_identifier': ('icontains', ),
        }


    def filter_cancel_einvoice_type(self, queryset, name, value):
        if value not in ['n', 'c', 'o']:
            queryset = queryset.none()
        elif 'n' == value:
            queryset = queryset.filter(canceleinvoice__isnull=True)
        elif 'c' == value:
            queryset = queryset.filter(canceleinvoice__isnull=False,
                                       canceleinvoice__in=CancelEInvoice.objects.filter(new_einvoice__isnull=True))
        elif 'o' == value:
            queryset = queryset.filter(canceleinvoice__isnull=False,
                                       canceleinvoice__in=CancelEInvoice.objects.filter(new_einvoice__isnull=False))
        return queryset


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



def einvoices_under_can_view_turnkey_services(request):
    from taiwan_einvoice.permissions import CanViewTurnkeyService
    lg = logging.getLogger('taiwan_einvoice')
    ts =  get_objects_for_user(request.user,
                               CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get("list", []),
                               any_perm=True,
                              )
    einvoices = EInvoice.objects.filter(seller_invoice_track_no__turnkey_service__in=ts)
    lg.debug("einvoices_under_can_view_turnkey_services: {}".format(einvoices)) 
    return einvoices



class EInvoicePrintLogFilter(filters.FilterSet):
    einvoice = filters.RelatedFilter(EInvoiceFilter, field_name='einvoice', queryset=einvoices_under_can_view_turnkey_services)
    printer = filters.RelatedFilter(PrinterFilter, field_name='printer', queryset=Printer.objects.all())
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



class CancelEInvoiceFilter(filters.FilterSet):
    einvoice__track_no__icontains = filters.CharFilter(method='filter_einvoice__track_no__icontains')
    einvoice__details__description__icontains = filters.CharFilter(method='filter_einvoice__details__description__icontains')
    einvoice__code39__exact = filters.CharFilter(method='filter_einvoice__code39__exact')
    einvoice__any_words__icontains = filters.CharFilter(method='filter_einvoice__any_words__icontains')
    new_einvoice__track_no__icontains = filters.CharFilter(method='filter_new_einvoice__track_no__icontains')



    class Meta:
        model = CancelEInvoice
        fields = {
            'generate_time': ('gte', 'lt', ),
            'ei_synced': ('exact', ),
        }


    def filter_einvoice__any_words__icontains(self, queryset, name, value):
        querys = [Q(**{"einvoice__{}__icontains".format(field): value})
                  for field in EInvoiceFilter.filter_any_words_in_those_fields]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)


    def filter_einvoice__details__description__icontains(self, queryset, name, value):
        querys = [Q(**{"einvoice__{}__icontains".format(field): value})
                  for field in EInvoiceFilter.filter_product_descriptions]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)


    def filter_einvoice__code39__exact(self, queryset, name, value):
        code39_barcode_re = RE_CODE39_BARCODE.search(value)
        if value and not code39_barcode_re:
            queryset = queryset.none()
        else:
            year, month, track, no, random_number = code39_barcode_re.groups()
            year = int(year) + 1911
            month = int(month)
            middle_time = datetime.datetime(year, month, 1, tzinfo=TAIPEI_TIMEZONE)
            queryset = queryset.filter(einvoice__seller_invoice_track_no__begin_time__lt=middle_time,
                                       einvoice__seller_invoice_track_no__end_time__gt=middle_time,
                                       einvoice__track=track,
                                       einvoice__no=no,
                                       einvoice__random_number=random_number)
        return queryset


    def filter_einvoice__track_no__icontains(self, queryset, name, value):
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
                queryset = queryset.filter(einvoice__track__iendswith=alphabet, einvoice__no__startswith=digit)
            else:
                if digit:
                    queryset = queryset.filter(einvoice__no__contains=digit)
                if alphabet:
                    queryset = queryset.filter(einvoice__track__icontains=alphabet)
        return queryset


    def filter_new_einvoice__track_no__icontains(self, queryset, name, value):
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
                queryset = queryset.filter(new_einvoice__track__iendswith=alphabet, new_einvoice__no__startswith=digit)
            else:
                if digit:
                    queryset = queryset.filter(new_einvoice__no__contains=digit)
                if alphabet:
                    queryset = queryset.filter(new_einvoice__track__icontains=alphabet)
        return queryset



class VoidEInvoiceFilter(filters.FilterSet):
    einvoice__track_no__icontains = filters.CharFilter(method='filter_einvoice__track_no__icontains')
    einvoice__code39__exact = filters.CharFilter(method='filter_einvoice__code39__exact')
    einvoice__details__description__icontains = filters.CharFilter(method='filter_einvoice__details__description__icontains')
    einvoice__any_words__icontains = filters.CharFilter(method='filter_einvoice__any_words__icontains')



    class Meta:
        model = VoidEInvoice
        fields = {
            'generate_time': ('gte', 'lt', ),
            'ei_synced': ('exact', ),
        }


    def filter_einvoice__any_words__icontains(self, queryset, name, value):
        querys = [Q(**{"einvoice__{}__icontains".format(field): value})
                  for field in EInvoiceFilter.filter_any_words_in_those_fields]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)


    def filter_einvoice__details__description__icontains(self, queryset, name, value):
        querys = [Q(**{"einvoice__{}__icontains".format(field): value})
                  for field in EInvoiceFilter.filter_product_descriptions]
        query = querys.pop()
        for q in querys:
            query |= q
        return queryset.filter(query)


    def filter_einvoice__code39__exact(self, queryset, name, value):
        code39_barcode_re = RE_CODE39_BARCODE.search(value)
        if value and not code39_barcode_re:
            queryset = queryset.none()
        else:
            year, month, track, no, random_number = code39_barcode_re.groups()
            year = int(year) + 1911
            month = int(month)
            middle_time = datetime.datetime(year, month, 1, tzinfo=TAIPEI_TIMEZONE)
            queryset = queryset.filter(einvoice__seller_invoice_track_no__begin_time__lt=middle_time,
                                       einvoice__seller_invoice_track_no__end_time__gt=middle_time,
                                       einvoice__track=track,
                                       einvoice__no=no,
                                       einvoice__random_number=random_number)
        return queryset


    def filter_einvoice__track_no__icontains(self, queryset, name, value):
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
                queryset = queryset.filter(einvoice__track__iendswith=alphabet, einvoice__no__startswith=digit)
            else:
                if digit:
                    queryset = queryset.filter(einvoice__no__contains=digit)
                if alphabet:
                    queryset = queryset.filter(einvoice__track__icontains=alphabet)
        return queryset



class UploadBatchFilter(filters.FilterSet):
    turnkey_service = filters.RelatedFilter(TurnkeyServiceFilter, field_name='turnkey_service', queryset=can_view_turnkey_services)
    mig_type__no = filters.CharFilter(method='filter_mig_type__no')



    class Meta:
        model = UploadBatch
        fields = {
            "slug": ("exact", "icontains", ),
            "create_time": ("gte", "lt", ),
            "kind": ("exact", ),
            "status": ("exact", ),
        }


    def filter_mig_type__no(self, queryset, name, value):
        if value:
            queryset = queryset.filter(mig_type__no=value)
        return queryset

        

def upload_batchs_under_can_view_turnkey_services(request):
    from taiwan_einvoice.permissions import CanViewTurnkeyService
    lg = logging.getLogger('taiwan_einvoice')
    ts =  get_objects_for_user(request.user,
                               CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get("list", []),
                               any_perm=True,
                              )
    ubs = UploadBatch.objects.filter(turnkey_service__in=ts)
    lg.debug("upload_batchs_under_can_view_turnkey_services: {}".format(ubs)) 
    return ubs



class BatchEInvoiceFilter(filters.FilterSet):
    batch = filters.RelatedFilter(UploadBatchFilter, field_name='batch', queryset=upload_batchs_under_can_view_turnkey_services)



    class Meta:
        model = BatchEInvoice
        fields = {
            "track_no": ("icontains", ),
            "status": ("exact", "regex", ),
            "pass_if_error": ("exact", ),
        }



class AuditLogFilter(filters.FilterSet):
    class Meta:
        model = AuditLog
        fields = {
            "create_time": ("gte", "gt", "lte", "lt"),
            "turnkey_service": ("exact", ),
            "is_error": ("exact", ),
        }



class SummaryReportFilter(filters.FilterSet):
    class Meta:
        model = SummaryReport
        fields = {
            "create_time": ("gte", "gt", "lte", "lt"),
            "turnkey_service": ("exact", ),
            "begin_time": ("gte", "gt", "lte", "lt"),
            "end_time": ("gte", "gt", "lte", "lt"),
            "report_type": ("exact", ),
            "good_count": ("gte", "gt", "lte", "lt"),
            "failed_count": ("gte", "gt", "lte", "lt"),
            "resolved_count": ("gte", "gt", "lte", "lt"),
            "is_resolved": ("exact", ),
            "resolved_note": ("exact", "icontains"),
        }



class TEAlarmFilter(filters.FilterSet):
    class Meta:
        model = TEAlarm
        fields = {
            "create_time": ("gte", "gt", "lte", "lt"),
            "turnkey_service": ("exact", ),
            "target_audience_type": ("exact", ),
            "title": ("exact", 'icontains', ),
            "body": ("exact", 'icontains', ),
        }