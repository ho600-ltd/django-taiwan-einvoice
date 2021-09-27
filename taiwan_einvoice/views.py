from django.http import Http404
from django.shortcuts import render
from rest_framework.renderers import JSONRenderer
from rest_framework.viewsets import ModelViewSet

from taiwan_einvoice.permissions import IsSuperUser
from taiwan_einvoice.renderers import TEBrowsableAPIRenderer
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


def index(request):
    escpos_webs = ESCPOSWeb.objects.all().order_by('id')
    return render(request, 'taiwan_einvoice/index.html', {
        'escpos_webs': escpos_webs
    })


def escpos_web(request, escpos_web_id):
    try:
        escpos_web = ESCPOSWeb.objects.get(id=escpos_web_id)
    except ESCPOSWeb.DoesNotExist:
        raise Http404("ESCPOS Web does not exist!")
    return render(request,
                  'taiwan_einvoice/escpos_web.html',
                  {"escpos_web": escpos_web})



class ESCPOSWebModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = ESCPOSWeb.objects.all().order_by('-id')
    serializer_class = ESCPOSWebSerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class LegalEntityModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = LegalEntity.objects.all().order_by('-id')
    serializer_class = LegalEntitySerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
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
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class SellerInvoiceTrackNoModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = SellerInvoiceTrackNo.objects.all().order_by('-id')
    serializer_class = SellerInvoiceTrackNoSerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class EInvoiceModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = EInvoice.objects.all().order_by('-id')
    serializer_class = EInvoiceSerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class EInvoicePrintLogModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = EInvoicePrintLog.objects.all().order_by('-id')
    serializer_class = EInvoicePrintLogSerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')



class CancelEInvoiceModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    queryset = CancelEInvoice.objects.all().order_by('-id')
    serializer_class = CancelEInvoiceSerializer
    renderer_classes = (JSONRenderer, TEBrowsableAPIRenderer, )
    http_method_names = ('post', 'get', 'delete', 'patch')