import json, datetime
from django.http import Http404
from django.shortcuts import render
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from taiwan_einvoice.permissions import IsSuperUser
from taiwan_einvoice.renderers import (
    TEBrowsableAPIRenderer,
    ESCPOSWebHtmlRenderer,
    TurnkeyWebHtmlRenderer,
    LegalEntityHtmlRenderer,
    SellerInvoiceTrackNoHtmlRenderer,
    EInvoiceHtmlRenderer,
    EInvoicePrintLogHtmlRenderer,
    CancelEInvoiceHtmlRenderer,
)
from taiwan_einvoice.models import (
    TAIPEI_TIMEZONE,
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
    ESCPOSWebSerializer,
    LegalEntitySerializer,
    SellerSerializer,
    TurnkeyWebSerializer,
    SellerInvoiceTrackNoSerializer,
    EInvoiceSerializer,
    EInvoicePrintLogSerializer,
    CancelEInvoiceSerializer,
)
from taiwan_einvoice.filters import (
    ESCPOSWebFilter,
    LegalEntityFilter,
    TurnkeyWebFilter,
    SellerInvoiceTrackNoFilter,
    EInvoiceFilter,
    EInvoicePrintLogFilter,
)


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



class ESCPOSWebModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = ESCPOSWeb.objects.all().order_by('-id')
    serializer_class = ESCPOSWebSerializer
    filter_class = ESCPOSWebFilter
    renderer_classes = (ESCPOSWebHtmlRenderer, TEBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('post', 'get', )



class LegalEntityModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = LegalEntity.objects.all().order_by('-id')
    serializer_class = LegalEntitySerializer
    filter_class = LegalEntityFilter
    renderer_classes = (LegalEntityHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'patch')



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
                    end_time_0 = TAIPEI_TIMEZONE.localize(datetime.datetime(end_year, end_month, 1, 0, 0, 0)) + datetime.timedelta(days=35)
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
                    "type": cols[1],
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
        serializer = self.get_serializer(data=datas, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            er = {
                "error_title": "Valid Error",
                "error_message": """When a serializer is passed a `data` keyword argument you must call `.is_valid()` before attempting to access the serialized `.data` representation.
You should either call `.is_valid()` first, or access `.initial_data` instead.""",
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)


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