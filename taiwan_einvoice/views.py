import json
from django.http import Http404
from django.shortcuts import render
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from taiwan_einvoice.permissions import IsSuperUser
from taiwan_einvoice.renderers import (
    TEBrowsableAPIRenderer,
    ESCPOSWebHtmlRenderer,
    LegalEntityHtmlRenderer,
    EInvoiceHtmlRenderer,
    EInvoicePrintLogHtmlRenderer,
)
from taiwan_einvoice.models import (
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
    http_method_names = ('post', 'get', 'delete', 'patch')



class LegalEntityModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = LegalEntity.objects.all().order_by('-id')
    serializer_class = LegalEntitySerializer
    filter_class = LegalEntityFilter
    renderer_classes = (LegalEntityHtmlRenderer, JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class SellerModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = Seller.objects.all().order_by('-id')
    serializer_class = SellerSerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class TurnkeyWebModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = TurnkeyWeb.objects.all().order_by('-id')
    serializer_class = TurnkeyWebSerializer
    filter_class = TurnkeyWebFilter
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class SellerInvoiceTrackNoModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = SellerInvoiceTrackNo.objects.all().order_by('-id')
    serializer_class = SellerInvoiceTrackNoSerializer
    filter_class = SellerInvoiceTrackNoFilter
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')


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
            return Response({"error_message": ""},
                            status=status.HTTP_400_BAD_REQUEST)



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
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', )