import json, datetime, logging
from django.http import Http404
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.models import Permission, User, Group
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from guardian.shortcuts import get_objects_for_user, get_perms, get_users_with_perms, remove_perm, assign_perm

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ho600_lib.permissions import Or

from taiwan_einvoice.permissions import (
    IsSuperUser,
    CanEditStaffProfile,
    CanViewSelfStaffProfile,
    CanEditESCPOSWebOperator,
    CanEditTurnkeyWebGroup,
)
from taiwan_einvoice.renderers import (
    TEBrowsableAPIRenderer,
    StaffProfileHtmlRenderer,
    ESCPOSWebHtmlRenderer,
    ESCPOSWebOperatorHtmlRenderer,
    TurnkeyWebHtmlRenderer,
    TurnkeyWebGroupHtmlRenderer,
    LegalEntityHtmlRenderer,
    SellerInvoiceTrackNoHtmlRenderer,
    EInvoiceHtmlRenderer,
    EInvoicePrintLogHtmlRenderer,
    CancelEInvoiceHtmlRenderer,
)
from taiwan_einvoice.models import (
    TAIPEI_TIMEZONE,
    StaffProfile,
    ESCPOSWeb,
    LegalEntity,
    Seller,
    TurnkeyWeb,
    SellerInvoiceTrackNo,
    EInvoice,
    EInvoicePrintLog,
    CancelEInvoice,
)
from taiwan_einvoice.serializers import (
    StaffProfileSerializer,
    StaffGroupSerializer,
    ESCPOSWebSerializer,
    ESCPOSWebOperatorSerializer,
    LegalEntitySerializerForUser,
    LegalEntitySerializerForSuperUser,
    SellerSerializer,
    TurnkeyWebSerializer,
    TurnkeyWebGroupSerializer,
    SellerInvoiceTrackNoSerializer,
    EInvoiceSerializer,
    EInvoicePrintLogSerializer,
    CancelEInvoiceSerializer,
)
from taiwan_einvoice.filters import (
    StaffProfileFilter,
    ESCPOSWebFilter,
    LegalEntityFilter,
    TurnkeyWebFilter,
    TurnkeyWebGroupFilter,
    SellerInvoiceTrackNoFilter,
    EInvoiceFilter,
    EInvoicePrintLogFilter,
)


class Default30PerPagePagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 30
    max_page_size = 30


class TenTo1000PerPagePagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 10
    max_page_size = 1000


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



class StaffProfileModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditStaffProfile, CanViewSelfStaffProfile), )
    pagination_class = TenTo1000PerPagePagination
    queryset = StaffProfile.objects.all().order_by('-id')
    serializer_class = StaffProfileSerializer
    filter_class = StaffProfileFilter
    renderer_classes = (StaffProfileHtmlRenderer, TEBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('post', 'get', 'patch')


    def create(self, request, *args, **kwargs):
        data = request.data
        if StaffProfile.objects.filter(user__username=data['user.username']).exists():
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
        serializer = StaffProfileSerializer(serializer.instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class ESCPOSWebModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditESCPOSWebOperator), )
    queryset = ESCPOSWeb.objects.all().order_by('-id')
    serializer_class = ESCPOSWebSerializer
    filter_class = ESCPOSWebFilter
    renderer_classes = (ESCPOSWebHtmlRenderer, TEBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('post', 'get', )


    def get_queryset(self):
        request = self.request
        queryset = super().get_queryset()
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



class ESCPOSWebOperatorModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditESCPOSWebOperator), )
    queryset = ESCPOSWeb.objects.all().order_by('-id')
    serializer_class = ESCPOSWebOperatorSerializer
    filter_class = ESCPOSWebFilter
    renderer_classes = (ESCPOSWebOperatorHtmlRenderer, TEBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', 'patch', )


    def get_queryset(self):
        request = self.request
        queryset = super().get_queryset()
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
                sp = StaffProfile.objects.get(id=data['staffprofile_id'])
            except StaffProfile.DoesNotExist:
                pass
            else:
                ct = ContentType.objects.get(app_label='taiwan_einvoice', model='escposweb')
                p = Permission.objects.get(content_type=ct, codename='operate_te_escposweb')
                remove_perm(p, sp.user, escposweb)
        elif 'add' == data['type']:
            ct = ContentType.objects.get(app_label='taiwan_einvoice', model='escposweb')
            p = Permission.objects.get(content_type=ct, codename='operate_te_escposweb')
            for staffprofile_id in data['staffprofile_ids']:
                try:
                    sp = StaffProfile.objects.get(id=staffprofile_id)
                except StaffProfile.DoesNotExist:
                    continue
                else:
                    assign_perm(p, sp.user, escposweb)
        serializer = ESCPOSWebOperatorSerializer(self.get_object(), context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)



class LegalEntityModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
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
    queryset = Seller.objects.all().order_by('-id')
    serializer_class = SellerSerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'patch')



class TurnkeyWebModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = TurnkeyWeb.objects.all().order_by('-id')
    serializer_class = TurnkeyWebSerializer
    filter_class = TurnkeyWebFilter
    renderer_classes = (TurnkeyWebHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'patch')



class TurnkeyWebGroupModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUser, CanEditTurnkeyWebGroup), )
    pagination_class = Default30PerPagePagination
    queryset = TurnkeyWeb.objects.all().order_by('-id')
    serializer_class = TurnkeyWebGroupSerializer
    filter_class = TurnkeyWebGroupFilter
    renderer_classes = (TurnkeyWebGroupHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', 'patch')


    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        turnkeyweb = self.get_object()
        if 'delete_group' == data['type']:
            try:
                g = Group.objects.get(id=data['group_id'])
            except Group.DoesNotExist:
                pass
            else:
                g.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        elif 'add_group' == data['type']:
            if len(turnkeyweb.groups) >= self.pagination_class.page_size:
                er = {
                    "error_title": _("The count of Existed Groups exceeds the limit"),
                    "error_message": _("The count of Existed Groups exceeds the limit({})").format(self.pagination_class.page_size),
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
            ct_id = ContentType.objects.get_for_model(turnkeyweb).id
            group_name = "ct{ct_id}:{id}:{name}".format(ct_id=ct_id, id=turnkeyweb.id, name=data['display_name'])
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
                ct = ContentType.objects.get_for_model(turnkeyweb)
                group_name = "ct{ct_id}:{id}:{name}".format(ct_id=ct.id, id=turnkeyweb.id, name=data['display_name'])
                g.name = group_name
                g.save()
                for k, v in data['permissions'].items():
                    try:
                        p = Permission.objects.get(content_type=ct, codename=k)
                    except Permission.DoesNotExist:
                        p = Permission.objects.get(codename=k)
                        target_obj = None
                    else:
                        target_obj = turnkeyweb
                    if v:
                        assign_perm(p, g, obj=target_obj)
                    else:
                        remove_perm(p, g, obj=target_obj)
                return Response({}, status=status.HTTP_200_OK)



class SellerInvoiceTrackNoModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = SellerInvoiceTrackNo.objects.all().order_by('-id')
    serializer_class = SellerInvoiceTrackNoSerializer
    filter_class = SellerInvoiceTrackNoFilter
    renderer_classes = (SellerInvoiceTrackNoHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', )


    @action(detail=False, methods=['post'], renderer_classes=[JSONRenderer, ])
    def upload_csv_to_multiple_create(self, request, *args, **kwargs):
        try:
            turnkey_web = TurnkeyWeb.objects.get(id=request.POST['turnkey_web'])
        except TurnkeyWeb.DoesNotExist:
            er = {
                "error_title": "TurnkeyWeb Does Not Exist",
                "error_message": _("TurnkeyWeb(id: {}) does not exist").format(turnkey_web),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        csv_file = request.FILES['file']
        datas = []
        while True:
            line = csv_file.readline().decode('cp950').rstrip("\r\n")
            if not line:
                break
            elif turnkey_web.seller.legal_entity.identifier in line:
                cols = line.split(',')

                try:
                    begin_month_str, end_month_str = cols[3].split(' ~ ')
                    begin_chmk_year, begin_month = begin_month_str.split('/')
                    begin_year = int(begin_chmk_year) + 1911
                    begin_month = int(begin_month)
                    end_chmk_year, end_month = begin_month_str.split('/')
                    end_year = int(end_chmk_year) + 1911
                    end_month = int(end_month)
                    begin_time = TAIPEI_TIMEZONE.localize(datetime.datetime(begin_year, begin_month, 1, 0, 0, 0))
                    end_time_0 = TAIPEI_TIMEZONE.localize(datetime.datetime(end_year, end_month, 1, 0, 0, 0)) + datetime.timedelta(days=70)
                    end_time = TAIPEI_TIMEZONE.localize(datetime.datetime(end_time_0.year, end_time_0.month, 1, 0, 0, 0))
                except Exception as e:
                    er = {
                        "error_title": "Year Month Range Error",
                        "error_message": _("{} has error: \n\n\n{}").format(line, e)
                    }
                    return Response(er, status=status.HTTP_403_FORBIDDEN)
                
                begin_no = cols[5]
                end_no = cols[6]
                if begin_no[-2:] not in ('00', '50'):
                    er = {
                        "error_title": "Begin No. Error",
                        "error_message": _("{} has error: \n\n\nThe suffix of begin_no should be 00 or 50.").format(line)
                    }
                    return Response(er, status=status.HTTP_403_FORBIDDEN)
                if end_no[-2:] not in ('49', '99'):
                    er = {
                        "error_title": "End No. Error",
                        "error_message": _("{} has error: \n\n\nThe suffix of end_no should be 49 or 99.").format(line)
                    }
                    return Response(er, status=status.HTTP_403_FORBIDDEN)


                data = {
                    "turnkey_web": turnkey_web.id,
                    "type": '{:02d}'.format(int(cols[1])),
                    "begin_time": begin_time,
                    "end_time": end_time,
                    "track": cols[4],
                    "begin_no": begin_no,
                    "end_no": end_no,
                }
                sitns = SellerInvoiceTrackNoSerializer(data=data, context={'request': request})
                if sitns.is_valid():
                    datas.append(data)
                else:
                    if 'unique' in str(sitns.errors):
                        error_message = _("{} exists").format(line)
                    else:
                        error_message = _("{} has error: \n\n\n{}").format(line, sitns.errors)
                    er = {
                        "error_title": "Data Error",
                        "error_message": error_message,
                    }
                    return Response(er, status=status.HTTP_403_FORBIDDEN)
        output_datas = []
        for data in datas:
            if SellerInvoiceTrackNo.objects.filter(type=data['type'],
                                                   begin_time=data['begin_time'],
                                                   end_time=data['end_time'],
                                                   track=data['track']
                                                  ).filter(Q(begin_no__lte=data['begin_no'], end_no__gte=data['begin_no'])
                                                            |Q(begin_no__lte=data['end_no'], end_no__gte=data['end_no'])).exists():
                
                error_message = _("{} ~ {} has error: \n\n\nnumber overlapping").format(data['begin_no'], data['end_no'])
                er = {
                    "error_title": "Data Error",
                    "error_message": error_message,
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(data=data, many=False)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            output_datas.append(serializer.data)
        return Response(output_datas, status=status.HTTP_201_CREATED)


    def get_queryset(self):
        queryset = super(SellerInvoiceTrackNoModelViewSet, self).get_queryset()
        return queryset



class EInvoiceModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = EInvoice.objects.all().order_by('-id')
    serializer_class = EInvoiceSerializer
    filter_class = EInvoiceFilter
    renderer_classes = (EInvoiceHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )


    @action(detail=True, methods=['get'], renderer_classes=[JSONRenderer, ])
    def get_escpos_print_scripts(self, request, pk=None):
        ei = self.get_object()
        if ei:
            escpos_print_scripts = ei.escpos_print_scripts
            if request.GET.get('with_details_content', False) not in ['true', '1']:
                del escpos_print_scripts['details_content']
            if request.GET.get('re_print_original_copy', False) in ['true', '1']:
                escpos_print_scripts['re_print_original_copy'] = True
            return Response(escpos_print_scripts)
        else:
            return Response({"error_title": _("E-Invoice Error"),
                             "error_message": _("{} does not exist").format(pk),
                            }, status=status.HTTP_403_FORBIDDEN)



class EInvoicePrintLogModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = EInvoicePrintLog.objects.all().order_by('-id')
    serializer_class = EInvoicePrintLogSerializer
    filter_class = EInvoicePrintLogFilter
    renderer_classes = (EInvoicePrintLogHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('get', )



class CancelEInvoiceModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = CancelEInvoice.objects.all().order_by('-id')
    serializer_class = CancelEInvoiceSerializer
    renderer_classes = (CancelEInvoiceHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', )
    

    def create(self, request, *args, **kwargs):
        data = request.data
        einvoice_id = data['einvoice_id']
        try:
            einvoice = EInvoice.objects.get(id=einvoice_id)
        except EInvoice.DoesNotExist:
            er = {
                "error_title": "E-Invoice Error",
                "error_message": _("E-Invoice(id: {}) does not exist!").format(einvoice_id),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        else:
            if einvoice.canceleinvoice_set.exists():
                er = {
                    "error_title": "E-Invoice Error",
                    "error_message": _("E-Invoice({}) was already canceled!").format(einvoice.track_no_)
                }
                return Response(er, status=status.HTTP_403_FORBIDDEN)
        data['creator'] = request.user.id
        data['einvoice'] = einvoice.id
        data['seller_identifier'] = einvoice.seller_identifier
        data['buyer_identifier'] = einvoice.buyer_identifier
        data['generate_time'] = now()
        re_create_einvoice = data['re_create_einvoice']
        del data['re_create_einvoice']
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if re_create_einvoice:
            _d = {f.name: getattr(einvoice, f.name)
                for f in EInvoice._meta.fields
            }
            for seller_invoice_track_no in SellerInvoiceTrackNo.filter_now_use_sitns(
                                                    turnkey_web=einvoice.seller_invoice_track_no.turnkey_web,
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
            del _d['id']
            del _d['random_number']
            del _d['generate_time']
            _d['creator'] = request.user
            _d['print_mark'] = False
            new_einvoice = EInvoice(**_d)
            new_einvoice.save()
            serializer.instance.new_einvoice = new_einvoice
            serializer.instance.save()
        serializer = CancelEInvoiceSerializer(serializer.instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)