import json, datetime, logging, re
from django.conf import settings
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import Permission, User, Group
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now, utc
from django.utils.translation import gettext_lazy as _

from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms, remove_perm, assign_perm

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ho600_lib.permissions import Or

from taiwan_einvoice.permissions import (
    IsSuperUser,
    CanEditTEAStaffProfile,
    CanViewSelfTEAStaffProfile,
    CanOperateESCPOSWebOperator,
    CanEditESCPOSWebOperator,
    CanEditTurnkeyServiceGroup,
    CanEntrySellerInvoiceTrackNo,
    CanViewE0501InvoiceAssignNo,
    CanEntryEInvoice,
    CanEntryEInvoicePrintLog,
    CanEntryCancelEInvoice,
    CanEntryVoidEInvoice,
    CanViewLegalEntity,
    CanViewTurnkeyService,
    CanViewBatchEInvoice,
    CanViewSummaryReport,
    CanViewTEAlarmForProgrammer,
    CanViewTEAlarmForGeneralUser,
)
from taiwan_einvoice.renderers import (
    TEBrowsableAPIRenderer,
    TEAStaffProfileHtmlRenderer,
    ESCPOSWebHtmlRenderer,
    ESCPOSWebOperatorHtmlRenderer,
    TurnkeyServiceHtmlRenderer,
    TurnkeyServiceGroupHtmlRenderer,
    LegalEntityHtmlRenderer,
    SellerInvoiceTrackNoHtmlRenderer,
    EInvoiceHtmlRenderer,
    EInvoicePrintLogHtmlRenderer,
    CancelEInvoiceHtmlRenderer,
    VoidEInvoiceHtmlRenderer,
    AuditLogHtmlRenderer,
    UploadBatchHtmlRenderer,
    BatchEInvoiceHtmlRenderer,
    SummaryReportHtmlRenderer,
    TEAlarmHtmlRenderer,
)
from taiwan_einvoice.models import (
    _year_to_chmk_year,
    TAIPEI_TIMEZONE,
    EInvoiceSellerAPI,
    TEAStaffProfile,
    ESCPOSWeb,
    LegalEntity,
    Seller,
    TurnkeyService,
    SellerInvoiceTrackNo, NotEnoughNumberError, UsedSellerInvoiceTrackNoError, ExcutedE0402UploadBatchError, ExistedE0402UploadBatchError,
    E0501InvoiceAssignNo,
    EInvoiceMIG,
    EInvoice,
    EInvoicePrintLog,
    CancelEInvoice,
    VoidEInvoice,
    IdentifierRule,
    UploadBatch,
    BatchEInvoice,
    AuditLog,
    SummaryReport,
    TEAlarm,
)
from taiwan_einvoice.serializers import (
    TEAStaffProfileSerializer,
    StaffGroupSerializer,
    ESCPOSWebSerializer,
    ESCPOSWebOperatorSerializer,
    LegalEntitySerializerForUser,
    LegalEntitySerializerForSuperUser,
    SellerSerializer,
    TurnkeyServiceSerializer,
    TurnkeyServiceGroupSerializer,
    SellerInvoiceTrackNoSerializer,
    E0501InvoiceAssignNoSerializer,
    EInvoiceSerializer,
    EInvoicePrintLogSerializer,
    CancelEInvoiceSerializer,
    VoidEInvoiceSerializer,
    UploadBatchSerializer,
    BatchEInvoiceSerializer,
    AuditLogSerializer,
    SummaryReportSerializer,
    TEAlarmSerializer,
)
from taiwan_einvoice.filters import (
    TEAStaffProfileFilter,
    ESCPOSWebFilter,
    SellerFilter,
    LegalEntityFilter,
    TurnkeyServiceFilter,
    TurnkeyServiceGroupFilter,
    SellerInvoiceTrackNoFilter,
    E0501InvoiceAssignNoFilter,
    EInvoiceFilter,
    EInvoicePrintLogFilter,
    CancelEInvoiceFilter,
    VoidEInvoiceFilter,
    UploadBatchFilter,
    BatchEInvoiceFilter,
    AuditLogFilter,
    SummaryReportFilter,
    TEAlarmFilter,
)
from taiwan_einvoice.paginations import (
    Default30PerPagePagination,
    TenTo100PerPagePagination,
    TenTo1000PerPagePagination,
)



class OneHundredPerPagePagination(TenTo100PerPagePagination):
    page_size = 100



def index(request):
    escpos_webs = ESCPOSWeb.objects.all().order_by('id')
    return render(request, 'taiwan_einvoice/index.html', {
        'escpos_webs': escpos_webs
    })


def escpos_web_demo(request, escpos_web_id):
    try:
        escpos_web = ESCPOSWeb.objects.get(id=escpos_web_id)
    except ESCPOSWeb.DoesNotExist:
        raise Http404("ESCPOS Web does not exist!")
    return render(request,
                  'taiwan_einvoice/escpos_web_demo.html',
                  {"escpos_web": escpos_web})



class TEAStaffProfileModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditTEAStaffProfile, CanViewSelfTEAStaffProfile), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TEAStaffProfile.objects.all().order_by('-id')
    serializer_class = TEAStaffProfileSerializer
    filter_class = TEAStaffProfileFilter
    renderer_classes = (TEAStaffProfileHtmlRenderer, TEBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('post', 'get', 'patch')


    def create(self, request, *args, **kwargs):
        data = request.data
        if TEAStaffProfile.objects.filter(user__username=data['user.username']).exists():
            er = {
                "error_title": _("Staff exist"),
                "error_message": _("Staff exist"),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        try:
            data['user'] = User.objects.get(username=data['user.username']).id
        except User.DoesNotExist:
            er = {
                "error_title": _("Username does not exist"),
                "error_message": _("Please check the username, this field is case-sensitive"),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        else:
            del data['user.username']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        serializer = TEAStaffProfileSerializer(serializer.instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class ESCPOSWebModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditESCPOSWebOperator, CanOperateESCPOSWebOperator), )
    pagination_class = TenTo100PerPagePagination
    queryset = ESCPOSWeb.objects.all().order_by('-id')
    serializer_class = ESCPOSWebSerializer
    filter_class = ESCPOSWebFilter
    renderer_classes = (ESCPOSWebHtmlRenderer, TEBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('post', 'get', )


    def get_queryset(self):
        request = self.request
        queryset = super().get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        res = request.user.is_superuser
        if res:
            return queryset
        else:
            for _p in CanEditESCPOSWebOperator.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
            if res:
                return queryset
            else:
                objs = get_objects_for_user(request.user,
                                            CanOperateESCPOSWebOperator.METHOD_PERMISSION_MAPPING.get(request.method, []),
                                            any_perm=True)
                return objs



class ESCPOSWebOperatorModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditESCPOSWebOperator), )
    pagination_class = TenTo100PerPagePagination
    queryset = ESCPOSWeb.objects.all().order_by('-id')
    serializer_class = ESCPOSWebOperatorSerializer
    filter_class = ESCPOSWebFilter
    renderer_classes = (ESCPOSWebOperatorHtmlRenderer, TEBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', 'patch', )


    def get_queryset(self):
        request = self.request
        queryset = super().get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        res = False
        for _p in CanEditESCPOSWebOperator.METHOD_PERMISSION_MAPPING.get(request.method, []):
            res = request.user.has_perm(_p)
            if res:
                break
        if res:
            return queryset
        else:
            objs = get_objects_for_user(request.user,
                                        CanEditESCPOSWebOperator.METHOD_PERMISSION_MAPPING.get(request.method, []),
                                        any_perm=True)
            return objs
    

    def update(self, request, *args, **kwargs):
        lg = logging.getLogger('info')
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        escposweb = self.get_object()
        if 'remove' == data['type']:
            try:
                sp = TEAStaffProfile.objects.get(id=data['teastaffprofile_id'])
            except TEAStaffProfile.DoesNotExist:
                pass
            else:
                ct = ContentType.objects.get(app_label='taiwan_einvoice', model='escposweb')
                p = Permission.objects.get(content_type=ct, codename='operate_te_escposweb')
                remove_perm(p, sp.user, escposweb)
        elif 'add' == data['type']:
            ct = ContentType.objects.get(app_label='taiwan_einvoice', model='escposweb')
            p = Permission.objects.get(content_type=ct, codename='operate_te_escposweb')
            for teastaffprofile_id in data['teastaffprofile_ids']:
                try:
                    sp = TEAStaffProfile.objects.get(id=teastaffprofile_id)
                except TEAStaffProfile.DoesNotExist:
                    continue
                else:
                    assign_perm(p, sp.user, escposweb)
        serializer = ESCPOSWebOperatorSerializer(self.get_object(), context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class LegalEntityModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewLegalEntity), )
    pagination_class = TenTo100PerPagePagination
    queryset = LegalEntity.objects.all().order_by('-id')
    serializer_class = None
    filter_class = LegalEntityFilter
    renderer_classes = (LegalEntityHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'patch')

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return LegalEntitySerializerForSuperUser
        return LegalEntitySerializerForUser



class SellerModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo100PerPagePagination
    queryset = Seller.objects.all().order_by('-id')
    serializer_class = SellerSerializer
    filter_class = SellerFilter
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'patch')



class TurnkeyServiceModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewTurnkeyService), )
    pagination_class = TenTo100PerPagePagination
    queryset = TurnkeyService.objects.all().order_by('-id')
    serializer_class = TurnkeyServiceSerializer
    filter_class = TurnkeyServiceFilter
    renderer_classes = (TurnkeyServiceHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'patch')


    def get_queryset(self):
        request = self.request
        queryset = super(TurnkeyServiceModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get(self.action, [])
            turnkey_service_ids = get_objects_for_user(request.user,
                                                       permissions,
                                                       any_perm=True).values_list('id',
                                                                                  flat=True)
            return queryset.filter(id__in=turnkey_service_ids)


    @action(detail=True, methods=['get'], renderer_classes=[JSONRenderer, ])
    def get_and_create_ei_turnkey_daily_summary_result(self, request, pk=None):
        ts = self.get_object()
        if ts:
            result_date = request.GET.get('result_date', '')
            try:
                _dev_null = datetime.datetime.strptime(result_date, "%Y-%m-%d")
            except:
                pass
            else:
                result_json = ts.get_and_create_ei_turnkey_daily_summary_result(result_date)
                return Response(result_json)
        return Response({"error_title": _("Turnkey Service Error"),
                            "error_message": _("{} does not exist").format(pk),
                        }, status=status.HTTP_403_FORBIDDEN)



class TurnkeyServiceGroupModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditTurnkeyServiceGroup), )
    pagination_class = Default30PerPagePagination
    queryset = TurnkeyService.objects.all().order_by('-id')
    serializer_class = TurnkeyServiceGroupSerializer
    filter_class = TurnkeyServiceGroupFilter
    renderer_classes = (TurnkeyServiceGroupHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', 'patch')


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        turnkeyservice = self.get_object()
        if 'delete_group' == data['type']:
            try:
                g = Group.objects.get(id=data['group_id'])
            except Group.DoesNotExist:
                pass
            else:
                g.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        elif 'add_group' == data['type']:
            if len(turnkeyservice.groups) >= self.pagination_class.page_size:
                er = {
                    "error_title": _("The count of Existed Groups exceeds the limit"),
                    "error_message": _("The count of Existed Groups exceeds the limit({})").format(self.pagination_class.page_size),
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
            ct_id = ContentType.objects.get_for_model(turnkeyservice).id
            group_name = "ct{ct_id}:{id}:{name}".format(ct_id=ct_id, id=turnkeyservice.id, name=data['display_name'])
            g, created = Group.objects.get_or_create(name=group_name)
            if created:
                serializer = StaffGroupSerializer(g, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                er = {
                    "error_title": _("Group name exists"),
                    "error_message": _("Group name exists"),
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
        elif 'update_group' == data['type']:
            try:
                g = Group.objects.get(id=data['group_id'])
            except Group.DoesNotExist:
                pass
            else:
                ct = ContentType.objects.get_for_model(turnkeyservice)
                group_name = "ct{ct_id}:{id}:{name}".format(ct_id=ct.id, id=turnkeyservice.id, name=data['display_name'])
                g.name = group_name
                g.save()
                for k, v in data['permissions'].items():
                    if "edit_te_turnkeyservicegroup" == k and not request.user.is_superuser:
                        continue

                    try:
                        p = Permission.objects.get(content_type=ct, codename=k)
                    except Permission.DoesNotExist:
                        p = Permission.objects.get(codename=k)
                        target_obj = None
                    else:
                        target_obj = turnkeyservice
                    if v:
                        assign_perm(p, g, obj=target_obj)
                    else:
                        remove_perm(p, g, obj=target_obj)
                return Response({}, status=status.HTTP_200_OK)



class SellerInvoiceTrackNoModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEntrySellerInvoiceTrackNo, ), )
    pagination_class = OneHundredPerPagePagination
    queryset = SellerInvoiceTrackNo.objects.all().order_by('-type', '-begin_time', '-track', '-begin_no')
    serializer_class = SellerInvoiceTrackNoSerializer
    filter_class = SellerInvoiceTrackNoFilter
    renderer_classes = (SellerInvoiceTrackNoHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')


    def get_queryset(self):
        request = self.request
        queryset = super(SellerInvoiceTrackNoModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanEntrySellerInvoiceTrackNo.ACTION_PERMISSION_MAPPING.get(self.action, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(turnkey_service__in=turnkey_services)


    @action(detail=True, methods=['post'], renderer_classes=[JSONRenderer, ])
    def ban_to_cancel(self, request, pk=None):
        error_result = {}
        sitn = self.get_object()
        if sitn:
            identifier = request.data.get('turnkey_service__seller__legal_entity__identifier', '')
            date_in_year_month_range = request.data.get('date_in_year_month_range', '')
            seller_invoice_track_no_ids = request.data.get('seller_invoice_track_no_ids', '')
            if "" in [identifier, date_in_year_month_range, seller_invoice_track_no_ids]:
                error_result = {"error_title": _("Ban to Cancel Error"),
                                "error_message": _("All fields are required!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            date_in_year_month_range = datetime.datetime.strptime(date_in_year_month_range, "%Y-%m-%d %H:%M:%S").astimezone(utc)
            seller_invoice_track_no_ids = seller_invoice_track_no_ids.split(',')
            seller_invoice_track_nos = SellerInvoiceTrackNo.objects.filter(turnkey_service__seller__legal_entity__identifier=identifier,
                                                                           begin_time__lte=date_in_year_month_range,
                                                                           end_time__gte=date_in_year_month_range)
            if not seller_invoice_track_nos.exists():
                error_result = {"error_title": _("Ban to Cancel Error"),
                                "error_message": _("There is no any seller-invoice-track-no records!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            elif seller_invoice_track_nos.filter(end_time__lte=now()).count() != seller_invoice_track_nos.count():
                error_result = {"error_title": _("End Time Error"),
                                "error_message": _("The end time of some seller-invoice-track-no records does not over now time!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            elif (len(seller_invoice_track_no_ids) != seller_invoice_track_nos.count()
                    or seller_invoice_track_nos.count() != seller_invoice_track_nos.filter(id__in=seller_invoice_track_no_ids).count()):
                error_result = {"error_title": _("Ban to Cancel Error"),
                                "error_message": _("Seller-invoice-track-no records do not match the records in the DB, please only set identifier and date in year-month range, and the others keep in empty!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            elif sitn not in seller_invoice_track_nos:
                error_result = {"error_title": _("Seller Invoice Track No. Error"),
                                "error_message": _("The first record does not exist!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            
            seller_invoice_track_nos.update(allow_cancel=False)
            return Response({"count": seller_invoice_track_nos.count()}, status=status.HTTP_201_CREATED)
        else:
            error_result = {"error_title": _("Seller Invoice Track No. Error"),
                            "error_message": _("{} does not exist").format(pk)}
            return Response(error_result, status=status.HTTP_403_FORBIDDEN)


    @action(detail=True, methods=['post'], renderer_classes=[JSONRenderer, ])
    def create_and_upload_blank_numbers(self, request, pk=None):
        error_result = {}
        sitn = self.get_object()
        if sitn:
            identifier = request.data.get('turnkey_service__seller__legal_entity__identifier', '')
            date_in_year_month_range = request.data.get('date_in_year_month_range', '')
            seller_invoice_track_no_ids = request.data.get('seller_invoice_track_no_ids', '')
            if "" in [identifier, date_in_year_month_range, seller_invoice_track_no_ids]:
                error_result = {"error_title": _("Blank Numbers Error"),
                                "error_message": _("All fields are required!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            date_in_year_month_range = datetime.datetime.strptime(date_in_year_month_range, "%Y-%m-%d %H:%M:%S").astimezone(utc)
            seller_invoice_track_no_ids = seller_invoice_track_no_ids.split(',')
            seller_invoice_track_nos = SellerInvoiceTrackNo.objects.filter(turnkey_service__seller__legal_entity__identifier=identifier,
                                                                           begin_time__lte=date_in_year_month_range,
                                                                           end_time__gte=date_in_year_month_range)
            if not seller_invoice_track_nos.exists():
                error_result = {"error_title": _("Blank Numbers Error"),
                                "error_message": _("There is no any seller-invoice-track-no records!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            elif seller_invoice_track_nos.filter(end_time__lte=now()).count() != seller_invoice_track_nos.count():
                error_result = {"error_title": _("End Time Error"),
                                "error_message": _("The end time of some seller-invoice-track-no records does not over now time!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            elif (len(seller_invoice_track_no_ids) != seller_invoice_track_nos.count()
                    or seller_invoice_track_nos.count() != seller_invoice_track_nos.filter(id__in=seller_invoice_track_no_ids).count()):
                error_result = {"error_title": _("Blank Numbers Error"),
                                "error_message": _("Seller-invoice-track-no records do not match the records in the DB, please only set identifier and date in year-month range, and the others keep in empty!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            elif sitn not in seller_invoice_track_nos:
                error_result = {"error_title": _("Seller Invoice Track No. Error"),
                                "error_message": _("The first record does not exist!")}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            
            try:
                upload_batchs = SellerInvoiceTrackNo.create_blank_numbers_and_upload_batchs(seller_invoice_track_nos, executor=request.user)
            except ExcutedE0402UploadBatchError as e:
                error_result = {"error_title": _("Create Upload Batch Error"),
                                "error_message": str(e)}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            except ExistedE0402UploadBatchError as e:
                error_result = {"error_title": _("Create Upload Batch Error"),
                                "error_message": str(e)}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                error_result = {"error_title": _("Create Upload Batch Error"),
                                "error_message": "{}: {}".format(type(e), str(e))}
                return Response(error_result, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"slugs": [upload_batch.slug for upload_batch in upload_batchs]}, status=status.HTTP_201_CREATED)
        else:
            error_result = {"error_title": _("Seller Invoice Track No. Error"),
                            "error_message": _("{} does not exist").format(pk)}
            return Response(error_result, status=status.HTTP_403_FORBIDDEN)


    @action(detail=False, methods=['post'], renderer_classes=[JSONRenderer, ])
    def upload_csv_to_multiple_create(self, request, *args, **kwargs):
        NOW = now()
        try:
            turnkey_service = TurnkeyService.objects.get(id=request.POST['turnkey_service'])
        except TurnkeyService.DoesNotExist:
            er = {
                "error_title": _("TurnkeyService Does Not Exist"),
                "error_message": _("TurnkeyService(id: {}) does not exist").format(turnkey_service),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
    
        raw_datas = []
        datas = []
        if request.POST.get("e0501invoiceassignno_ids", ""):
            for id in request.POST['e0501invoiceassignno_ids'].split(','):
                try:
                    eian = E0501InvoiceAssignNo.objects.get(id=id)
                except E0501InvoiceAssignNo.DoesNotExist:
                    er = {
                        "error_title": _("E0501InvoiceAssignNo Does Not Exist"),
                        "error_message": _("E0501InvoiceAssignNo(id: {}) does not exist").format(id),
                    }
                    return Response(er, status=status.HTTP_403_FORBIDDEN)
                else:
                    type = '{:02d}'.format(int(eian.type))
                    if '07' != type:
                        er = {
                            "error_title": _("Track No. Type Error"),
                            "error_message": _("It only support '07' type now.")
                        }
                        return Response(er, status=status.HTTP_403_FORBIDDEN)
                    elif eian.identifier != turnkey_service.seller.legal_entity.identifier:
                        continue

                    end_chmk_year, end_month = eian.year_month[:3], eian.year_month[3:]
                    end_year = int(end_chmk_year) + 1911
                    end_month = int(end_month)
                    end_time_0 = TAIPEI_TIMEZONE.localize(datetime.datetime(end_year, end_month, 1, 0, 0, 0)) + datetime.timedelta(days=40)
                    end_time = TAIPEI_TIMEZONE.localize(datetime.datetime(end_time_0.year, end_time_0.month, 1, 0, 0, 0))
                    begin_time_0 = end_time - datetime.timedelta(days=45)
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(begin_time_0.year, begin_time_0.month, 1, 0, 0, 0))
                    raw_data = {
                        "turnkey_service": turnkey_service.id,
                        "type": type,
                        "begin_time": begin_time,
                        "end_time": end_time,
                        "track": eian.track,
                        "begin_no": eian.begin_no,
                        "end_no": eian.end_no,
                    }
                raw_datas.append(raw_data)
        else:
            csv_file = request.FILES['file']
            while True:
                line = csv_file.readline().decode('cp950').rstrip("\r\n")
                if not line:
                    break
                elif turnkey_service.seller.legal_entity.identifier in line:
                    cols = line.split(',')

                    if '07' != '{:02d}'.format(int(cols[1])):
                        er = {
                            "error_title": _("Track No. Type Error"),
                            "error_message": _("It only support '07' type now.")
                        }
                        return Response(er, status=status.HTTP_403_FORBIDDEN)

                    try:
                        begin_month_str, end_month_str = cols[3].split(' ~ ')
                        begin_chmk_year, begin_month = begin_month_str.split('/')
                        begin_year = int(begin_chmk_year) + 1911
                        begin_month = int(begin_month)
                        end_chmk_year, end_month = end_month_str.split('/')
                        end_year = int(end_chmk_year) + 1911
                        end_month = int(end_month)
                        begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(begin_year, begin_month, 1, 0, 0, 0))
                        end_time_0 = TAIPEI_TIMEZONE.localize(datetime.datetime(end_year, end_month, 1, 0, 0, 0)) + datetime.timedelta(days=40)
                        end_time = TAIPEI_TIMEZONE.localize(datetime.datetime(end_time_0.year, end_time_0.month, 1, 0, 0, 0))
                    except Exception as e:
                        er = {
                            "error_title": _("Year Month Range Error"),
                            "error_message": _("{} has error: \n\n\n{}").format(line, e)
                        }
                        return Response(er, status=status.HTTP_403_FORBIDDEN)
                    else:
                        if NOW < begin_time - datetime.timedelta(days=15):
                            er = {
                                "error_title": _("Begin Time Error"),
                                "error_message": _("{} has error: \nToo early to import.").format(line)
                            }
                            return Response(er, status=status.HTTP_403_FORBIDDEN)
                        elif NOW > end_time:
                            er = {
                                "error_title": _("End Time Error"),
                                "error_message": _("{} has error: \nToo late to import.").format(line)
                            }
                            return Response(er, status=status.HTTP_403_FORBIDDEN)
                    
                    begin_no = cols[5]
                    end_no = cols[6]
                    if begin_no[-2:] not in ('00', '50'):
                        er = {
                            "error_title": _("Begin No. Error"),
                            "error_message": _("{} has error: \n\n\nThe suffix of begin_no should be 00 or 50.").format(line)
                        }
                        return Response(er, status=status.HTTP_403_FORBIDDEN)
                    if end_no[-2:] not in ('49', '99'):
                        er = {
                            "error_title": _("End No. Error"),
                            "error_message": _("{} has error: \n\n\nThe suffix of end_no should be 49 or 99.").format(line)
                        }
                        return Response(er, status=status.HTTP_403_FORBIDDEN)

                    raw_data = {
                        "turnkey_service": turnkey_service.id,
                        "type": '{:02d}'.format(int(cols[1])),
                        "begin_time": begin_time,
                        "end_time": end_time,
                        "track": cols[4],
                        "begin_no": begin_no,
                        "end_no": end_no,
                    }
                    raw_datas.append(raw_data)

        split_by_numbers = int(request.POST.get('split_by_numbers', '100'))
        for rd in raw_datas:
            begin_no = int(rd['begin_no'])
            end_no = int(rd['end_no'])
            _begin_no_in_split = begin_no
            _end_no_in_split = _begin_no_in_split + split_by_numbers - 1
            if _end_no_in_split > end_no:
                _end_no_in_split = end_no
            while _begin_no_in_split < _end_no_in_split:
                data = {
                    "turnkey_service": rd['turnkey_service'],
                    "type": rd['type'],
                    "begin_time": rd['begin_time'],
                    "end_time": rd['end_time'],
                    "track": rd['track'],
                    "begin_no": _begin_no_in_split,
                    "end_no": _end_no_in_split,
                }
                sitns = SellerInvoiceTrackNoSerializer(data=data, context={'request': request})
                if sitns.is_valid():
                    datas.append(data)
                elif 'unique' in str(sitns.errors) and (_begin_no_in_split != begin_no or _end_no_in_split != end_no):
                    pass
                else:
                    if 'unique' in str(sitns.errors):
                        error_message = _("{} exists").format(line)
                    else:
                        error_message = _("{} has error: \n\n\n{}").format(line, sitns.errors)
                    er = {
                        "error_title": _("Data Error"),
                        "error_message": error_message,
                    }
                    return Response(er, status=status.HTTP_403_FORBIDDEN)

                _begin_no_in_split = _end_no_in_split + 1
                if _begin_no_in_split > end_no:
                    break
                _end_no_in_split = _begin_no_in_split + split_by_numbers - 1
                if _end_no_in_split > end_no:
                    _end_no_in_split = end_no
        output_datas = []
        if not datas:
            er = {
                "error_title": _("Identifier Error"),
                "error_message": _("Identifier does not match the seller identifier of the TurnkeyService."),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        for data in datas:
            if SellerInvoiceTrackNo.objects.filter(type=data['type'],
                                                   begin_time=data['begin_time'],
                                                   end_time=data['end_time'],
                                                   track=data['track']
                                                  ).filter(Q(begin_no__lte=data['begin_no'], end_no__gte=data['begin_no'])
                                                            |Q(begin_no__lte=data['end_no'], end_no__gte=data['end_no'])
                                                            |Q(begin_no__gte=data['begin_no'], end_no__lte=data['end_no'])).exists():
                
                error_message = _("{} ~ {} has error: \n\n\nnumber overlapping").format(data['begin_no'], data['end_no'])
                er = {
                    "error_title": _("Data Error"),
                    "error_message": error_message,
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(data=data, many=False)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            output_datas.append(serializer.data)
        return Response(output_datas, status=status.HTTP_201_CREATED)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except UsedSellerInvoiceTrackNoError as e:
            message, track_no_ = e.args
            return Response({"error_title": _("Delete Error"),
                             "error_message": message.format(track_no_),
                            }, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)



class E0501InvoiceAssignNoModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewE0501InvoiceAssignNo, ), )
    pagination_class = OneHundredPerPagePagination
    queryset = E0501InvoiceAssignNo.objects.all().order_by('-year_month', )
    serializer_class = E0501InvoiceAssignNoSerializer
    filter_class = E0501InvoiceAssignNoFilter
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )


    def get_queryset(self):
        request = self.request
        queryset = super(E0501InvoiceAssignNoModelViewSet, self).get_queryset()
        NOW = now().astimezone(TAIPEI_TIMEZONE)
        year_month = '{:03d}{:02d}'.format(_year_to_chmk_year(NOW.year), NOW.month)
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset.filter(year_month__gte=year_month)
        else:
            permissions = CanEntrySellerInvoiceTrackNo.ACTION_PERMISSION_MAPPING.get(self.action, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(identifier__in=[ts.party_id for ts in turnkey_services], year_month__gte=year_month)



class EInvoiceModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEntryEInvoice), )
    pagination_class = TenTo100PerPagePagination
    queryset = EInvoice.objects.all().order_by('-id')
    serializer_class = EInvoiceSerializer
    filter_class = EInvoiceFilter
    renderer_classes = (EInvoiceHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )


    def get_queryset(self):
        request = self.request
        queryset = super(EInvoiceModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanEntryEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(seller_invoice_track_no__turnkey_service__in=turnkey_services)


    @action(detail=True, methods=['get'], renderer_classes=[JSONRenderer, ])
    def get_escpos_print_scripts(self, request, pk=None):
        ei = self.get_object()
        if ei:
            escpos_print_scripts = ei.escpos_print_scripts
            if request.GET.get('with_details_content', False) not in ['true', '1']:
                del escpos_print_scripts['details_content']
            if request.GET.get('re_print_original_copy', False) in ['true', '1']:
                escpos_print_scripts['re_print_original_copy'] = True
                NOW = now()
                if (ei.generate_time.astimezone(TAIPEI_TIMEZONE).day != NOW.astimezone(TAIPEI_TIMEZONE).day
                    and NOW - ei.generate_time >= datetime.timedelta(hours=6)):
                    return Response({"error_title": _("Re-print E-Invoice Error"),
                                     "error_message": _("Expired time: over next day AM00:00 and 6 hours past the generate time."),
                                    }, status=status.HTTP_403_FORBIDDEN)
            if escpos_print_scripts.get('is_canceled', False):
                escpos_print_scripts['re_print_original_copy'] = True
            if escpos_print_scripts.get('buyer_is_business_entity', False):
                escpos_print_scripts['re_print_original_copy'] = True
            return Response(escpos_print_scripts)
        else:
            return Response({"error_title": _("E-Invoice Error"),
                             "error_message": _("{} does not exist").format(pk),
                            }, status=status.HTTP_403_FORBIDDEN)


    @action(detail=True, methods=['get'], renderer_classes=[JSONRenderer, ])
    def get_escpos_print_scripts_for_sales_return_receipt(self, request, pk=None):
        ei = self.get_object()
        if ei:
            escpos_print_scripts_for_sales_return_receipt = ei.escpos_print_scripts_for_sales_return_receipt
            return Response(escpos_print_scripts_for_sales_return_receipt)
        else:
            return Response({"error_title": _("E-Invoice Error"),
                             "error_message": _("E-Invoice(id:{}) does not exist").format(pk),
                            }, status=status.HTTP_403_FORBIDDEN)



class EInvoicePrintLogModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEntryEInvoicePrintLog), )
    pagination_class = TenTo100PerPagePagination
    queryset = EInvoicePrintLog.objects.all().order_by('-id')
    serializer_class = EInvoicePrintLogSerializer
    filter_class = EInvoicePrintLogFilter
    renderer_classes = (EInvoicePrintLogHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )


    def get_queryset(self):
        request = self.request
        queryset = super(EInvoicePrintLogModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanEntryEInvoicePrintLog.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services)



class CancelEInvoiceModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEntryCancelEInvoice), )
    pagination_class = TenTo100PerPagePagination
    queryset = CancelEInvoice.objects.all().order_by('-id')
    serializer_class = CancelEInvoiceSerializer
    filter_class = CancelEInvoiceFilter
    renderer_classes = (CancelEInvoiceHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', )


    def get_queryset(self):
        request = self.request
        queryset = super(CancelEInvoiceModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanEntryCancelEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services)
    

    def create(self, request, *args, **kwargs):
        data = request.data
        einvoice_id = data['einvoice_id']
        re_create_einvoice = data['re_create_einvoice']
        force_to_cancel_the_einvoice = False
        del data['re_create_einvoice']
        try:
            einvoice = EInvoice.objects.get(id=einvoice_id)
        except EInvoice.DoesNotExist:
            er = {
                "error_title": _("E-Invoice Error"),
                "error_message": _("E-Invoice(id: {}) does not exist!").format(einvoice_id),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        else:
            if not einvoice.can_cancel:
                er = {
                    "error_title": _("Cancel Error"),
                    "error_message": einvoice.cancel_fail_reason,
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
            elif not re_create_einvoice:
                if (("#NO-RETURN" in data['remark'] or "#無退貨" in data['remark'])
                    and re.search('[a-zA-Z]{2}-?[0-9]{8}', data['remark'])):
                    force_to_cancel_the_einvoice = True
                else:
                    message = einvoice.check_before_cancel_einvoice()
                    if message:
                        er = {
                            "error_title": _("Cancel Error"),
                            "error_message": message,
                        }
                        return Response(er, status=status.HTTP_403_FORBIDDEN)

        if "wp" == einvoice.in_cp_np_or_wp() and not einvoice.print_mark:
            einvoice.set_print_mark_true()
        dev_null = UploadBatch.append_to_the_upload_batch(einvoice, executor=request.user)

        data['creator'] = request.user.id
        data['einvoice'] = einvoice.id
        data['mig_type'] = EInvoiceMIG.objects.get(no=CancelEInvoice.MIG_NO_SET[einvoice.get_mig_no()]).id
        data['seller_identifier'] = einvoice.seller_identifier
        data['buyer_identifier'] = einvoice.buyer_identifier
        data['generate_time'] = now()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if force_to_cancel_the_einvoice:
            serializer.instance.post_cancel_einvoice()
        elif re_create_einvoice:
            _d = {f.name: getattr(einvoice, f.name)
                for f in EInvoice._meta.fields
            }
            seller_invoice_track_no = None
            for seller_invoice_track_no in SellerInvoiceTrackNo.filter_now_use_sitns(
                                                    turnkey_service=einvoice.seller_invoice_track_no.turnkey_service,
                                                    type=einvoice.seller_invoice_track_no.type
                                           ).order_by('-begin_no'):
                try:
                    _d['no'] = seller_invoice_track_no.get_new_no()
                except NotEnoughNumberError:
                    continue
                else:
                    _d['track'] = seller_invoice_track_no.track
                    _d['seller_invoice_track_no'] = seller_invoice_track_no
                    break
                return cei
            if not seller_invoice_track_no:
                er = {
                    "error_title": _("No Seller Invoice Track No. Error"),
                    "error_message": _("Canceled E-Invoice, but it could not create the new E-Invoice"),
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
            del _d['id']
            del _d['random_number']
            del _d['generate_time']
            _d['creator'] = request.user
            _d['ei_synced'] = False
            _d['print_mark'] = False
            new_einvoice = EInvoice(**_d)
            new_einvoice.save()
            serializer.instance.set_new_einvoice(new_einvoice)
            serializer.instance.post_cancel_einvoice()
        serializer = CancelEInvoiceSerializer(serializer.instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class VoidEInvoiceModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEntryVoidEInvoice), )
    pagination_class = TenTo100PerPagePagination
    queryset = VoidEInvoice.objects.all().order_by('-id')
    serializer_class = VoidEInvoiceSerializer
    filter_class = VoidEInvoiceFilter
    renderer_classes = (VoidEInvoiceHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', )


    def get_queryset(self):
        request = self.request
        queryset = super(VoidEInvoiceModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanEntryVoidEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services)
    

    def create(self, request, *args, **kwargs):
        data = request.data
        cancel_before_void = data['cancel_before_void']
        del data['cancel_before_void']
        if data['npoban'] and data['buyer_identifier']:
            er = {
                "error_title": _("Void Error"),
                "error_message": _("NPOBAN can not be set with Buyer Identifier at the same time")
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        elif data['mobile_barcode'] and data['natural_person_barcode']:
            er = {
                "error_title": _("Void Error"),
                "error_message": _("Mobile barcode can not be set with Natural Person barcode at the same time")
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        elif data['natural_person_barcode'] and not re.search('[a-zA-Z]{2}[0-9]{14}', data['natural_person_barcode']):
            er = {
                "error_title": _("Natural Person barcode Error"),
                "error_message": _("Natural Person barcode should be prefixed two digits alphabets and follow 14 digits number.")
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)

        NOW = now()
        einvoice_id = data['einvoice_id']
        try:
            einvoice = EInvoice.objects.get(id=einvoice_id)
        except EInvoice.DoesNotExist:
            er = {
                "error_title": _("E-Invoice Error"),
                "error_message": _("E-Invoice(id: {}) does not exist!").format(einvoice_id),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        else:
            if (einvoice.generate_time.astimezone(TAIPEI_TIMEZONE).day != NOW.astimezone(TAIPEI_TIMEZONE).day
                and NOW - einvoice.generate_time >= datetime.timedelta(hours=6)):
                return Response({"error_title": _("Void Error"),
                                 "error_message": _("Expired time: over next day AM00:00 and 6 hours past the generate time."),
                                }, status=status.HTTP_403_FORBIDDEN)
            if einvoice.is_voided:
                er = {
                    "error_title": _("Void Error"),
                    "error_message": _("E-Invoice({}) was already voided!").format(einvoice.track_no_)
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
            elif not einvoice.can_void:
                er = {
                    "error_title": _("Void Error"),
                    "error_message": _("E-Invoice({}) was already canceled!").format(einvoice.track_no_)
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)

        eisa = EInvoiceSellerAPI.objects.get(AppId=settings.TAIWAN_EINVOICE_APP_ID)
        ir = IdentifierRule()
        if data['buyer_identifier'] and False == ir.verify_identifier(data['buyer_identifier']):
            er = {
                "error_title": _("Buyer Identifier Error"),
                "error_message": _('Buyer identifier is not valid.')
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        elif data['npoban'] and False == eisa.inquery('donate-mark', data['npoban']):
            er = {
                "error_title": _("NPOBan Error"),
                "error_message": _('NPO bn does not exist.')
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        elif data['mobile_barcode'] and False == eisa.inquery('mobile-barcode', data['mobile_barcode']):
            er = {
                "error_title": _("Mobile barcode Error"),
                "error_message": _('Mobile barcode does not exist.')
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)

        if "wp" == einvoice.in_cp_np_or_wp() and not einvoice.print_mark:
            einvoice.set_print_mark_true()
        dev_null = UploadBatch.append_to_the_upload_batch(einvoice, executor=request.user)

        if cancel_before_void:
            cei = CancelEInvoice(creator=request.user,
                                 einvoice=einvoice,
                                 seller_identifier=einvoice.seller_identifier,
                                 buyer_identifier=einvoice.buyer_identifier,
                                 generate_time=now(),
                                 mig_type=EInvoiceMIG.objects.get(no=CancelEInvoice.MIG_NO_SET[einvoice.get_mig_no()]),
                                 reason=data['reason'],
                                 remark=data['remark']
                                )
            cei.save()

        data['creator'] = request.user.id
        data['einvoice'] = einvoice.id
        data['mig_type'] = EInvoiceMIG.objects.get(no=VoidEInvoice.MIG_NO_SET[einvoice.get_mig_no()]).id
        data['seller_identifier'] = einvoice.seller_identifier
        _post_buyer_identifier = data['buyer_identifier']
        data['buyer_identifier'] = einvoice.buyer_identifier
        data['generate_time'] = NOW
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        for _ei in EInvoice.objects.filter(seller_invoice_track_no__turnkey_service=einvoice.seller_invoice_track_no.turnkey_service,
                                           track=einvoice.track,
                                           no=einvoice.no).order_by('-reverse_void_order'):
            _ei.increase_reverse_void_order()


        _d = {f.name: getattr(einvoice, f.name) for f in EInvoice._meta.fields }
        del _d['id']
        del _d['random_number']
        _d['creator'] = request.user
        _d['ei_synced'] = False
        _d['print_mark'] = False
        gci = LegalEntity.objects.get(identifier=LegalEntity.GENERAL_CONSUMER_IDENTIFIER)
        _d['buyer'] = gci
        _d['buyer_identifier'] = gci.identifier
        _d['buyer_name'] = gci.name
        _d['buyer_customer_number'] = gci.customer_number
        for clear_value in [
            'carrier_type',
            'carrier_id1',
            'carrier_id2',
            'npoban',
            "buyer_address",
            "buyer_person_in_charge",
            "buyer_telephone_number",
            "buyer_facsimile_number",
            "buyer_email_address",
            "buyer_role_remark",
        ]:
            _d[clear_value] = ''
        data['buyer_identifier'] = _post_buyer_identifier

        if data['mobile_barcode']:
            _d['carrier_type'] = '3J0002'
            _d['carrier_id1'] = _d['carrier_id2'] = data['mobile_barcode']
        elif data['natural_person_barcode']:
            _d['carrier_type'] = 'CQ0001'
            _d['carrier_id1'] = _d['carrier_id2'] = data['natural_person_barcode']

        lg = logging.getLogger('taiwan_einvoice')
        if data['npoban']:
            _d['npoban'] = data['npoban']
        elif data['buyer_identifier']:
            _d['buyer_identifier'] = data['buyer_identifier']
            try:
                buyer_legal_entity = LegalEntity.objects.get(identifier=_d['buyer_identifier'])
            except LegalEntity.DoesNotExist:
                buyer_legal_entity = LegalEntity(identifier=_d['buyer_identifier'], name=_d['buyer_identifier'])
                buyer_legal_entity.save()
            _d["buyer"] = buyer_legal_entity
            _d["buyer_name"] = buyer_legal_entity.name
            _d["buyer_address"] = buyer_legal_entity.address
            _d["buyer_person_in_charge"] = buyer_legal_entity.person_in_charge
            _d["buyer_telephone_number"] = buyer_legal_entity.telephone_number
            _d["buyer_facsimile_number"] = buyer_legal_entity.facsimile_number
            _d["buyer_email_address"] = buyer_legal_entity.email_address
            _d["buyer_customer_number"] = buyer_legal_entity.customer_number
            _d["buyer_role_remark"] = buyer_legal_entity.role_remark

        new_einvoice = EInvoice(**_d)
        new_einvoice.save(upload_batch_kind='57')
        new_einvoice.set_generate_time(einvoice.generate_time)
        serializer.instance.set_new_einvoice(new_einvoice)
        serializer.instance.save()
        serializer.instance.post_void_einvoice()
        serializer = VoidEInvoiceSerializer(serializer.instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class UploadBatchModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewTEAlarmForProgrammer), )
    pagination_class = TenTo100PerPagePagination
    queryset = UploadBatch.objects.all().order_by('-id')
    serializer_class = UploadBatchSerializer
    filter_class = UploadBatchFilter
    renderer_classes = (UploadBatchHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )


    def get_queryset(self):
        request = self.request
        queryset = super(UploadBatchModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanViewTEAlarmForProgrammer.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(turnkey_service__in=turnkey_services)



class BatchEInvoiceModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewBatchEInvoice), )
    pagination_class = TenTo100PerPagePagination
    queryset = BatchEInvoice.objects.all().order_by('-id')
    serializer_class = BatchEInvoiceSerializer
    filter_class = BatchEInvoiceFilter
    renderer_classes = (BatchEInvoiceHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', 'post')


    def get_queryset(self):
        request = self.request
        queryset = super(BatchEInvoiceModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanViewBatchEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(batch__turnkey_service__in=turnkey_services)


    @action(detail=True, methods=['post'], renderer_classes=[JSONRenderer, ])
    def re_create_another_upload_batch(self, request, pk=None):
        batch_einvoice = self.get_object()
        handling_type = request.data.get("handling_type", "")
        handling_note = request.data.get("handling_note", "")
        if batch_einvoice.pass_if_error:
            er = {
                "error_title": _("Batch E-Invoice Error"),
                "error_message": _('Already handled!')
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        elif not handling_note:
            er = {
                "error_title": _("Data Error"),
                "error_message": _('Empty Hanling Note!')
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        elif handling_type not in ["the_same_track_no", "with_new_track_no", "no_new_upload_batch"]:
            er = {
                "error_title": _("Data Error"),
                "error_message": _('Wrong Hanling Type!')
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)

        content_object = batch_einvoice.content_object
        if "no_new_upload_batch" == handling_type:
            kind = ''
        elif "the_same_track_no" == handling_type:
            kind = 'R'
        elif "with_new_track_no" == handling_type:
            kind = 'RN'
            content_object = content_object.renew_track_no_and_sitn_obj()

        if '' == kind:
            new_ub = False
            batch_einvoice.batch.status = '4'
            batch_einvoice.batch.save()
            batch_einvoice.batch.check_in_4_status_then_update_to_the_next()
            if 'f' != batch_einvoice.batch.status:
                er = {
                    "error_title": _("UploadBatch Status Error"),
                    "error_message": _('Upload Batch Status != "f"'),
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
        else:
            i = 0 
            while i < 10000:
                slug = "{}{:04d}".format(content_object.track_no, i)
                if not UploadBatch.objects.filter(slug=slug).exists():
                    break
                i += 1
            new_ub = UploadBatch(turnkey_service=batch_einvoice.batch.turnkey_service,
                                slug=slug,
                                mig_type=batch_einvoice.batch.mig_type,
                                kind=kind,
                                status='0')
            new_ub.save()
            new_be = BatchEInvoice(batch=new_ub,
                                content_object=content_object,
                                begin_time=content_object.seller_invoice_track_no.begin_time,
                                end_time=content_object.seller_invoice_track_no.end_time,
                                track_no=content_object.track_no,
                                body="",
                                )
            new_be.save()
        batch_einvoice.handling_note = handling_note
        batch_einvoice.pass_if_error = True
        batch_einvoice.save()
        return Response({"slug": new_ub.slug if new_ub else _("None")}, status=status.HTTP_201_CREATED)


class AuditLogModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewTEAlarmForProgrammer), )
    pagination_class = TenTo100PerPagePagination
    queryset = AuditLog.objects.all().order_by('-id')
    serializer_class = AuditLogSerializer
    filter_class = AuditLogFilter
    renderer_classes = (AuditLogHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )
    

    def get_queryset(self):
        request = self.request
        queryset = super(AuditLogModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanViewTEAlarmForProgrammer.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(turnkey_service__in=turnkey_services)



class SummaryReportModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewSummaryReport), )
    pagination_class = TenTo100PerPagePagination
    queryset = SummaryReport.objects.all().order_by('-id')
    serializer_class = SummaryReportSerializer
    filter_class = SummaryReportFilter
    renderer_classes = (SummaryReportHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )
    

    def get_queryset(self):
        request = self.request
        queryset = super(SummaryReportModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            permissions = CanViewSummaryReport.METHOD_PERMISSION_MAPPING.get(request.method, [])
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(turnkey_service__in=turnkey_services)



class TEAlarmModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanViewTEAlarmForProgrammer, CanViewTEAlarmForGeneralUser), )
    pagination_class = TenTo100PerPagePagination
    queryset = TEAlarm.objects.all().order_by('-id')
    serializer_class = TEAlarmSerializer
    filter_class = TEAlarmFilter
    renderer_classes = (TEAlarmHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )
    

    def get_queryset(self):
        request = self.request
        queryset = super(TEAlarmModelViewSet, self).get_queryset()
        if not request.user.teastaffprofile or not request.user.teastaffprofile.is_active:
            return queryset.none()
        elif request.user.is_superuser:
            return queryset
        else:
            programmer_permissions = CanViewTEAlarmForGeneralUser.METHOD_PERMISSION_MAPPING.get(request.method, [])
            general_user_permissions = CanViewTEAlarmForProgrammer.METHOD_PERMISSION_MAPPING.get(request.method, [])
            permissions = list(programmer_permissions) + list(general_user_permissions)
            turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
            return queryset.filter(turnkey_service__in=turnkey_services)


